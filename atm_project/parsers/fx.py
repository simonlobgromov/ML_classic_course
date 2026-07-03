"""Fetch historical USD/KGS exchange rates from the National Bank of the Kyrgyz Republic.

Output: external/fx_usd_kgs.parquet
Columns: date (datetime64[ns]), rate (float64)

Source: НБКР Excel archive — https://www.nbkr.kg/EXCEL/dailyrus.xls
One workbook with a sheet per year (2010..present); each sheet has columns
["дата*", "USD"] holding the daily official USD/KGS rate for trading days.
A single download covers the whole period, so no per-date requests are needed.

Strategy:
  - Download the archive once (with retries/backoff).
  - Read the sheets covering the requested years, drop note rows.
  - Reindex trading-day rates to a continuous daily series (forward-fill
    weekends/holidays from the previous trading day).
"""

import io
import logging

import pandas as pd

from . import EXTERNAL_DIR, _retry_get

log = logging.getLogger(__name__)

_ARCHIVE_URL = "https://www.nbkr.kg/EXCEL/dailyrus.xls"
OUTPUT = EXTERNAL_DIR / "fx_usd_kgs.parquet"


def fetch(start: str = "2024-01-01", end: str = "2025-12-31",
          force: bool = False) -> pd.DataFrame:
    """Download daily USD/KGS rate. Returns cached result if available."""
    if OUTPUT.exists() and not force:
        log.info("FX: cache hit %s", OUTPUT)
        return pd.read_parquet(OUTPUT)

    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)

    start_ts, end_ts = pd.Timestamp(start), pd.Timestamp(end)
    years = [str(y) for y in range(start_ts.year, end_ts.year + 1)]

    log.info("FX: downloading НБКР archive %s …", _ARCHIVE_URL)
    resp = _retry_get(_ARCHIVE_URL, timeout=60)
    book = pd.ExcelFile(io.BytesIO(resp.content), engine="xlrd")

    frames = []
    for year in years:
        if year not in book.sheet_names:
            log.warning("FX: sheet %s missing in archive — skipping", year)
            continue
        sheet = pd.read_excel(book, sheet_name=year, header=0).iloc[:, :2]
        sheet.columns = ["date", "rate"]
        frames.append(sheet)

    if not frames:
        raise ValueError(f"НБКР archive has no sheets for years {years}")

    raw = pd.concat(frames, ignore_index=True)
    raw["date"] = pd.to_datetime(raw["date"], errors="coerce")
    raw["rate"] = pd.to_numeric(raw["rate"], errors="coerce")
    raw = raw.dropna(subset=["date", "rate"])

    df = _build_full_series(raw, start_ts, end_ts)
    df.to_parquet(OUTPUT, index=False)
    log.info("FX: %d days saved (%d trading days) → %s", len(df), len(raw), OUTPUT)
    return df


def _build_full_series(raw: pd.DataFrame, start_ts: pd.Timestamp,
                       end_ts: pd.Timestamp) -> pd.DataFrame:
    """Reindex trading-day rates to a continuous daily series (ffill weekends)."""
    s = (raw.drop_duplicates("date", keep="last")
            .set_index("date")["rate"].sort_index())
    all_dates = pd.date_range(start_ts, end_ts, freq="D")
    # Union so forward-fill can see trading days that flank the requested range.
    full = s.reindex(all_dates.union(s.index)).ffill().bfill().reindex(all_dates)
    return pd.DataFrame({
        "date": all_dates.normalize(),
        "rate": full.round(4).values,
    })
