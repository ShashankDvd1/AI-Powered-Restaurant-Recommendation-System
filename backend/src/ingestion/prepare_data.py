"""
One-shot ingestion: Hugging Face -> clean -> data/processed/restaurants.parquet

Usage (from backend/):
    python -m src.ingestion.prepare_data
"""

from __future__ import annotations

import sys
from pathlib import Path

from src.config import DEFAULT_DATA_PATH, INGESTION_REPORT_PATH, PROJECT_ROOT
from src.ingestion.load_dataset import load_raw_dataframe
from src.ingestion.preprocess import preprocess_restaurants, sample_query_bangalore


def main() -> int:
    output_path = DEFAULT_DATA_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading dataset from Hugging Face...")
    raw = load_raw_dataframe()
    print(f"  Raw rows: {len(raw)}")
    print(f"  Raw columns: {list(raw.columns)}")

    processed, stats = preprocess_restaurants(raw)
    processed.to_parquet(output_path, index=False)

    bangalore = sample_query_bangalore(processed)
    stats["bangalore_rating_4_plus"] = len(bangalore)

    report_lines = [
        "Zomato ingestion report",
        "=======================",
        f"Project root: {PROJECT_ROOT}",
        f"Output: {output_path}",
        f"Raw rows: {stats['raw_rows']}",
        f"Processed rows: {stats['processed_rows']}",
        f"Dropped rows: {stats['dropped_rows']}",
        f"Bangalore rating >= 4.0: {stats['bangalore_rating_4_plus']}",
        f"Sample cities: {stats['cities_sample']}",
        "",
        "Canonical columns:",
        ", ".join(stats["columns"]),
    ]
    report = "\n".join(report_lines)
    INGESTION_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    INGESTION_REPORT_PATH.write_text(report, encoding="utf-8")

    print(report)
    print(f"\nSaved parquet to {output_path}")

    if stats["processed_rows"] == 0:
        print("ERROR: No rows after preprocessing.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
