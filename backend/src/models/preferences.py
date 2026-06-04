from pydantic import BaseModel, Field
from typing import Literal

class UserPreferences(BaseModel):
    location: str
    budget: Literal["low", "medium", "high"]
    cuisine: str
    min_rating: float = Field(default=3.5, ge=0.0, le=5.0)
    extra_preferences: str = ""
    top_k: int = Field(default=5, ge=1, le=20)

    def to_dict(self) -> dict:
        return self.model_dump()
