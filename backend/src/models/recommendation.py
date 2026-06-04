from pydantic import BaseModel, Field

class RecommendationItem(BaseModel):
    restaurant_name: str
    cuisine: str
    rating: float
    estimated_cost: str
    explanation: str

class RecommendationMeta(BaseModel):
    candidate_count: int
    source: str  # "grok" or "fallback"

class RecommendationResponse(BaseModel):
    summary: str
    recommendations: list[RecommendationItem]
    meta: RecommendationMeta
