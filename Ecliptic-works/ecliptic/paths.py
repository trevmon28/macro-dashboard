"""Central path constants for every data/ subdirectory.

See specs/005-ecliptic-works-fx/data-model.md's Storage Layout section —
if a path is needed that isn't listed there, update data-model.md first.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

RAW_DIR = DATA_DIR / "raw"
RAW_FX_DIR = RAW_DIR / "fx"
RAW_MACRO_DIR = RAW_DIR / "macro"

PROCESSED_DIR = DATA_DIR / "processed"
FEATURE_MATRIX_PATH = PROCESSED_DIR / "feature_matrix.parquet"
CARRY_PORTFOLIO_PATH = PROCESSED_DIR / "carry_portfolio.parquet"
MOMENTUM_PORTFOLIO_PATH = PROCESSED_DIR / "momentum_portfolio.parquet"
RISK_SCORE_ALIGNED_PATH = PROCESSED_DIR / "risk_score_aligned.parquet"

SIGNALS_DIR = DATA_DIR / "signals"

TRIALS_DIR = DATA_DIR / "trials"
TRIAL_REGISTRY_PATH = TRIALS_DIR / "trial_registry.parquet"

EXECUTION_DIR = DATA_DIR / "execution"
ORDERS_PATH = EXECUTION_DIR / "orders.parquet"
FILLS_PATH = EXECUTION_DIR / "fills.parquet"
RECONCILIATION_PATH = EXECUTION_DIR / "reconciliation.parquet"

CONFIGS_DIR = PROJECT_ROOT / "configs"
BASELINE_CONFIG_PATH = CONFIGS_DIR / "baseline.yml"

# Read-only: the macro-dashboard's own output, not owned by Ecliptic Works
MACRO_DASHBOARD_ROOT = PROJECT_ROOT.parent
MACRO_RISK_SCORE_PATH = MACRO_DASHBOARD_ROOT / "data" / "outputs" / "risk_score.parquet"


def fx_pair_year_path(pair: str, year: int) -> Path:
    return RAW_FX_DIR / pair / f"{year}.parquet"


def macro_series_path(series_id: str) -> Path:
    return RAW_MACRO_DIR / f"{series_id}.parquet"


def signal_path(date_str: str) -> Path:
    return SIGNALS_DIR / f"signal_{date_str}.json"
