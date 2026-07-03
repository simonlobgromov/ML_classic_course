"""Fetch historical daily weather for Bishkek from Open-Meteo (ERA5 reanalysis).

Output: external/weather_daily.parquet
Columns: date, temp_avg, temp_max, temp_min, precip_mm, snowfall_mm, wind_max, weathercode

Source: Open-Meteo Historical Weather API — https://open-meteo.com/
License: CC BY 4.0 (attribution required).
"""

import logging

import pandas as pd

from . import EXTERNAL_DIR, _retry_get

log = logging.getLogger(__name__)

_API_URL = "https://archive-api.open-meteo.com/v1/archive"
OUTPUT = EXTERNAL_DIR / "weather_daily.parquet"

BISHKEK_LAT = 42.87
BISHKEK_LON = 74.59

_DAILY_VARS = ",".join([
    "temperature_2m_mean",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "snowfall_sum",
    "windspeed_10m_max",
    "weathercode",
])


def fetch(start: str = "2024-01-01", end: str = "2025-12-31",
          force: bool = False) -> pd.DataFrame:
    """Download daily weather. Returns cached result if available."""
    if OUTPUT.exists() and not force:
        log.info("Weather: cache hit %s", OUTPUT)
        return pd.read_parquet(OUTPUT)

    log.info("Weather: fetching Open-Meteo %s → %s …", start, end)
    params = {
        "latitude": BISHKEK_LAT,
        "longitude": BISHKEK_LON,
        "start_date": start,
        "end_date": end,
        "daily": _DAILY_VARS,
        "timezone": "Asia/Bishkek",
    }
    resp = _retry_get(_API_URL, params=params)
    daily = resp.json()["daily"]

    df = pd.DataFrame({
        "date": pd.to_datetime(daily["time"]).normalize(),
        "temp_avg":    daily["temperature_2m_mean"],
        "temp_max":    daily["temperature_2m_max"],
        "temp_min":    daily["temperature_2m_min"],
        "precip_mm":   daily["precipitation_sum"],
        "snowfall_mm": daily["snowfall_sum"],
        "wind_max":    daily["windspeed_10m_max"],
        "weathercode": daily["weathercode"],
    })

    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT, index=False)
    log.info("Weather: %d days saved → %s", len(df), OUTPUT)
    return df
