"""Runtime access to processed restaurant data."""

from __future__ import annotations

import threading
from pathlib import Path

import pandas as pd

from src.config import get_settings

_lock = threading.Lock()
_df: pd.DataFrame | None = None


def is_data_ready() -> bool:
    return get_settings().processed_data_path.is_file()


def get_data_path() -> Path:
    return get_settings().processed_data_path


def get_restaurant_dataframe(*, reload: bool = False) -> pd.DataFrame:
    """Load processed parquet (cached singleton)."""
    global _df

    path = get_data_path()
    if not path.is_file():
        raise FileNotFoundError(
            f"Processed dataset not found at {path}. "
            "Run: cd backend && python -m src.ingestion.prepare_data"
        )

    with _lock:
        if _df is None or reload:
            _df = pd.read_parquet(path)
        return _df.copy()
