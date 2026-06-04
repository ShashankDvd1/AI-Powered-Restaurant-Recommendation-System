from fastapi import APIRouter
from src.api.schemas import RecommendationRequest
from src.models.preferences import UserPreferences
from src.models.recommendation import RecommendationResponse
from src.services.recommendation_service import get_recommendations

router = APIRouter(tags=["recommendations"])


@router.post(
    "/recommendations",
    response_model=RecommendationResponse,
)
def create_recommendations(body: RecommendationRequest) -> RecommendationResponse:
    """Validate user preferences and retrieve Zomato recommendations (grounded via Grok or fallback)."""
    prefs = UserPreferences(
        location=body.location,
        budget=body.budget,
        cuisine=body.cuisine,
        min_rating=body.min_rating,
        extra_preferences=body.extra_preferences,
        top_k=body.top_k,
    )
    return get_recommendations(prefs)

