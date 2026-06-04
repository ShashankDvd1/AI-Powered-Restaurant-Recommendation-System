"""Runtime access to processed restaurant data."""

from __future__ import annotations

import threading
from pathlib import Path

import pandas as pd

from src.config import get_settings

_lock = threading.RLock()
_df: pd.DataFrame | None = None
_unique_cities: list[str] | None = None
_unique_cuisines: list[str] | None = None


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


def get_unique_cities() -> list[str]:
    """Get sorted list of unique cities (cached)."""
    global _unique_cities
    if _unique_cities is None:
        with _lock:
            if _unique_cities is None:
                df = get_restaurant_dataframe()
                _unique_cities = sorted(df["city"].dropna().unique().tolist())
    return _unique_cities


def get_unique_cuisines() -> list[str]:
    """Get sorted list of unique cuisines (cached)."""
    global _unique_cuisines
    if _unique_cuisines is None:
        with _lock:
            if _unique_cuisines is None:
                df = get_restaurant_dataframe()
                cuisines_set = set()
                for c_str in df["cuisines"].dropna():
                    parts = [p.strip() for p in str(c_str).split(",") if p.strip()]
                    cuisines_set.update(parts)
                _unique_cuisines = sorted(list(cuisines_set))
    return _unique_cuisines

