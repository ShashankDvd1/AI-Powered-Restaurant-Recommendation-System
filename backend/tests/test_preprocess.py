import pandas as pd

from src.ingestion.preprocess import preprocess_restaurants, sample_query_bangalore


def test_preprocess_minimal_raw():
    raw = pd.DataFrame(
        {
            "Restaurant Name": ["Cafe A", "Cafe B", "Bad"],
            "City": ["Bangalore", "Delhi", "Mumbai"],
            "Cuisines": ["Italian", "Chinese", None],
            "Aggregate rating": ["4.5", "3.0", "NEW"],
            "Average Cost for two": [500, 1200, 800],
            "Votes": [100, 50, 10],
            "Address": ["Addr 1", "Addr 2", "Addr 3"],
        }
    )
    processed, stats = preprocess_restaurants(raw)
    assert stats["processed_rows"] == 2
    assert "name" in processed.columns
    assert processed.loc[0, "budget_bucket"] in ("low", "medium", "high")


def test_bangalore_rating_filter():
    raw = pd.DataFrame(
        {
            "name": ["R1", "R2", "R3"],
            "city": ["bangalore", "bangalore", "delhi"],
            "location": ["bangalore", "bangalore", "delhi"],
            "cuisines": ["Italian", "Chinese", "Thai"],
            "rating": [4.5, 3.5, 4.8],
            "approx_cost_for_two": [400.0, 600.0, 500.0],
            "budget_bucket": ["low", "medium", "low"],
            "votes": [10, 20, 30],
            "address": [None, None, None],
            "rest_type": [None, None, None],
            "online_order": [None, None, None],
        }
    )
    result = sample_query_bangalore(raw, min_rating=4.0)
    assert len(result) == 1
    assert result.iloc[0]["name"] == "R1"
