"""Shared Parquet read/append-write helpers.

Used by data, harness, and execution layers. Enforces plan.md invariant 5:
execution logs (orders/fills/reconciliation) and the trial registry are
append-only — rows are never mutated or deleted, only added.
"""

from pathlib import Path

import pandas as pd


def read_parquet(path: Path) -> pd.DataFrame:
    """Read a Parquet file, returning an empty DataFrame if it doesn't exist yet."""
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


def write_parquet(df: pd.DataFrame, path: Path) -> None:
    """Overwrite a Parquet file. Only for derived/recomputable data
    (feature matrices, portfolios) — never for append-only logs.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)


def append_parquet(df: pd.DataFrame, path: Path) -> None:
    """Append rows to a Parquet file without mutating existing rows.

    Reads the existing file (if any), concatenates the new rows, and
    rewrites — Parquet has no native append, so this is the safe pattern
    for the trial registry and execution logs (plan.md invariant 5).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = read_parquet(path)
    combined = pd.concat([existing, df], ignore_index=True) if not existing.empty else df
    combined.to_parquet(path)
