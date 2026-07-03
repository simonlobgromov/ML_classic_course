"""Orchestrator: run all external-data parsers in sequence.

Usage:
    python -m parsers.run_all          # uses ../config.yaml
    python -m parsers.run_all --force  # re-download even if cache exists

Each parser is independent: a failure in one does not stop the others.
The dimension generators fall back to synthetic data if a parquet is missing.
"""

import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s  %(levelname)-7s  %(message)s",
                    datefmt="%H:%M:%S")

# Resolve project root so we can import generator.load_config.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from generator import load_config
from parsers import weather, fx, osm_atms


def run(config: dict, force: bool = False) -> dict[str, tuple]:
    """
    Run all parsers. Returns {name: ("ok", n_rows) | ("failed", reason)}.
    """
    start = config["period"]["start"]
    end   = config["period"]["end"]
    results: dict[str, tuple] = {}

    for name, fn, kwargs in [
        ("weather", weather.fetch, {"start": start, "end": end, "force": force}),
        ("fx",      fx.fetch,      {"start": start, "end": end, "force": force}),
        ("osm",     osm_atms.fetch, {"force": force}),
    ]:
        try:
            df = fn(**kwargs)
            results[name] = ("ok", len(df))
        except Exception as exc:
            logging.warning("%s parser failed: %s", name, exc)
            results[name] = ("failed", str(exc))

    return results


def _print_summary(results: dict) -> None:
    print("\n=== Parser results ===")
    for name, (status, detail) in results.items():
        tag = "✓" if status == "ok" else "✗"
        suffix = f"{detail} rows" if status == "ok" else detail
        print(f"  {tag} {name:10s} {suffix}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all external data parsers.")
    parser.add_argument("--force", action="store_true",
                        help="Re-download even if cache exists.")
    args = parser.parse_args()

    config = load_config()
    results = run(config, force=args.force)
    _print_summary(results)

    if any(s == "failed" for s, _ in results.values()):
        print("Some parsers failed — dimension generators will use synthetic fallbacks.")


if __name__ == "__main__":
    main()
