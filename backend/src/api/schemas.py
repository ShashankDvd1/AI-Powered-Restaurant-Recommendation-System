from pydantic import BaseModel, Field, field_validator


class HealthResponse(BaseModel):
    status: str
    data_ready: bool
    data_path: str
    restaurant_count: int | None = None


class RecommendationRequest(BaseModel):
    """Request schema for restaurant recommendations."""

    location: str = Field(..., min_length=1)
    budget: str = Field(..., pattern="^(low|medium|high)$")
    cuisine: str = Field(..., min_length=1)
    min_rating: float = Field(default=3.5, ge=0.0, le=5.0)
    extra_preferences: str = ""
    top_k: int = Field(default=5, ge=1, le=20)

    @field_validator("location")
    @classmethod
    def validate_location(cls, v: str) -> str:
        from src.data.store import is_data_ready, get_unique_cities
        if not is_data_ready():
            return v

        cities = get_unique_cities()
        cities_lower = [c.lower() for c in cities]
        v_clean = v.strip().lower()
        if v_clean in cities_lower:
            idx = cities_lower.index(v_clean)
            return cities[idx]

        import difflib
        suggestions = difflib.get_close_matches(v, cities, n=3, cutoff=0.4)
        if suggestions:
            suggestion_str = ", ".join(suggestions)
            raise ValueError(f"Unknown location '{v}'. Did you mean: {suggestion_str}?")
        else:
            raise ValueError(f"Unknown location '{v}'. Please select from valid cities.")



class NotImplementedDetail(BaseModel):
    detail: str
    phase: str
