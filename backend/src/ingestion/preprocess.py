"""Clean and normalize raw Zomato data to canonical schema."""

from __future__ import annotations

import re
from typing import Any

import numpy as np
import pandas as pd

# Canonical output columns
CANONICAL_COLUMNS = [
    "name",
    "city",
    "location",
    "cuisines",
    "rating",
    "approx_cost_for_two",
    "budget_bucket",
    "votes",
    "address",
    "rest_type",
    "online_order",
]

# Source column aliases (lowercase keys)
COLUMN_ALIASES: dict[str, list[str]] = {
    "name": [
        "name",
        "restaurant name",
        "restaurant_name",
        "restaurant",
    ],
    "city": ["city", "city name"],
    "location": [
        "location",
        "listed in(city)",
        "listed in (city)",
        "locality",
        "locality verbose",
        "locality_verbose",
    ],
    "cuisines": ["cuisines", "cuisine"],
    "rating": [
        "rating",
        "rate",
        "aggregate rating",
        "aggregate_rating",
        "stars",
    ],
    "approx_cost_for_two": [
        "approx_cost(for two people)",
        "approx cost (for two people)",
        "approx_cost_for_two",
        "average cost for two",
        "average_cost_for_two",
        "cost",
        "price",
    ],
    "votes": ["votes", "vote"],
    "address": ["address", "full address"],
    "rest_type": [
        "rest type",
        "rest_type",
        "type",
        "listed in(type)",
        "listed in (type)",
    ],
    "online_order": [
        "online_order",
        "online order",
        "has online delivery",
        "has_online_delivery",
    ],
}

CITY_ALIASES = {
    "bengaluru": "bangalore",
    "bangalore": "bangalore",
    "new delhi": "delhi",
    "delhi ncr": "delhi",
}

NON_NUMERIC_RATINGS = frozenset(
    {"new", "-", "nan", "", "none", "not rated", "no rating"}
)


def _normalize_key(col: str) -> str:
    return re.sub(r"\s+", " ", col.strip().lower())


def _find_column(df: pd.DataFrame, canonical: str) -> str | None:
    normalized = {_normalize_key(c): c for c in df.columns}
    for alias in COLUMN_ALIASES.get(canonical, [canonical]):
        key = _normalize_key(alias)
        if key in normalized:
            return normalized[key]
    return None


def _parse_rating(value: Any) -> float | None:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    text = str(value).strip().lower()
    if text in NON_NUMERIC_RATINGS:
        return None
    # e.g. "4.1/5"
    if "/" in text:
        text = text.split("/")[0].strip()
    match = re.search(r"(\d+\.?\d*)", text)
    if not match:
        return None
    rating = float(match.group(1))
    if rating > 5:
        rating = rating / 2  # scale 10-point if needed
    if rating < 0 or rating > 5:
        return None
    return round(rating, 2)


def _parse_cost(value: Any) -> float | None:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    if isinstance(value, (int, float)) and not np.isnan(value):
        return float(value)
    text = str(value).strip().lower()
    if text in {"", "-", "nan", "none"}:
        return None
    # Remove currency symbols and commas
    cleaned = re.sub(r"[^\d.]", "", text.replace(",", ""))
    if not cleaned:
        return None
    try:
        cost = float(cleaned)
        return cost if cost > 0 else None
    except ValueError:
        return None


def _normalize_city(value: Any) -> str | None:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    text = str(value).strip()
    if not text or text.lower() in NON_NUMERIC_RATINGS:
        return None
    # "BTM, Bangalore" -> take last segment after comma
    if "," in text:
        parts = [p.strip() for p in text.split(",") if p.strip()]
        text = parts[-1] if parts else text
    key = text.lower()
    key = CITY_ALIASES.get(key, key)
    return key.title() if key else None


def _normalize_cuisines(value: Any) -> str | None:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    text = str(value).strip()
    if not text or text.lower() in NON_NUMERIC_RATINGS:
        return None
    return text


def _assign_budget_buckets(costs: pd.Series) -> pd.Series:
    """Map numeric cost to low / medium / high using tertiles."""
    result = pd.Series("medium", index=costs.index, dtype=str)
    valid = costs.dropna()
    if len(valid) < 3:
        return result

    try:
        labels = pd.qcut(valid, q=3, labels=["low", "medium", "high"], duplicates="drop")
        result.loc[labels.index] = labels.astype(str)
        return result
    except ValueError:
        q33, q66 = valid.quantile(0.33), valid.quantile(0.66)
        for idx, value in costs.items():
            if pd.isna(value):
                continue
            if value <= q33:
                result[idx] = "low"
            elif value <= q66:
                result[idx] = "medium"
            else:
                result[idx] = "high"
        return result


def _extract_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Map raw columns to canonical schema."""
    out = pd.DataFrame(index=df.index)

    for canonical in COLUMN_ALIASES:
        src = _find_column(df, canonical)
        out[canonical] = df[src] if src else pd.Series([pd.NA] * len(df), index=df.index)

    # Prefer city column; fall back to location for city
    if out["city"].isna().all() and out["location"].notna().any():
        out["city"] = out["location"]

    out["name"] = out["name"].astype(str).str.strip()
    out["city"] = out["city"].apply(_normalize_city)
    out["location"] = out["location"].fillna(out["city"]).apply(
        lambda x: _normalize_city(x) if pd.notna(x) else None
    )
    out["cuisines"] = out["cuisines"].apply(_normalize_cuisines)
    out["rating"] = out["rating"].apply(_parse_rating)
    out["approx_cost_for_two"] = out["approx_cost_for_two"].apply(_parse_cost)

    votes_col = out["votes"]
    out["votes"] = pd.to_numeric(votes_col, errors="coerce").fillna(0).astype(int)

    for col in ("address", "rest_type", "online_order"):
        out[col] = out[col].apply(
            lambda x: str(x).strip() if pd.notna(x) and str(x).strip() else None
        )

    out["budget_bucket"] = _assign_budget_buckets(out["approx_cost_for_two"])
    return out


def preprocess_restaurants(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Clean raw data and return canonical DataFrame plus stats dict.
    """
    raw_count = len(df)
    extracted = _extract_frame(df)

    # Drop rows missing critical fields
    clean = extracted.dropna(subset=["name", "city", "rating"])
    clean = clean[clean["name"].str.len() > 0]
    clean = clean[clean["cuisines"].notna()]

    clean = clean.drop_duplicates(subset=["name", "city"], keep="first")
    clean = clean.reset_index(drop=True)

    # Enforce column order
    for col in CANONICAL_COLUMNS:
        if col not in clean.columns:
            clean[col] = None
    clean = clean[CANONICAL_COLUMNS]

    stats = {
        "raw_rows": raw_count,
        "processed_rows": len(clean),
        "dropped_rows": raw_count - len(clean),
        "columns": list(clean.columns),
        "cities_sample": sorted(clean["city"].dropna().unique().tolist())[:15],
    }
    return clean, stats


def sample_query_bangalore(df: pd.DataFrame, min_rating: float = 4.0) -> pd.DataFrame:
    """Acceptance check: Bangalore restaurants with rating >= min_rating."""
    city_match = df["city"].str.lower() == "bangalore"
    return df[city_match & (df["rating"] >= min_rating)]
