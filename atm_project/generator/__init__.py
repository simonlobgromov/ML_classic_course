"""Synthetic MBank ATM dataset generator.

Modules build the star-schema reference tables (dimensions) and, later, the
per-second transaction fact table. See ../design.md for the full specification.
"""

from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_config(path: str | Path | None = None) -> dict:
    """Load the generator configuration from YAML."""
    path = Path(path) if path else PROJECT_ROOT / "config.yaml"
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)
