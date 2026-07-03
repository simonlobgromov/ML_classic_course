"""dim_calendar: one row per day with holidays, paydays, climate and FX rate.

All temporal seasonality of the network lives here. Climate and FX are synthetic
but realistic in v1 (Bishkek climatology; a random walk for USD/KGS) and can be
swapped for downloaded real series later without touching the schema.
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

# Fixed-date public holidays of the Kyrgyz Republic (month, day) -> name.
FIXED_HOLIDAYS = {
    (1, 1): "Новый год",
    (1, 2): "Новогодние каникулы",
    (1, 3): "Новогодние каникулы",
    (1, 4): "Новогодние каникулы",
    (1, 5): "Новогодние каникулы",
    (1, 6): "Новогодние каникулы",
    (1, 7): "Рождество Христово",
    (2, 23): "День защитника Отечества",
    (3, 8): "Международный женский день",
    (3, 21): "Нооруз",
    (4, 7): "День Апрельской народной революции",
    (5, 1): "Праздник труда",
    (5, 5): "День Конституции",
    (5, 9): "День Победы",
    (8, 31): "День независимости",
    (11, 7): "Дни истории и памяти предков",
    (11, 8): "Дни истории и памяти предков",
}

# Floating Islamic holidays (lunar calendar) by year.
ISLAMIC_HOLIDAYS = {
    "2024-04-10": "Орозо айт",
    "2025-03-30": "Орозо айт",
    "2024-06-17": "Курман айт",
    "2025-06-06": "Курман айт",
}

# Ramadan (Orozo) fasting periods (inclusive) by year.
RAMADAN_PERIODS = [
    ("2024-03-11", "2024-04-09"),
    ("2025-03-01", "2025-03-29"),
]

# Pre-holiday shortened days (month, day).
PRE_HOLIDAYS = {(2, 22), (3, 7), (3, 20), (4, 30), (5, 8), (8, 30), (11, 6), (12, 31)}

# Monthly climatology of Bishkek: mean temperature (°C) for months 1..12.
MONTHLY_TEMP = np.array([-1, 1, 9, 15, 22, 26, 30, 29, 24, 14, 6, 1], dtype=float)
# Relative precipitation propensity per month (0..1); April is the wettest.
MONTHLY_PRECIP = np.array(
    [0.10, 0.15, 0.50, 1.00, 0.80, 0.70, 0.25, 0.15, 0.20, 0.45, 0.40, 0.20]
)

_SEASON = {12: "winter", 1: "winter", 2: "winter",
           3: "spring", 4: "spring", 5: "spring",
           6: "summer", 7: "summer", 8: "summer",
           9: "autumn", 10: "autumn", 11: "autumn"}


def _daily_temperature(dates: pd.DatetimeIndex, rng: np.random.Generator) -> np.ndarray:
    """Smoothly interpolated daily mean temperature with day-to-day noise."""
    # Month centres at ~day 15; interpolate over a periodic day-of-year axis.
    month_centre_doy = np.array([15, 46, 74, 105, 135, 166, 196, 227,
                                 258, 288, 319, 349], dtype=float)
    # Pad for wrap-around so January interpolates from December.
    xp = np.concatenate(([month_centre_doy[-1] - 365], month_centre_doy,
                         [month_centre_doy[0] + 365]))
    fp = np.concatenate(([MONTHLY_TEMP[-1]], MONTHLY_TEMP, [MONTHLY_TEMP[0]]))
    doy = dates.dayofyear.to_numpy().astype(float)
    base = np.interp(doy, xp, fp)
    return np.round(base + rng.normal(0, 2.5, size=len(dates)), 1)


def _daily_precip(dates: pd.DatetimeIndex, rng: np.random.Generator) -> np.ndarray:
    """Daily precipitation (mm); zero on dry days, exponential on wet days."""
    month = dates.month.to_numpy()
    wet_prob = MONTHLY_PRECIP[month - 1] * 0.5          # share of wet days
    is_wet = rng.random(len(dates)) < wet_prob
    amount = rng.exponential(scale=8.0, size=len(dates)) * MONTHLY_PRECIP[month - 1]
    return np.round(np.where(is_wet, amount, 0.0), 1)


def _fx_series(dates: pd.DatetimeIndex, fx_cfg: dict,
               rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """USD/KGS random walk with mild drift and occasional shocks."""
    n = len(dates)
    drift = np.log(1 + fx_cfg["drift_per_year"]) / 365.0
    returns = rng.normal(drift, fx_cfg["daily_vol"], size=n)
    # Inject shock days (sign random) on top of the ordinary returns.
    shock_days = rng.random(n) < fx_cfg["shock_prob"]
    shock_sign = rng.choice([-1.0, 1.0], size=n)
    returns += shock_days * shock_sign * fx_cfg["shock_size"]
    log_rate = np.log(fx_cfg["base_rate"]) + np.cumsum(returns)
    rate = np.round(np.exp(log_rate), 4)
    change_pct = np.round(np.concatenate(([0.0], np.diff(rate) / rate[:-1] * 100)), 3)
    fx_shock = np.abs(change_pct) > (fx_cfg["shock_size"] * 100 * 0.7)
    return rate, change_pct, fx_shock


def build_calendar(config: dict, rng: np.random.Generator | None = None) -> pd.DataFrame:
    """Return the dim_calendar reference table for the configured period."""
    if rng is None:
        rng = np.random.default_rng(config["seed"])

    start, end = config["period"]["start"], config["period"]["end"]
    dates = pd.date_range(start, end, freq="D")
    df = pd.DataFrame({"date": dates})

    df["dow"] = dates.dayofweek
    df["is_weekend"] = df["dow"] >= 5
    df["month"] = dates.month
    df["day"] = dates.day

    # Holidays (fixed + floating Islamic).
    md = list(zip(dates.month, dates.day))
    df["holiday_name"] = [FIXED_HOLIDAYS.get(k) for k in md]
    iso = dates.strftime("%Y-%m-%d")
    for i, d in enumerate(iso):
        if d in ISLAMIC_HOLIDAYS:
            df.loc[i, "holiday_name"] = ISLAMIC_HOLIDAYS[d]
    df["is_holiday"] = df["holiday_name"].notna()

    # Pre-holiday shortened days.
    df["is_pre_holiday"] = [k in PRE_HOLIDAYS for k in md]

    # Ramadan periods.
    is_ramadan = np.zeros(len(df), dtype=bool)
    for lo, hi in RAMADAN_PERIODS:
        is_ramadan |= (dates >= lo) & (dates <= hi)
    df["is_ramadan"] = is_ramadan

    # Pay cycles: salaries mid-month (10-14) and advance (25-27); pensions from 10th.
    day = df["day"].to_numpy()
    df["is_pension_day"] = (day >= 10) & (day <= 14)
    df["is_payday"] = ((day >= 10) & (day <= 14)) | ((day >= 25) & (day <= 27))

    df["season"] = df["month"].map(_SEASON)
    df["temp_avg"] = _daily_temperature(dates, rng)
    df["precip_mm"] = _daily_precip(dates, rng)

    rate, change_pct, fx_shock = _fx_series(dates, config["calendar"]["fx"], rng)
    df["usd_kgs_rate"] = rate
    df["fx_change_pct"] = change_pct
    df["fx_shock"] = fx_shock

    df["year_index"] = (dates.year - dates.year.min()).astype(int)

    df = df.drop(columns=["day"])

    # Replace synthetic placeholders with real downloaded series if available.
    from . import EXTERNAL_DIR
    _merge_real_weather(df, EXTERNAL_DIR)
    _merge_real_fx(df, EXTERNAL_DIR)

    return df


def _merge_real_weather(df: pd.DataFrame, external_dir: Path) -> None:
    path = external_dir / "weather_daily.parquet"
    if not path.exists():
        return
    w = pd.read_parquet(path)
    w["date"] = pd.to_datetime(w["date"]).dt.normalize()
    idx = w.set_index("date")

    dates_norm = pd.to_datetime(df["date"]).dt.normalize()
    matched = dates_norm.isin(idx.index).sum()

    for col in ("temp_avg", "precip_mm"):
        if col in idx.columns:
            df[col] = dates_norm.map(idx[col]).fillna(df[col]).values

    for col in ("snowfall_mm", "wind_max", "weathercode"):
        if col in idx.columns:
            df[col] = dates_norm.map(idx[col]).values

    log.info("Calendar: real weather merged (%d/%d days matched)", matched, len(df))


def _merge_real_fx(df: pd.DataFrame, external_dir: Path) -> None:
    path = external_dir / "fx_usd_kgs.parquet"
    if not path.exists():
        return
    fx = pd.read_parquet(path)
    fx["date"] = pd.to_datetime(fx["date"]).dt.normalize()
    idx = fx.set_index("date")["rate"]

    dates_norm = pd.to_datetime(df["date"]).dt.normalize()
    matched = dates_norm.isin(idx.index).sum()

    real_rate = dates_norm.map(idx)
    if real_rate.notna().any():
        df["usd_kgs_rate"] = real_rate.fillna(df["usd_kgs_rate"]).values
        prev = df["usd_kgs_rate"].shift(1)
        df["fx_change_pct"] = ((df["usd_kgs_rate"] - prev) / prev * 100).round(3).fillna(0).values
        shock_threshold = 0.7  # same fraction as synthetic
        df["fx_shock"] = df["fx_change_pct"].abs() > shock_threshold

    log.info("Calendar: real FX merged (%d/%d days matched)", matched, len(df))
