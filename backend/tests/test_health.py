from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "data_ready" in body


def test_recommendations_implemented():
    response = client.post(
        "/recommendations",
        json={
            "location": "Btm",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": 4.0,
        },
    )
    assert response.status_code == 200


