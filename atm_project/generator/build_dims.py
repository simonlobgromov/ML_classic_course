"""Build all dimension (reference) tables and write them to the data directory.

Usage:
    python -m generator.build_dims            # uses ../config.yaml
"""

from pathlib import Path

import numpy as np

from . import load_config, PROJECT_ROOT
from .geography import build_districts
from .calendar import build_calendar
from .atms import build_atms
from .customers import build_customers, build_cards

# Small tables get a CSV mirror for easy inspection; large ones are Parquet only.
CSV_MIRROR = {"dim_district", "dim_calendar", "dim_atm"}


def build_all_dims(config: dict) -> dict:
    """Generate every dimension table. Returns a name -> DataFrame mapping."""
    # Independent RNG streams per table for reproducible, decoupled generation.
    streams = np.random.default_rng(config["seed"]).spawn(5)

    districts = build_districts(config)
    calendar = build_calendar(config, streams[0])
    atms = build_atms(config, streams[1])
    customers = build_customers(config, streams[2])
    cards = build_cards(config, customers, streams[3])

    return {
        "dim_district": districts,
        "dim_calendar": calendar,
        "dim_atm": atms,
        "dim_customer": customers,
        "dim_card": cards,
    }


def write_dims(tables: dict, config: dict) -> Path:
    """Write tables to <data_dir> as Parquet (+ CSV mirror for small ones)."""
    data_dir = PROJECT_ROOT / config["output"]["data_dir"]
    data_dir.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        df.to_parquet(data_dir / f"{name}.parquet", index=False)
        if config["output"]["write_csv_mirror"] and name in CSV_MIRROR:
            df.to_csv(data_dir / f"{name}.csv", index=False)
    return data_dir


def _summary(tables: dict) -> None:
    print("\n=== Dimension tables ===")
    for name, df in tables.items():
        print(f"{name:14s} rows={len(df):>8,}  cols={df.shape[1]}")

    atms = tables["dim_atm"]
    print("\nATM archetype distribution:")
    print(atms["atm_type"].value_counts().sort_index().to_string())

    cust = tables["dim_customer"]
    print("\nCustomer income_source mix:")
    print((cust["income_source"].value_counts(normalize=True)
           .round(3).sort_index()).to_string())

    cal = tables["dim_calendar"]
    print(f"\nCalendar: {len(cal)} days, "
          f"{int(cal['is_holiday'].sum())} holidays, "
          f"USD/KGS {cal['usd_kgs_rate'].iloc[0]} -> {cal['usd_kgs_rate'].iloc[-1]}, "
          f"{int(cal['fx_shock'].sum())} fx-shock days")


def main() -> None:
    config = load_config()
    tables = build_all_dims(config)
    out = write_dims(tables, config)
    _summary(tables)
    print(f"\nWritten to: {out}")


if __name__ == "__main__":
    main()
