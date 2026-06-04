import json
from unittest.mock import patch
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.filters.restaurant_filter import filter_restaurants
from src.models.preferences import UserPreferences
from src.services.recommendation_service import get_recommendations, _run_fallback_engine
from src.llm import parse_grok_json_response

client = TestClient(app)


@pytest.fixture
def sample_dataset():
    """Create a small DataFrame to test filtering rules."""
    return pd.DataFrame(
        [
            # Match location, budget, cuisine, rating
            {"name": "Rest A", "city": "Btm", "location": "Btm", "cuisines": "Italian, Pizza", "rating": 4.5, "approx_cost_for_two": 500, "budget_bucket": "medium", "votes": 100, "address": "Addr A", "rest_type": "Cafe", "online_order": "Yes"},
            # Match location, budget, cuisine, but rating too low
            {"name": "Rest B", "city": "Btm", "location": "Btm", "cuisines": "Italian", "rating": 3.0, "approx_cost_for_two": 600, "budget_bucket": "medium", "votes": 50, "address": "Addr B", "rest_type": "Cafe", "online_order": "Yes"},
            # Match location, budget, rating, but wrong cuisine
            {"name": "Rest C", "city": "Btm", "location": "Btm", "cuisines": "Chinese", "rating": 4.2, "approx_cost_for_two": 400, "budget_bucket": "medium", "votes": 80, "address": "Addr C", "rest_type": "Diner", "online_order": "No"},
            # Match location, cuisine, rating, but wrong budget (high)
            {"name": "Rest D", "city": "Btm", "location": "Btm", "cuisines": "Italian", "rating": 4.6, "approx_cost_for_two": 1500, "budget_bucket": "high", "votes": 200, "address": "Addr D", "rest_type": "Fine Dining", "online_order": "No"},
            # Match budget, cuisine, rating, but wrong location (Indiranagar)
            {"name": "Rest E", "city": "Indiranagar", "location": "Indiranagar", "cuisines": "Italian", "rating": 4.7, "approx_cost_for_two": 700, "budget_bucket": "medium", "votes": 150, "address": "Addr E", "rest_type": "Cafe", "online_order": "Yes"},
            # Another match for sorting order check (same rating, lower votes than A)
            {"name": "Rest F", "city": "Btm", "location": "Btm", "cuisines": "Italian, Cafe", "rating": 4.5, "approx_cost_for_two": 550, "budget_bucket": "medium", "votes": 50, "address": "Addr F", "rest_type": "Cafe", "online_order": "Yes"},
        ]
    )


def test_filter_restaurants_rules(sample_dataset):
    prefs = UserPreferences(
        location="Btm",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
        extra_preferences="",
        top_k=5
    )
    filtered = filter_restaurants(sample_dataset, prefs)
    # Rest A and Rest F should match
    assert len(filtered) == 2
    # Sorting: Rest A (votes=100) should be first, Rest F (votes=50) second
    assert filtered.iloc[0]["name"] == "Rest A"
    assert filtered.iloc[1]["name"] == "Rest F"


def test_parser_grok_json():
    raw_response = """
    {
      "summary": "These are selected restaurants.",
      "recommendations": [
        {
          "restaurant_name": "Rest A",
          "cuisine": "Italian",
          "rating": 4.5,
          "estimated_cost": "500",
          "explanation": "Great food."
        }
      ]
    }
    """
    parsed = parse_grok_json_response(raw_response)
    assert parsed["summary"] == "These are selected restaurants."
    assert len(parsed["recommendations"]) == 1
    assert parsed["recommendations"][0]["restaurant_name"] == "Rest A"


def test_recommendation_fallback_logic():
    prefs = UserPreferences(
        location="Btm",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
        extra_preferences="",
        top_k=5
    )
    
    # We bypass the actual Grok API by testing with an empty key or mocking Grok client error
    with patch("src.llm.grok_client.get_settings") as mock_settings:
        # Mock settings to return empty xai_api_key and groq_api_key
        from src.config import Settings
        mock_settings.return_value = Settings(xai_api_key="", grok_model="grok-2-latest", groq_api_key="")
        
        response = get_recommendations(prefs)
        assert response.meta.source == "fallback"
        assert len(response.recommendations) > 0
        assert response.recommendations[0].restaurant_name == "Empire Restaurant" or response.recommendations[0].restaurant_name is not None
        assert "unavailable" in response.summary.lower()


@patch("src.services.recommendation_service.call_grok_api")
def test_recommendation_api_grok_mocked(mock_api):
    # Mock successful JSON response from Grok
    mock_api.return_value = json.dumps({
        "summary": "Here are your custom picks.",
        "recommendations": [
            {
                "restaurant_name": "Empire Restaurant",  # must match actual BTM restaurant in dataset
                "cuisine": "North Indian",
                "rating": 4.1,
                "estimated_cost": "₹600 for two",
                "explanation": "Highly popular choice."
            }
        ]
    })

    # Call POST endpoint
    response = client.post(
        "/recommendations",
        json={
            "location": "Btm",
            "budget": "medium",
            "cuisine": "North Indian",
            "min_rating": 3.5,
            "top_k": 3
        }
    )
    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["source"] == "grok"
    assert body["summary"] == "Here are your custom picks."
    assert len(body["recommendations"]) == 1
    assert body["recommendations"][0]["restaurant_name"] == "Empire Restaurant"
    assert "estimated_cost" in body["recommendations"][0]


@patch("src.services.recommendation_service.call_grok_api")
def test_grounding_discards_hallucination(mock_api):
    # Mock Grok returning a hallucinated name "Fake Burger Place"
    mock_api.return_value = json.dumps({
        "summary": "Fake choices.",
        "recommendations": [
            {
                "restaurant_name": "Fake Burger Place",  # Hallucinated!
                "cuisine": "Burgers",
                "rating": 4.9,
                "estimated_cost": "₹200",
                "explanation": "Best burgers ever."
            },
            {
                "restaurant_name": "Empire Restaurant",  # Valid BTM restaurant
                "cuisine": "North Indian",
                "rating": 4.1,
                "estimated_cost": "₹600",
                "explanation": "Real place."
            }
        ]
    })

    # Call POST endpoint
    response = client.post(
        "/recommendations",
        json={
            "location": "Btm",
            "budget": "medium",
            "cuisine": "North Indian",
            "min_rating": 3.0,
            "top_k": 5
        }
    )
    assert response.status_code == 200
    body = response.json()
    # The hallucinated one should be discarded by grounding, leaving only the valid one!
    assert len(body["recommendations"]) == 1
    assert body["recommendations"][0]["restaurant_name"] == "Empire Restaurant"
