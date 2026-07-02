"""dim_customer and dim_card: the on-us customer/card base of MBank.

These tables give repeat customers (a bounded card pool), demographics and the
income-source structure that later couples withdrawals to pay/pension cycles.
Off-us cards (other banks, tourists) are NOT here; they are synthesised at
transaction time. Everything is generated vectorised with numpy.
"""

import numpy as np
import pandas as pd

from .geography import ZONES

AGE_BANDS = ["18-25", "26-35", "36-50", "51-65", "65+"]
AGE_PROBS = [0.18, 0.28, 0.28, 0.16, 0.10]

# P(income_source | age_band), columns ordered as INCOME_SOURCES.
INCOME_SOURCES = ["salary", "pension", "social", "business", "remittance", "student"]
INCOME_BY_AGE = {
    "18-25": [0.40, 0.00, 0.05, 0.05, 0.15, 0.35],
    "26-35": [0.50, 0.00, 0.08, 0.17, 0.25, 0.00],
    "36-50": [0.50, 0.00, 0.10, 0.20, 0.20, 0.00],
    "51-65": [0.45, 0.10, 0.10, 0.20, 0.15, 0.00],
    "65+":   [0.00, 0.85, 0.10, 0.05, 0.00, 0.00],
}

CHANNELS = ["atm", "mobile", "branch"]
CHANNEL_BY_AGE = {
    "18-25": [0.35, 0.60, 0.05],
    "26-35": [0.40, 0.55, 0.05],
    "36-50": [0.50, 0.40, 0.10],
    "51-65": [0.55, 0.25, 0.20],
    "65+":   [0.50, 0.10, 0.40],
}

CARD_SCHEMES = ["Elcart", "Visa", "Mastercard", "UnionPay", "Mir"]
SCHEME_PROBS = [0.55, 0.25, 0.15, 0.03, 0.02]
SCHEME_BIN = {  # representative issuing BIN prefixes
    "Elcart": "990001", "Visa": "405871", "Mastercard": "555912",
    "UnionPay": "625812", "Mir": "220012",
}

# Mapping income_source -> base debit product.
PRODUCT_BY_SOURCE = {
    "salary": "debit_salary", "pension": "debit_pension", "social": "debit_social",
    "business": "debit_classic", "remittance": "debit_classic", "student": "debit_classic",
}


def _sample_by_group(group_values, prob_table, choices, rng):
    """Vectorised categorical sampling where probabilities depend on a group key."""
    out = np.empty(len(group_values), dtype=object)
    for key, probs in prob_table.items():
        mask = group_values == key
        m = int(mask.sum())
        if m:
            out[mask] = rng.choice(choices, size=m, p=probs)
    return out


def build_customers(config: dict, rng: np.random.Generator | None = None) -> pd.DataFrame:
    """Return the dim_customer reference table."""
    if rng is None:
        rng = np.random.default_rng(config["seed"])

    n = config["customers"]["n_customers"]
    cust_id = np.array([f"CUST-{i+1:07d}" for i in range(n)], dtype=object)

    # Home district weighted by zone population.
    zone_ids = np.array([z["district_id"] for z in ZONES], dtype=object)
    zone_w = np.array([z["pop_weight"] for z in ZONES], dtype=float)
    zone_w /= zone_w.sum()
    home = rng.choice(zone_ids, size=n, p=zone_w)

    age = rng.choice(AGE_BANDS, size=n, p=AGE_PROBS)
    gender = rng.choice(["M", "F"], size=n)
    income_source = _sample_by_group(age, INCOME_BY_AGE, INCOME_SOURCES, rng)
    pref_channel = _sample_by_group(age, CHANNEL_BY_AGE, CHANNELS, rng)

    # Income band, skewed by income source.
    band = np.full(n, "mid", dtype=object)
    r = rng.random(n)
    high_src = np.isin(income_source, ["business", "salary"])
    low_src = np.isin(income_source, ["pension", "social", "student"])
    band[high_src & (r < 0.22)] = "high"
    band[low_src & (r < 0.55)] = "low"
    band[~high_src & ~low_src & (r < 0.30)] = "low"

    # Segment.
    segment = np.full(n, "mass", dtype=object)
    segment[income_source == "salary"] = "payroll"
    segment[income_source == "pension"] = "pensioner"
    segment[band == "high"] = "affluent"

    # Migrant-family flag: remittance receivers plus a base rate.
    is_migrant = (income_source == "remittance") | (rng.random(n) < 0.12)

    # Customer tenure: skewed recent for younger customers.
    start_year = int(config["period"]["start"][:4])
    base_year = np.where(np.isin(age, ["18-25", "26-35"]), start_year - 4, start_year - 8)
    since_offset = rng.integers(0, 365 * 4, size=n)
    customer_since = (pd.to_datetime(base_year.astype(str) + "-01-01")
                      + pd.to_timedelta(since_offset, unit="D")).normalize()

    return pd.DataFrame({
        "customer_id": cust_id,
        "home_district_id": home,
        "age_band": age,
        "gender": gender,
        "income_source": income_source,
        "income_band": band,
        "segment": segment,
        "is_migrant_family": is_migrant,
        "customer_since": customer_since,
        "preferred_channel": pref_channel,
    })


def build_cards(config: dict, customers: pd.DataFrame,
                rng: np.random.Generator | None = None) -> pd.DataFrame:
    """Return the dim_card reference table (on-us MBank cards)."""
    if rng is None:
        rng = np.random.default_rng(config["seed"])

    n_cust = len(customers)
    n_cards = config["customers"]["n_cards"]
    multi_share = config["customers"]["multi_card_share"]

    # Every customer gets one base card; extra cards go to a multi-card subset.
    # Extras are dealt round-robin over the eligible subset, so a customer holds
    # at most ceil(n_extra / |eligible|) + 1 cards (typically 2-3, never many).
    owners = np.arange(n_cust)
    n_extra = max(0, n_cards - n_cust)
    eligible = rng.permutation(rng.choice(n_cust, size=int(n_cust * multi_share),
                                          replace=False))
    reps = int(np.ceil(n_extra / len(eligible)))
    extra_owners = np.tile(eligible, reps)[:n_extra]
    owner_idx = np.concatenate([owners, extra_owners])

    n = len(owner_idx)
    card_id = np.array([f"CARD-{i+1:08d}" for i in range(n)], dtype=object)
    cust_id = customers["customer_id"].to_numpy()[owner_idx]
    src = customers["income_source"].to_numpy()[owner_idx]
    band = customers["income_band"].to_numpy()[owner_idx]

    scheme = rng.choice(CARD_SCHEMES, size=n, p=SCHEME_PROBS)
    bin6 = np.array([SCHEME_BIN[s] for s in scheme], dtype=object)

    # Product from income source, with some credit/virtual sprinkled in.
    product = np.array([PRODUCT_BY_SOURCE[s] for s in src], dtype=object)
    r = rng.random(n)
    product[(band == "high") & (r < 0.25)] = "credit"
    product[(src == "student") & (r > 0.7)] = "virtual"

    start_year = int(config["period"]["start"][:4])
    issue_offset = rng.integers(0, 365 * 5, size=n)
    issue_date = (pd.to_datetime(f"{start_year - 5}-01-01")
                  + pd.to_timedelta(issue_offset, unit="D")).normalize()
    expiry = (issue_date + pd.to_timedelta(rng.integers(3, 6, size=n) * 365, unit="D")).normalize()

    return pd.DataFrame({
        "card_id": card_id,
        "customer_id": cust_id,
        "scheme": scheme,
        "bin": bin6,
        "product": product,
        "is_on_us": True,
        "issuer_bank": "MBank",
        "issue_date": issue_date,
        "expiry": expiry,
        "is_active": rng.random(n) < 0.93,
        "contactless_enabled": rng.random(n) < 0.85,
    })
