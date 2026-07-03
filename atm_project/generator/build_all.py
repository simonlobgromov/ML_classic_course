"""End-to-end dataset build: dimensions → transactions → cash → anomalies.

Usage:
    python -m generator.build_all              # full period, all months
    python -m generator.build_all --months 2024-03 2024-04   # subset (dev)

Runs the whole pipeline with independent RNG streams per stage and prints a
summary. Reference tables land in data/, fact_transactions is partitioned by
year/month, ground truth in labels/.
"""

import argparse
import logging
import time

import numpy as np

from . import load_config
from .build_dims import build_all_dims, write_dims
from .transactions import build_transactions
from .cash_ops import build_cash_ops
from .anomalies import inject_anomalies

log = logging.getLogger(__name__)


def build_all(config: dict, months: list[str] | None = None) -> dict:
    """Run every stage in order; return a summary dict."""
    # Independent, reproducible RNG streams per stage.
    s_dims, s_txn, s_cash, s_anom = np.random.default_rng(config["seed"]).spawn(4)

    t0 = time.time()
    log.info("[1/4] Dimensions …")
    tables = build_all_dims(config)
    write_dims(tables, config)

    log.info("[2/4] Transactions …")
    txn_summary = build_transactions(config, tables, s_txn, months=months)
    total_txn = sum(txn_summary.values())

    log.info("[3/4] Cash management …")
    cash_summary = build_cash_ops(config, tables, s_cash)

    log.info("[4/4] Anomalies …")
    anom_summary = inject_anomalies(config, tables, s_anom)

    elapsed = time.time() - t0
    return {
        "months": len(txn_summary),
        "transactions": total_txn,
        "cash": cash_summary,
        "anomalies": anom_summary,
        "elapsed_s": round(elapsed, 1),
    }


def _print_summary(s: dict) -> None:
    print("\n=== build_all summary ===")
    print(f"months generated : {s['months']}")
    print(f"transactions     : {s['transactions']:,}")
    print(f"cash refills     : {s['cash']['refills']:,}")
    print(f"out_of_cash      : {s['cash']['out_of_cash']:,} events, "
          f"{s['cash']['declined_99']:,} '99' declines")
    a = s["anomalies"]
    print(f"fault windows    : {a['fault_windows']:,} ({a['fault_txns']:,} txns)")
    print(f"fraud / geo rows : {a['fraud_rows']:,} / {a['geo_rows']:,}")
    print(f"elapsed          : {s['elapsed_s']} s")


def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s  %(levelname)-7s  %(message)s",
                        datefmt="%H:%M:%S")
    ap = argparse.ArgumentParser(description="Build the full ATM dataset.")
    ap.add_argument("--months", nargs="*", default=None,
                    help="Restrict to specific 'YYYY-MM' months (dev/testing).")
    args = ap.parse_args()

    config = load_config()
    summary = build_all(config, months=args.months)
    _print_summary(summary)


if __name__ == "__main__":
    main()
