"""Fetch ATM locations in Bishkek from OpenStreetMap via Overpass API.

Output: external/atm_locations.parquet
Columns: source_id, lat, lon, address, district_hint, placement_hint, is_24_7_hint

License: ODbL (© OpenStreetMap contributors). Attribution required.
"""

import logging

import pandas as pd

from . import EXTERNAL_DIR, _retry_get

log = logging.getLogger(__name__)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OUTPUT = EXTERNAL_DIR / "atm_locations.parquet"

_QUERY = """
[out:json][timeout:60];
node["amenity"="atm"](42.77,74.44,43.00,74.80);
out body;
"""


def fetch(force: bool = False) -> pd.DataFrame:
    """Download ATM node locations from OSM. Returns cached result if available."""
    if OUTPUT.exists() and not force:
        log.info("OSM ATMs: cache hit %s", OUTPUT)
        return pd.read_parquet(OUTPUT)

    log.info("OSM ATMs: querying Overpass API …")
    resp = _retry_get(OVERPASS_URL, method="post", data={"data": _QUERY})
    nodes = [e for e in resp.json().get("elements", []) if e.get("type") == "node"]

    rows = []
    for n in nodes:
        tags = n.get("tags", {})
        rows.append({
            "source_id": str(n["id"]),
            "lat": float(n["lat"]),
            "lon": float(n["lon"]),
            "address": tags.get("addr:full") or tags.get("addr:street", ""),
            "district_hint": tags.get("addr:district", ""),
            "placement_hint": _infer_placement(tags),
            "is_24_7_hint": tags.get("opening_hours", "").strip() == "24/7",
        })

    df = pd.DataFrame(rows) if rows else _empty_df()
    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT, index=False)
    log.info("OSM ATMs: %d locations saved → %s", len(df), OUTPUT)
    return df


def _infer_placement(tags: dict) -> str:
    loc = tags.get("location", "")
    if loc in ("inside", "indoor"):
        return "indoor_branch"
    name = tags.get("name", "").lower()
    if any(w in name for w in ("mall", "парк", "plaza", "vefa", "asia")):
        return "mall"
    if tags.get("amenity") == "fuel" or "azs" in name or "аzs" in name:
        return "gas_station"
    return "street"


def _empty_df() -> pd.DataFrame:
    return pd.DataFrame(columns=[
        "source_id", "lat", "lon", "address",
        "district_hint", "placement_hint", "is_24_7_hint",
    ])
