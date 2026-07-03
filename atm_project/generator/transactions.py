"""fact_transactions: per-second withdrawal events (TZ §4, §5).

Pipeline (all vectorised, batched by calendar month to bound memory):

    λ(a,d,h)  →  N ~ NegBinomial  →  per-second expansion  →  customer &
    amount & processing fields  →  Parquet partitions year=YYYY/month=MM/

Design choices / simplifications (documented for the tuning stage, §11.7):
  - Customer assignment uses a gravity pool per ATM (Huff model, §4.1): each ATM
    draws a fixed-size pool of on-us cards weighted by zone distance × demographic
    affinity; transactions sample from that pool → repeat customers, fat-tail RFM.
  - Off-us share (other banks / tourists) synthesised on the fly, no customer_id.
  - Amount ~ LogNormal by income band × ATM type, rounded to cash denominations,
    clipped to txn_limit; per-card daily limit is approximated by the txn_limit
    clip only (exact daily aggregation deferred to tuning).
  - device_cash_level_after and response_code '99' (out-of-cash) are filled by
    cash_ops.py (Step 4), which owns the running cash balance. Here the cash
    column is left as -1 and '99' is not emitted.
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from . import PROJECT_ROOT
from .geography import ZONES
from .intensity import compute_hourly_intensity, DISPERSION_DEFAULT

log = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Behavioural constants (§4.3, §5). High-level shapes; tuned in §11.7.
# --------------------------------------------------------------------------- #

# Off-us share of transactions by ATM archetype (tourists/other banks).
OFF_US_SHARE = {
    "tourist_center": 0.45, "transport_market": 0.30, "shopping_mall": 0.25,
    "office_business": 0.18, "highway_gas": 0.20, "residential": 0.10,
    "pension_social": 0.06,
}

# Transaction type mix (withdrawal/fast_cash dominate, §4.3).
TXN_TYPES = ["withdrawal", "fast_cash", "balance_inquiry", "mini_statement",
             "transfer", "deposit"]
TXN_TYPE_P = [0.70, 0.12, 0.09, 0.04, 0.04, 0.01]

# LogNormal amount parameters by income band (KGS); mu is log-scale.
AMOUNT_MU = {"low": 7.6, "mid": 8.2, "high": 8.7}     # ≈ 2k / 3.6k / 6k KGS
AMOUNT_SIGMA = 0.55
YEAR2_INFLATION = 0.08                                # §4.2

# Off-us card scheme mix (tourists lean Visa/MC/UnionPay).
OFFUS_SCHEMES = ["Visa", "Mastercard", "UnionPay", "Mir", "Elcart"]
OFFUS_SCHEME_P = [0.38, 0.30, 0.16, 0.10, 0.06]
OFFUS_BIN = {"Visa": "411111", "Mastercard": "522222", "UnionPay": "620000",
             "Mir": "220220", "Elcart": "990099"}

# response_code distribution for approved-eligible cash transactions (§5.4).
# '99' (out-of-cash) is intentionally absent — added by cash_ops.py (Step 4).
RESPONSE_CODES = ["00", "51", "55", "91", "92", "94"]
RESPONSE_P     = [0.935, 0.028, 0.020, 0.008, 0.006, 0.003]

POOL_SIZE = 7000          # on-us cards in each ATM's catchment pool (~67% base reached over 2y)
GRAVITY_BETA = 1.8        # distance decay exponent (Huff)

# Demographic affinity: weight of an income_source for an ATM archetype (§4.1).
DEMO_AFFINITY = {
    "transport_market": {"business": 3, "salary": 2, "remittance": 2, "student": 1, "social": 1, "pension": 1},
    "office_business":  {"salary": 3, "business": 3, "remittance": 1, "student": 1, "social": 1, "pension": 1},
    "residential":      {"salary": 2, "pension": 2, "social": 2, "remittance": 2, "business": 1, "student": 1},
    "shopping_mall":    {"business": 3, "salary": 2, "student": 2, "remittance": 1, "social": 1, "pension": 1},
    "tourist_center":   {"business": 2, "salary": 2, "student": 1, "remittance": 1, "social": 1, "pension": 1},
    "pension_social":   {"pension": 4, "social": 3, "salary": 1, "remittance": 1, "business": 1, "student": 1},
    "highway_gas":      {"business": 2, "salary": 2, "remittance": 1, "student": 1, "social": 1, "pension": 1},
}


# --------------------------------------------------------------------------- #
# Customer catchment pools (§4.1 gravity/Huff model)
# --------------------------------------------------------------------------- #

def _zone_distance_matrix() -> tuple[dict, np.ndarray]:
    """Euclidean (deg) distance between zone centres; small-area proxy for km."""
    ids = [z["district_id"] for z in ZONES]
    lat = np.array([z["lat_center"] for z in ZONES])
    lon = np.array([z["lon_center"] for z in ZONES])
    d = np.sqrt((lat[:, None] - lat[None, :]) ** 2 + (lon[:, None] - lon[None, :]) ** 2)
    return {zid: i for i, zid in enumerate(ids)}, d


def _build_customer_pools(atms, customers, cards, rng) -> list[np.ndarray]:
    """For each ATM, sample a pool of on-us card row-indices by gravity × affinity.

    Groups cards by (home_zone, income_source); allocates POOL_SIZE across groups
    proportional to their weight for the ATM, then samples uniformly within each
    group. Result: pool[a] is an int array of card indices into `cards`.
    """
    zone_idx, dist = _zone_distance_matrix()
    # Card -> customer attributes.
    cust = customers.set_index("customer_id")
    card_cust = cards["customer_id"].to_numpy()
    home = cust.loc[card_cust, "home_district_id"].to_numpy()
    income = cust.loc[card_cust, "income_source"].to_numpy()

    # Group cards by (home_zone, income_source).
    zone_ids = list(zone_idx)
    incomes = ["salary", "pension", "social", "business", "remittance", "student"]
    group_cards: dict[tuple, np.ndarray] = {}
    for zid in zone_ids:
        for inc in incomes:
            m = (home == zid) & (income == inc)
            if m.any():
                group_cards[(zid, inc)] = np.where(m)[0]

    pools = []
    for _, atm in atms.iterrows():
        a_zone = atm["district_id"]
        a_type = atm["atm_type"]
        ai = zone_idx[a_zone]
        # Weight per group = gravity(zone) × demographic affinity.
        keys, weights = [], []
        for (zid, inc), idxs in group_cards.items():
            grav = 1.0 / (dist[ai, zone_idx[zid]] + 0.01) ** GRAVITY_BETA
            aff = DEMO_AFFINITY[a_type].get(inc, 1)
            keys.append((zid, inc))
            weights.append(grav * aff * len(idxs))
        w = np.array(weights)
        w /= w.sum()
        # Multinomial allocation of pool slots across groups.
        alloc = rng.multinomial(POOL_SIZE, w)
        parts = [rng.choice(group_cards[k], size=n, replace=True)
                 for k, n in zip(keys, alloc) if n > 0]
        pools.append(np.concatenate(parts))
    return pools


# --------------------------------------------------------------------------- #
# Per-month expansion
# --------------------------------------------------------------------------- #

def _expand_counts(lam_month: np.ndarray, r: float, rng) -> tuple:
    """NegBinomial counts per (atm,day,hour) → flat repeated index arrays."""
    p = r / (r + lam_month)
    counts = rng.negative_binomial(r, p)                 # (n_atms, D, 24)
    n_atms, D, _ = counts.shape
    flat = counts.reshape(-1)
    cell = np.repeat(np.arange(flat.size), flat)         # cell index per txn
    atm_i = cell // (D * 24)
    rem = cell % (D * 24)
    day_i = rem // 24
    hour = rem % 24
    return atm_i.astype(np.int32), day_i.astype(np.int32), hour.astype(np.int8)


def _round_to_cash(amount: np.ndarray) -> np.ndarray:
    """Round withdrawal amounts to 'round' cash values (nearest 500 KGS, min 500)."""
    r = np.round(amount / 500.0) * 500
    return np.clip(r, 500, None).astype(np.int64)


def _build_month(month_key, atms, calendar, cards, pools, lam, config, rng,
                 txn_id_start) -> pd.DataFrame:
    """Assemble the fact_transactions frame for one calendar month."""
    cal = calendar.reset_index(drop=True)
    day_mask = (pd.to_datetime(cal["date"]).dt.to_period("M").astype(str)
                == month_key).to_numpy()
    day_pos = np.where(day_mask)[0]
    lam_month = lam[:, day_pos, :]

    r = config["intensity"]["nb_dispersion"]
    atm_i, day_local, hour = _expand_counts(lam_month, r, rng)
    n = atm_i.size
    if n == 0:
        return pd.DataFrame()

    day_global = day_pos[day_local]
    dates = pd.to_datetime(cal["date"].to_numpy()[day_global])
    year_index = cal["year_index"].to_numpy()[day_global]

    # timestamp to the second: uniform jitter within the hour (§5).
    sec = rng.integers(0, 3600, size=n)
    ts = dates.values + (hour.astype("timedelta64[s]") * 3600
                         + sec.astype("timedelta64[s]"))
    ts = pd.to_datetime(ts)

    atm_ids = atms["atm_id"].to_numpy()[atm_i]
    terminal = atms["terminal_id"].to_numpy()[atm_i]
    district = atms["district_id"].to_numpy()[atm_i]
    atm_types = atms["atm_type"].to_numpy()[atm_i]
    txn_limit = atms["txn_limit"].to_numpy()[atm_i]

    # --- on-us vs off-us ---------------------------------------------------- #
    off_share = np.array([OFF_US_SHARE[t] for t in atm_types])
    is_off = rng.random(n) < off_share
    is_on = ~is_off

    card_id = np.empty(n, dtype=object)
    customer_id = np.empty(n, dtype=object)
    scheme = np.empty(n, dtype=object)
    card_bin = np.empty(n, dtype=object)
    income_band = np.full(n, "mid", dtype=object)

    # on-us: sample a card from the ATM's pool (repeat customers).
    cust_by_card = cards["customer_id"].to_numpy()
    scheme_by_card = cards["scheme"].to_numpy()
    bin_by_card = cards["bin"].to_numpy()
    # customer income band via join (once).
    cust = config["_customers_index"]
    band_by_card = cust.loc[cust_by_card, "income_band"].to_numpy()

    for a in np.unique(atm_i[is_on]):
        sel = is_on & (atm_i == a)
        m = int(sel.sum())
        pick = pools[a][rng.integers(0, len(pools[a]), size=m)]
        card_id[sel] = cards["card_id"].to_numpy()[pick]
        customer_id[sel] = cust_by_card[pick]
        scheme[sel] = scheme_by_card[pick]
        card_bin[sel] = bin_by_card[pick]
        income_band[sel] = band_by_card[pick]

    # off-us: synthetic card, no customer.
    n_off = int(is_off.sum())
    if n_off:
        osc = rng.choice(OFFUS_SCHEMES, size=n_off, p=OFFUS_SCHEME_P)
        scheme[is_off] = osc
        card_bin[is_off] = np.array([OFFUS_BIN[s] for s in osc], dtype=object)
        card_id[is_off] = np.array([f"OFFUS-{i:08d}"
                                    for i in rng.integers(0, 10**8, size=n_off)], dtype=object)
        customer_id[is_off] = None
        income_band[is_off] = rng.choice(["low", "mid", "high"], size=n_off, p=[0.3, 0.5, 0.2])

    # --- transaction type & entry mode ------------------------------------- #
    txn_type = rng.choice(TXN_TYPES, size=n, p=TXN_TYPE_P)
    supports_nfc = atms["supports_nfc"].to_numpy()[atm_i]
    supports_qr = atms["supports_qr"].to_numpy()[atm_i]
    entry_mode = _entry_modes(year_index, supports_nfc, supports_qr, rng)

    # --- amounts ------------------------------------------------------------ #
    mu = np.array([AMOUNT_MU[b] for b in income_band])
    mu = mu + np.log1p(YEAR2_INFLATION) * (year_index == 1)
    raw = rng.lognormal(mean=mu, sigma=AMOUNT_SIGMA)
    requested = _round_to_cash(raw)
    requested = np.minimum(requested, txn_limit)
    is_cash = np.isin(txn_type, ["withdrawal", "fast_cash", "deposit"])
    requested = np.where(is_cash, requested, 0)

    # --- response codes & approval ----------------------------------------- #
    rc = rng.choice(RESPONSE_CODES, size=n, p=RESPONSE_P)
    is_approved = rc == "00"
    dispensed = np.where(is_approved & is_cash, requested, 0)
    auth_code = np.where(is_approved,
                         [f"{c:06d}" for c in rng.integers(0, 10**6, size=n)], "")

    # --- fees & fx ---------------------------------------------------------- #
    fee = np.where(is_off, rng.integers(100, 201, size=n), 0)
    fx_rate = np.ones(n)
    currency = np.full(n, "KGS", dtype=object)

    # --- processing telemetry (§5) ----------------------------------------- #
    rrn = np.array([f"{v:012d}" for v in rng.integers(0, 10**12, size=n)], dtype=object)
    stan = rng.integers(1, 10**6, size=n)
    pin_attempts = np.where(rc == "55", rng.integers(2, 4, size=n),
                            rng.integers(1, 2, size=n)).astype(np.int8)
    session = rng.integers(15, 90, size=n).astype(np.int32)
    latency = rng.integers(120, 1500, size=n).astype(np.int32)

    is_remit = (np.isin(income_band, ["low", "mid"]) & is_on
                & (rng.random(n) < 0.08) & is_cash)

    df = pd.DataFrame({
        "txn_id": np.arange(txn_id_start, txn_id_start + n, dtype=np.int64),
        "rrn": rrn,
        "stan": stan.astype(np.int32),
        "timestamp": ts,
        "local_time": ts.time,
        "atm_id": atm_ids,
        "terminal_id": terminal,
        "district_id": district,
        "card_id": card_id,
        "customer_id": customer_id,
        "card_scheme": scheme,
        "card_bin": card_bin,
        "is_on_us": is_on,
        "mcc": np.int32(6011),
        "txn_type": txn_type,
        "entry_mode": entry_mode,
        "requested_amount": requested.astype(np.int64),
        "dispensed_amount": dispensed.astype(np.int64),
        "currency": currency,
        "fee_amount": fee.astype(np.int32),
        "fx_rate": fx_rate,
        "response_code": rc,
        "is_approved": is_approved,
        "auth_code": auth_code,
        "pin_attempts": pin_attempts,
        "session_duration_s": session,
        "network_latency_ms": latency,
        "is_remittance_cashout": is_remit,
        "balance_after": np.int64(-1),
        "device_cash_level_after": np.int64(-1),   # filled by cash_ops.py (Step 4)
        "date": dates.normalize(),
        "hour": hour,
    })
    # Chronological order within the month.
    return df.sort_values("timestamp", kind="stable").reset_index(drop=True)


def _entry_modes(year_index, supports_nfc, supports_qr, rng) -> np.ndarray:
    """chip dominant in y1; contactless/qr grow in y2 where hardware allows (§4.3)."""
    n = len(year_index)
    out = np.full(n, "chip", dtype=object)
    u = rng.random(n)
    # Base contactless share; higher in year 2 and only where NFC is supported.
    cl_share = np.where(year_index == 1, 0.35, 0.18) * supports_nfc
    qr_share = np.where(year_index == 1, 0.12, 0.05) * supports_qr
    out[u < qr_share] = "qr"
    out[(u >= qr_share) & (u < qr_share + cl_share)] = "contactless"
    # A little magstripe/fallback noise.
    tail = u > 0.97
    out[tail] = rng.choice(["magstripe", "fallback"], size=int(tail.sum()))
    return out


# --------------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------------- #

def build_transactions(config, tables, rng=None, months=None) -> dict:
    """Generate fact_transactions, writing Parquet partitions by year/month.

    `months` optionally restricts to a list of 'YYYY-MM' strings (for smoke tests).
    Returns a summary dict {month: n_rows}.
    """
    if rng is None:
        rng = np.random.default_rng(config["seed"])

    atms = tables["dim_atm"].reset_index(drop=True)
    calendar = tables["dim_calendar"].reset_index(drop=True)
    customers = tables["dim_customer"]
    cards = tables["dim_card"].reset_index(drop=True)

    # Cache a customer index for income-band lookups inside the month loop.
    config = {**config, "_customers_index": customers.set_index("customer_id")}

    log.info("Transactions: computing intensity …")
    lam = compute_hourly_intensity(atms, calendar, config, rng)

    log.info("Transactions: building %d ATM catchment pools …", len(atms))
    pools = _build_customer_pools(atms, customers, cards, rng)

    all_months = (pd.to_datetime(calendar["date"]).dt.to_period("M")
                  .astype(str).unique().tolist())
    if months is not None:
        all_months = [m for m in all_months if m in months]

    out_root = PROJECT_ROOT / config["output"]["data_dir"] / "fact_transactions"
    summary, txn_id = {}, 1
    for mk in all_months:
        df = _build_month(mk, atms, calendar, cards, pools, lam, config, rng, txn_id)
        if df.empty:
            continue
        year, month = mk.split("-")
        part = out_root / f"year={year}" / f"month={month}"
        part.mkdir(parents=True, exist_ok=True)
        df.to_parquet(part / "part.parquet", index=False)
        summary[mk] = len(df)
        txn_id += len(df)
        log.info("  %s → %s rows", mk, f"{len(df):,}")
    return summary


def _smoke() -> None:
    from . import load_config
    from .build_dims import build_all_dims

    config = load_config()
    tables = build_all_dims(config)
    rng = np.random.default_rng(config["seed"])
    # One month only, to keep the smoke test fast.
    summary = build_transactions(config, tables, rng, months=["2024-03"])
    total = sum(summary.values())
    print("\n=== transactions smoke (2024-03) ===")
    print(f"rows: {total:,}")

    part = (PROJECT_ROOT / config["output"]["data_dir"]
            / "fact_transactions" / "year=2024" / "month=03" / "part.parquet")
    df = pd.read_parquet(part)
    print(f"columns ({df.shape[1]}): {list(df.columns)}")
    print(f"approval rate: {df['is_approved'].mean():.3f}")
    print(f"on-us share: {df['is_on_us'].mean():.3f}")
    print("response_code mix:")
    print(df["response_code"].value_counts(normalize=True).round(3).to_string())
    print("entry_mode mix:")
    print(df["entry_mode"].value_counts(normalize=True).round(3).to_string())
    print(f"mean dispensed (cash txns): "
          f"{df.loc[df['dispensed_amount'] > 0, 'dispensed_amount'].mean():,.0f} KGS")
    print(f"repeat customers: {df['customer_id'].notna().sum():,} on-us rows, "
          f"{df['customer_id'].nunique()} unique customers")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    _smoke()
