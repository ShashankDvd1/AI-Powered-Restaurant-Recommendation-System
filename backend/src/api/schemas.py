from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    data_ready: bool
    data_path: str
    restaurant_count: int | None = None


class RecommendationRequest(BaseModel):
    """Stub for Phase 2+; POST returns 501 until Phase 4."""

    location: str = Field(..., min_length=1)
    budget: str = Field(..., pattern="^(low|medium|high)$")
    cuisine: str = Field(..., min_length=1)
    min_rating: float = Field(default=3.5, ge=0.0, le=5.0)
    extra_preferences: str = ""
    top_k: int = Field(default=5, ge=1, le=20)


class NotImplementedDetail(BaseModel):
    detail: str
    phase: str
