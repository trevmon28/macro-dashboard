"""Loads configs/baseline.yml and exposes env-var overrides.

See specs/005-ecliptic-works-fx/quickstart.md's Key Environment Variables table.
"""

import os
from functools import lru_cache
from typing import Any

import yaml

from ecliptic.paths import BASELINE_CONFIG_PATH

FRED_API_KEY = os.environ.get("FRED_API_KEY")
ECLIPTIC_PORTFOLIO_SIZE = float(os.environ.get("ECLIPTIC_PORTFOLIO_SIZE", 100_000))
ECLIPTIC_DSR_THRESHOLD = float(os.environ.get("ECLIPTIC_DSR_THRESHOLD", 0.5))
ECLIPTIC_IBKR_PORT = int(os.environ.get("ECLIPTIC_IBKR_PORT", 7497))
ECLIPTIC_RISK_STALENESS_DAYS = int(os.environ.get("ECLIPTIC_RISK_STALENESS_DAYS", 7))


@lru_cache(maxsize=1)
def load_baseline_config() -> dict[str, Any]:
    """Load configs/baseline.yml (research defaults: carry bins, momentum window,
    DSR threshold, embargo days, etc.) — env vars above take precedence over
    this file's values where both exist.
    """
    with open(BASELINE_CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)
