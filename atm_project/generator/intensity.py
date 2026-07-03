"""Intensity model: expected withdrawals λ(a, d, h) per ATM, day and hour.

This is the heart of the generative model (TZ §3). For every ATM ``a``, day ``d``
and hour ``h`` we build a mean intensity as a product of dimensionless factors,
each ≈1 in neutral conditions:

    λ(a,d,h) = λ0(a) · H[type,h] · D[type,dow] · Pay · Pension · Holiday
             · Ramadan · Season · Trend · Weather · FX · ε(a,d)

``λ0(a)`` is ``dim_atm.base_intensity`` — the expected *daily* withdrawals in
neutral conditions. ``H`` is the intra-day shape (normalised so the hours sum to
24, i.e. average hour = 1); dividing by 24 turns it into per-hour shares that
integrate to the daily volume. The output is a dense ``(n_atms, n_days, 24)``
array of means, consumed by ``transactions.py`` as NegBinomial expectations.

Everything is vectorised (no per-transaction Python loops, TZ §8). Hourly/weekly
shapes and boost coefficients live here as module constants; only high-level
knobs (noise, trend, dispersion) come from ``config['intensity']``.
"""

import logging

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

HOURS = np.arange(24)

# NegBinomial dispersion is fairly type-independent; a single knob in config
# scales it. Exposed here for transactions.py (Step 3).
DISPERSION_DEFAULT = 8.0


# --------------------------------------------------------------------------- #
# §3.3  Intra-day profiles H[type, h] — 24 values, normalised so they sum to 24
# --------------------------------------------------------------------------- #

def _bumps(centres, widths, weights, floor=0.05) -> np.ndarray:
    """Sum of Gaussian bumps over 24 hours plus a flat floor; sum-normalised to 24."""
    curve = np.full(24, float(floor))
    for c, w, a in zip(centres, widths, weights):
        curve += a * np.exp(-0.5 * ((HOURS - c) / w) ** 2)
    return curve / curve.sum() * 24.0


HOURLY_PROFILES = {
    # Two humps: morning (markets open early) and late afternoon; daytime floor.
    "transport_market": _bumps([9.5, 17.0], [1.8, 1.6], [1.0, 0.9], floor=0.20),
    # Commute peaks 09-10 and 18, a lunch bump at 13; near-zero at night.
    "office_business":  _bumps([9.5, 13.0, 18.0], [1.1, 1.2, 1.2], [1.0, 0.5, 0.9], floor=0.03),
    # Residential districts: daytime + evening humps, evening-dominant. Kept
    # deliberately close to pension_social so the two overlap under clustering
    # (§9.10 / design §4) while still differing in peak hour (§9.2).
    "residential":      _bumps([11.5, 18.8], [2.5, 2.5], [0.85, 1.0], floor=0.12),
    # Opens around noon, plateau 14-21 peaking towards evening.
    "shopping_mall":    _bumps([15.0, 19.5], [3.0, 2.2], [0.7, 1.0], floor=0.05),
    # Broad flat plateau 11-19.
    "tourist_center":   _bumps([15.0], [4.5], [1.0], floor=0.20),
    # Pension/social: daytime-dominant but shares residential's evening tail.
    "pension_social":   _bumps([11.5, 18.5], [2.5, 2.5], [1.0, 0.85], floor=0.12),
    # Nearly flat 08-20, weak peaks, non-zero at night (24/7 highway).
    "highway_gas":      _bumps([9.0, 18.0], [4.0, 4.0], [0.4, 0.5], floor=0.45),
}


# --------------------------------------------------------------------------- #
# §3.4  Weekly coefficients D[type, dow] — 7 values (Mon..Sun), mean = 1
# --------------------------------------------------------------------------- #

def _weekly(mon_fri, sat, sun) -> np.ndarray:
    """Build a 7-vector from weekday/Sat/Sun levels, normalised to mean 1."""
    v = np.array([mon_fri] * 5 + [sat, sun], dtype=float)
    return v / v.mean()


WEEKLY_COEF = {
    "office_business":  _weekly(1.0, 0.25, 0.20),   # weekdays ≫ weekend
    "shopping_mall":    _weekly(0.85, 1.35, 1.30),  # weekend > weekday
    "residential":      _weekly(0.97, 1.08, 1.08),  # weekend > weekday (soft)
    "transport_market": _weekly(1.0, 1.0, 0.95),    # market never sleeps
    "pension_social":   _weekly(1.03, 0.94, 0.90),  # date-driven; weak dow (§3.4)
    "highway_gas":      _weekly(1.0, 1.05, 1.05),   # weak modulation
    "tourist_center":   _weekly(0.95, 1.15, 1.10),  # weak modulation
}


# --------------------------------------------------------------------------- #
# §3.5  Calendar boosts (per ATM-day multipliers)
# --------------------------------------------------------------------------- #

# Payday multiplier by type (applied on is_payday windows 10-14 and 25-27).
PAY_MULT = {
    "office_business": 2.2, "residential": 1.3, "shopping_mall": 1.25,
    "transport_market": 1.15, "tourist_center": 1.05, "highway_gas": 1.05,
    "pension_social": 1.05,
}
# Pension multiplier by type (applied on is_pension_day, days 10-14).
PENSION_MULT = {
    "pension_social": 3.0, "residential": 1.2, "transport_market": 1.1,
    "shopping_mall": 1.05, "office_business": 1.0, "tourist_center": 1.0,
    "highway_gas": 1.0,
}
# Pre-holiday shopping spike by type; strongest for mall/market.
PRE_HOLIDAY_MULT = {
    "shopping_mall": 2.4, "transport_market": 2.2, "residential": 1.7,
    "tourist_center": 1.5, "highway_gas": 1.4, "office_business": 1.5,
    "pension_social": 1.5,
}
# On the holiday itself: offices dead, malls/markets still active.
HOLIDAY_MULT = {
    "office_business": 0.15, "pension_social": 0.5, "transport_market": 1.1,
    "shopping_mall": 1.1, "residential": 0.9, "tourist_center": 1.05,
    "highway_gas": 1.0,
}


def _pay_factor(types, cal) -> np.ndarray:
    """(n_atms, n_days) payday boost; ramps down across the pay window."""
    is_pay = cal["is_payday"].to_numpy()
    # Taper: first day of a window gets the full boost, later days decay.
    day = pd.to_datetime(cal["date"]).dt.day.to_numpy()
    window_pos = np.where(day <= 14, day - 10, day - 25)          # 0.. within window
    taper = np.clip(1.0 - 0.12 * np.clip(window_pos, 0, None), 0.6, 1.0)
    per_type = np.array([PAY_MULT[t] for t in types])[:, None]
    boost = 1.0 + (per_type - 1.0) * taper[None, :]
    return np.where(is_pay[None, :], boost, 1.0)


def _pension_factor(types, cal) -> np.ndarray:
    is_pen = cal["is_pension_day"].to_numpy()
    per_type = np.array([PENSION_MULT[t] for t in types])[:, None]
    return np.where(is_pen[None, :], per_type, 1.0)


def _holiday_factor(types, cal) -> np.ndarray:
    is_pre = cal["is_pre_holiday"].to_numpy()
    is_hol = cal["is_holiday"].to_numpy()
    pre = np.array([PRE_HOLIDAY_MULT[t] for t in types])[:, None]
    hol = np.array([HOLIDAY_MULT[t] for t in types])[:, None]
    out = np.ones((len(types), len(cal)))
    out = np.where(is_pre[None, :], pre, out)
    out = np.where(is_hol[None, :], hol, out)   # holiday overrides pre-holiday
    return out


# --------------------------------------------------------------------------- #
# §3.6  Season and weather
# --------------------------------------------------------------------------- #

def _season_factor(types, cal) -> np.ndarray:
    """Mild annual cycle for all; a stronger summer lift for tourist_center."""
    doy = pd.to_datetime(cal["date"]).dt.dayofyear.to_numpy()
    # Peaks in summer (~day 200), troughs in winter.
    annual = 1.0 + 0.05 * np.sin(2 * np.pi * (doy - 100) / 365.0)
    tourist = 1.0 + 0.40 * np.clip(np.sin(2 * np.pi * (doy - 100) / 365.0), 0, 1)
    out = np.tile(annual, (len(types), 1))
    is_tourist = np.array([t == "tourist_center" for t in types])
    out[is_tourist] = annual * tourist
    return out


def _weather_factor(types, cal) -> np.ndarray:
    """Cold/snow/rain depress street ATMs; indoor/mall barely affected (§3.6)."""
    temp = cal["temp_avg"].to_numpy(dtype=float)
    precip = cal["precip_mm"].to_numpy(dtype=float)
    snow = (cal["snowfall_mm"].to_numpy(dtype=float)
            if "snowfall_mm" in cal.columns else np.zeros(len(cal)))

    # Smooth severity in [0, ~0.65]: hard frost + heavy snow + heavy rain.
    cold = np.clip((-temp - 5.0) / 20.0, 0, 1) * 0.30
    snowy = np.clip(snow / 20.0, 0, 1) * 0.25
    rainy = np.clip(precip / 30.0, 0, 1) * 0.10
    severity = cold + snowy + rainy                              # (n_days,)

    outdoor = {"transport_market", "residential", "highway_gas"}
    sens = np.array([1.0 if t in outdoor else 0.15 for t in types])[:, None]
    return 1.0 - sens * severity[None, :]


# --------------------------------------------------------------------------- #
# §3.7  FX shock → cash run (short-lived, decays over a few days)
# --------------------------------------------------------------------------- #

# Peak FX boost by type; markets/tourists/business feel it most.
FX_MULT = {
    "transport_market": 1.8, "tourist_center": 1.9, "office_business": 1.6,
    "shopping_mall": 1.4, "residential": 1.25, "pension_social": 1.15,
    "highway_gas": 1.2,
}
_FX_DECAY = np.array([1.0, 0.55, 0.25])   # day-of-shock, +1, +2


def _fx_factor(types, cal) -> np.ndarray:
    """(n_atms, n_days) transient boost around FX shock days."""
    shock = cal["fx_shock"].to_numpy().astype(float)
    # Spread each shock forward over the decay kernel (a 1-3 day run).
    intensity = np.zeros(len(cal))
    for lag, w in enumerate(_FX_DECAY):
        if lag == 0:
            intensity = np.maximum(intensity, shock * w)
        else:
            shifted = np.zeros(len(cal))
            shifted[lag:] = shock[:-lag] * w
            intensity = np.maximum(intensity, shifted)
    per_type = np.array([FX_MULT[t] for t in types])[:, None]
    return 1.0 + (per_type - 1.0) * intensity[None, :]


# --------------------------------------------------------------------------- #
# §3.8  Trend / digitalisation and ATM commissioning step
# --------------------------------------------------------------------------- #

def _trend_factor(atms, cal, config) -> np.ndarray:
    """Logistic year-2 growth × install-date step (new ATMs switch on).

    Returns (n_atms, n_days). ATMs are silent (factor 0) before install_date —
    this creates the cold-start truncated history of §7.4.
    """
    dates = pd.to_datetime(cal["date"]).to_numpy()
    n_days = len(cal)
    t = np.arange(n_days)

    # Logistic growth centred near the start of year 2 (~day 365), normalised so
    # the network-average trend rises smoothly to (1 + uplift) by the end.
    uplift = config["intensity"]["trend_year2_uplift"]
    k = 8.0 / n_days
    logistic = 1.0 / (1.0 + np.exp(-k * (t - 365)))
    logistic = 1.0 + uplift * (logistic - logistic[0])          # starts ~1.0

    install = pd.to_datetime(atms["install_date"]).to_numpy()
    # (n_atms, n_days) mask: 1 once commissioned, 0 before.
    step = (dates[None, :] >= install[:, None]).astype(float)
    return step * logistic[None, :]


# --------------------------------------------------------------------------- #
# §3.1  Cox daily jitter ε(a, d)
# --------------------------------------------------------------------------- #

def _daily_noise(n_atms, n_days, config, rng) -> np.ndarray:
    """Lognormal per ATM-day multiplier with mean 1 (overdispersion source)."""
    sigma = config["intensity"]["daily_noise_sigma"]
    return rng.lognormal(mean=-0.5 * sigma ** 2, sigma=sigma, size=(n_atms, n_days))


# --------------------------------------------------------------------------- #
# Ramadan: intra-day reshaping (day ↓, evening ↑) — depends on (day, hour)
# --------------------------------------------------------------------------- #

def _ramadan_hourly(cal) -> np.ndarray:
    """(n_days, 24) multiplier: fasting daytime ×0.8, post-iftar evening ×1.2."""
    is_ram = cal["is_ramadan"].to_numpy()
    hourly = np.ones(24)
    hourly[8:17] = 0.8            # daytime fast
    hourly[18:23] = 1.2          # evening after iftar
    out = np.ones((len(cal), 24))
    out[is_ram] = hourly
    return out


# --------------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------------- #

def compute_hourly_intensity(atms: pd.DataFrame, calendar: pd.DataFrame,
                             config: dict,
                             rng: np.random.Generator | None = None) -> np.ndarray:
    """Return the (n_atms, n_days, 24) array of mean withdrawals λ(a, d, h)."""
    if rng is None:
        rng = np.random.default_rng(config["seed"])

    types = atms["atm_type"].to_numpy()
    scale = config["intensity"].get("volume_scale", 1.0)
    lam0 = atms["base_intensity"].to_numpy(dtype=float) * scale  # daily baseline
    n_atms, n_days = len(atms), len(calendar)
    dow = calendar["dow"].to_numpy()

    # Per-ATM shape jitter on the hourly/weekly profiles: two ATMs of the same
    # type are no longer identical, so neighbouring archetypes (residential ↔
    # pension_social) overlap and clustering is honestly hard (§9.10).
    jit = config["intensity"].get("profile_jitter", 0.0)
    base_h = np.stack([HOURLY_PROFILES[t] for t in types])       # (n_atms, 24)
    base_w = np.stack([WEEKLY_COEF[t] for t in types])           # (n_atms, 7)
    if jit > 0:
        base_h = base_h * rng.lognormal(0, jit, size=base_h.shape)
        base_w = base_w * rng.lognormal(0, jit, size=base_w.shape)
    base_h = base_h / base_h.sum(axis=1, keepdims=True) * 24.0   # Σ_h = 24
    base_w = base_w / base_w.mean(axis=1, keepdims=True)         # mean = 1

    # Per ATM-day multipliers (n_atms, n_days).
    daily = np.ones((n_atms, n_days))
    daily *= base_w[:, dow]
    daily *= _pay_factor(types, calendar)
    daily *= _pension_factor(types, calendar)
    daily *= _holiday_factor(types, calendar)
    daily *= _season_factor(types, calendar)
    daily *= _weather_factor(types, calendar)
    daily *= _fx_factor(types, calendar)
    daily *= _trend_factor(atms, calendar, config)              # includes install step
    daily *= _daily_noise(n_atms, n_days, config, rng)          # ε

    daily_lambda = lam0[:, None] * daily                        # (n_atms, n_days)

    # Split each day over hours: H/24 sums to 1, so hours integrate to the daily
    # volume. Ramadan reshapes the day (broadcast over ATMs).
    hshare = base_h / 24.0                                          # (n_atms, 24)
    ramadan = _ramadan_hourly(calendar)                             # (n_days, 24)

    lam = (daily_lambda[:, :, None]
           * hshare[:, None, :]
           * ramadan[None, :, :])
    np.clip(lam, 0.0, None, out=lam)                            # no negative λ
    return lam


def _smoke() -> None:
    """Quick self-check on real dimensions: ranges, non-negativity, profiles."""
    from . import load_config
    from .build_dims import build_all_dims

    config = load_config()
    tables = build_all_dims(config)
    atms, cal = tables["dim_atm"], tables["dim_calendar"]
    rng = np.random.default_rng(config["seed"])
    lam = compute_hourly_intensity(atms, cal, config, rng)

    assert lam.shape == (len(atms), len(cal), 24)
    assert np.all(lam >= 0), "negative intensity!"
    daily = lam.sum(axis=2)                                     # (n_atms, n_days)

    print("=== intensity smoke ===")
    print(f"shape {lam.shape}, total expected withdrawals/period ≈ {lam.sum():,.0f}")
    print(f"per-ATM mean daily withdrawals: {daily.mean():.1f} "
          f"(min {daily.mean(axis=1).min():.1f}, max {daily.mean(axis=1).max():.1f})")

    # Peak hour by archetype (should differ: market≠office≠residential).
    print("\nPeak hour by archetype:")
    for t in sorted(set(atms["atm_type"])):
        idx = np.where(atms["atm_type"].to_numpy() == t)[0]
        prof = lam[idx].mean(axis=(0, 1))
        print(f"  {t:17s} peak h={int(prof.argmax()):2d}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    _smoke()
