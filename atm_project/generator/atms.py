"""dim_atm: the 120-ATM network of MBank in Bishkek.

ATMs are placed so that the global archetype mix matches the configured shares,
while each ATM lands in a geographically plausible zone (markets get market
ATMs, microdistricts get residential/pension ATMs, etc.). Hardware attributes
(vendor, capabilities, capacity) and the latent baseline intensity are drawn
from per-archetype parameters.
"""

import numpy as np
import pandas as pd

from .geography import ZONES

# Per-archetype parameters. base_intensity is the latent daily baseline scale
# (expected withdrawals/day at neutral conditions); tuned with the intensity model.
TYPE_PARAMS = {
    "transport_market": dict(base_intensity=420, cap=(6_000_000, 8_000_000),
                             p_24_7=0.55, p_qr=0.45, p_fx=0.25, p_recycler=0.15,
                             placement="street"),
    "office_business":  dict(base_intensity=240, cap=(4_000_000, 6_000_000),
                             p_24_7=0.35, p_qr=0.70, p_fx=0.20, p_recycler=0.40,
                             placement="indoor_branch"),
    "residential":      dict(base_intensity=180, cap=(4_000_000, 6_000_000),
                             p_24_7=0.45, p_qr=0.50, p_fx=0.05, p_recycler=0.20,
                             placement="street"),
    "shopping_mall":    dict(base_intensity=300, cap=(6_000_000, 8_000_000),
                             p_24_7=0.50, p_qr=0.75, p_fx=0.30, p_recycler=0.55,
                             placement="mall"),
    "tourist_center":   dict(base_intensity=210, cap=(5_000_000, 7_000_000),
                             p_24_7=0.60, p_qr=0.65, p_fx=0.85, p_recycler=0.35,
                             placement="indoor_branch"),
    "pension_social":   dict(base_intensity=160, cap=(5_000_000, 7_000_000),
                             p_24_7=0.25, p_qr=0.25, p_fx=0.03, p_recycler=0.15,
                             placement="indoor_branch"),
    "highway_gas":      dict(base_intensity=150, cap=(4_000_000, 6_000_000),
                             p_24_7=0.85, p_qr=0.40, p_fx=0.10, p_recycler=0.10,
                             placement="gas_station"),
}

VENDORS = {
    "NCR": ["SelfServ 22", "SelfServ 26", "SelfServ 84"],
    "Wincor Nixdorf": ["ProCash 280", "ProCash 2100xe"],
    "Hyosung": ["MoniMax 5600", "MoniMax 8600"],
    "Diebold Nixdorf": ["Opteva 520", "DN Series 200"],
}

DENOM_SETS = [[500, 1000, 5000], [200, 500, 1000, 5000], [500, 1000, 2000, 5000]]


def _allocate_type_counts(shares: dict, n_atms: int,
                          rng: np.random.Generator) -> dict:
    """Split n_atms across archetypes proportionally to shares (sums exactly)."""
    types = list(shares)
    raw = np.array([shares[t] for t in types], dtype=float)
    raw = raw / raw.sum() * n_atms
    base = np.floor(raw).astype(int)
    remainder = n_atms - base.sum()
    # Distribute the rounding remainder to the largest fractional parts.
    frac_order = np.argsort(-(raw - base))
    for i in range(remainder):
        base[frac_order[i]] += 1
    return dict(zip(types, base))


def _zone_choices_for_type(atm_type: str):
    """Return (zone_indices, normalised weights) of zones plausible for a type."""
    idx, w = [], []
    for i, z in enumerate(ZONES):
        weight = z["type_affinity"].get(atm_type, 0)
        if weight > 0:
            idx.append(i)
            w.append(weight)
    w = np.array(w, dtype=float)
    return idx, w / w.sum()


def build_atms(config: dict, rng: np.random.Generator | None = None) -> pd.DataFrame:
    """Return the dim_atm reference table."""
    if rng is None:
        rng = np.random.default_rng(config["seed"])

    n_atms = config["network"]["n_atms"]
    counts = _allocate_type_counts(config["atm_types"], n_atms, rng)

    start_year = int(config["period"]["start"][:4])
    n_new = int(round(n_atms * config["network"]["installed_during_period_share"]))

    rows = []
    for atm_type, k in counts.items():
        params = TYPE_PARAMS[atm_type]
        zone_idx, zone_w = _zone_choices_for_type(atm_type)
        chosen = rng.choice(zone_idx, size=k, p=zone_w)
        for zi in chosen:
            z = ZONES[zi]
            vendor = rng.choice(list(VENDORS))
            model = rng.choice(VENDORS[vendor])
            rows.append(dict(
                atm_type=atm_type,
                district_id=z["district_id"],
                location_name=z["name"],
                lat=round(z["lat_center"] + rng.normal(0, 0.004), 6),
                lon=round(z["lon_center"] + rng.normal(0, 0.004), 6),
                placement=params["placement"],
                is_24_7=bool(rng.random() < params["p_24_7"]),
                vendor=vendor,
                model=model,
                firmware_version=f"v{rng.integers(2, 6)}.{rng.integers(0, 9)}",
                supports_nfc=bool(rng.random() < 0.8),
                supports_qr=bool(rng.random() < params["p_qr"]),
                is_recycler=bool(rng.random() < params["p_recycler"]),
                supports_fx=bool(rng.random() < params["p_fx"]),
                num_cassettes=int(rng.integers(3, 5)),
                denominations=DENOM_SETS[rng.integers(0, len(DENOM_SETS))],
                cash_capacity=int(rng.integers(params["cap"][0], params["cap"][1])),
                txn_limit=int(rng.choice([20000, 25000])),
                daily_limit=int(rng.choice([60000, 100000, 150000])),
                base_intensity=round(
                    params["base_intensity"] * rng.lognormal(0, 0.25), 1),
            ))

    df = pd.DataFrame(rows)
    # Shuffle so atm_id ordering is not grouped by type, then assign stable ids.
    df = df.sample(frac=1.0, random_state=int(rng.integers(0, 2**31))).reset_index(drop=True)
    df.insert(0, "atm_id", [f"ATM-{i+1:04d}" for i in range(len(df))])
    df.insert(1, "terminal_id", [f"T{rng.integers(10**7, 10**8)}" for _ in range(len(df))])

    # Install / service dates. Most ATMs predate the period; n_new commissioned
    # during it, biased towards the start of year 2.
    start_dt = pd.Timestamp(config["period"]["start"])
    end_dt = pd.Timestamp(config["period"]["end"])
    install_dates = []
    new_idx = set(rng.choice(len(df), size=n_new, replace=False).tolist())
    for i in range(len(df)):
        if i in new_idx:
            # Commission during the period, mostly early in year 2.
            offset = int(abs(rng.normal(loc=380, scale=120)))
            d = start_dt + pd.Timedelta(days=min(offset, (end_dt - start_dt).days - 5))
        else:
            # Pre-existing: installed in 2022-2023.
            d = pd.Timestamp(f"{start_year - rng.integers(1, 3)}-01-01") + \
                pd.Timedelta(days=int(rng.integers(0, 365)))
        install_dates.append(d.normalize())
    df["install_date"] = install_dates
    df["last_service_date"] = [
        (end_dt - pd.Timedelta(days=int(rng.integers(1, 120)))).normalize()
        for _ in range(len(df))
    ]
    df["service_route_id"] = "RT-" + df["district_id"].str.slice(3, 6)

    column_order = [
        "atm_id", "terminal_id", "district_id", "location_name", "lat", "lon",
        "atm_type", "placement", "is_24_7", "vendor", "model", "firmware_version",
        "supports_nfc", "supports_qr", "is_recycler", "supports_fx",
        "num_cassettes", "denominations", "cash_capacity", "txn_limit",
        "daily_limit", "service_route_id", "install_date", "last_service_date",
        "base_intensity",
    ]
    return df[column_order]
