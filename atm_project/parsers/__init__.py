"""External data parsers: OSM ATM locations, Open-Meteo weather, НБКР FX rates.

All parsers follow the same contract:
  - cache-first: if the output parquet exists, return it without network calls;
  - retry with exponential backoff on transient failures;
  - raise on permanent failure so the caller can fall back to synthetic data.
"""

import time
import logging
from pathlib import Path

import requests

EXTERNAL_DIR = Path(__file__).resolve().parent.parent / "external"

log = logging.getLogger(__name__)

# A descriptive User-Agent; some APIs (e.g. Overpass) reject the bare
# python-requests default with 406 Not Acceptable.
_USER_AGENT = "atm-dataset-generator/1.0 (educational synthetic dataset; contact via project repo)"


def _retry_get(url: str, *, method: str = "get", data=None, params=None,
               retries: int = 3, backoff: float = 5.0, timeout: int = 90) -> requests.Response:
    """GET or POST with exponential-backoff retries."""
    headers = {"User-Agent": _USER_AGENT}
    for attempt in range(retries):
        try:
            if method == "post":
                r = requests.post(url, data=data, headers=headers, timeout=timeout)
            else:
                r = requests.get(url, params=params, headers=headers, timeout=timeout)
            r.raise_for_status()
            return r
        except requests.RequestException as exc:
            if attempt == retries - 1:
                raise
            wait = backoff * (2 ** attempt)
            log.warning("Attempt %d/%d failed (%s) — retrying in %.0fs …",
                        attempt + 1, retries, exc, wait)
            time.sleep(wait)
