from fastapi.testclient import TestClient
import pytest
from pydantic import ValidationError

from src.api.main import app
from src.api.schemas import RecommendationRequest
from src.data.store import get_unique_cities, get_unique_cuisines

client = TestClient(app)


def test_metadata_locations():
    response = client.get("/metadata/locations")
    assert response.status_code == 200
    cities = response.json()
    assert isinstance(cities, list)
    assert len(cities) > 0
    assert "Btm" in cities


def test_metadata_cuisines():
    response = client.get("/metadata/cuisines")
    assert response.status_code == 200
    cuisines = response.json()
    assert isinstance(cuisines, list)
    assert len(cuisines) > 0
    assert "Italian" in cuisines


def test_recommendation_request_valid():
    # Valid request
    req = RecommendationRequest(
        location="Btm",
        budget="medium",
        cuisine="Italian",
        min_rating=4.0,
        extra_preferences="rooftop",
        top_k=5
    )
    assert req.location == "Btm"
    assert req.budget == "medium"


def test_recommendation_request_casing():
    # Casing normalization test
    req = RecommendationRequest(
        location="btm",  # should normalize to "Btm"
        budget="low",
        cuisine="Chinese"
    )
    assert req.location == "Btm"


def test_recommendation_request_invalid_rating():
    with pytest.raises(ValidationError):
        RecommendationRequest(
            location="Btm",
            budget="medium",
            cuisine="Italian",
            min_rating=6.0  # rating must be <= 5.0
        )


def test_recommendation_request_invalid_budget():
    with pytest.raises(ValidationError):
        RecommendationRequest(
            location="Btm",
            budget="premium",  # budget must be low, medium, or high
            cuisine="Italian"
        )


def test_recommendation_request_invalid_location():
    # Test fuzzy suggestion matching
    with pytest.raises(ValidationError) as exc_info:
        RecommendationRequest(
            location="btmm",  # close to "Btm"
            budget="medium",
            cuisine="Italian"
        )
    assert "Did you mean: Btm" in str(exc_info.value)
