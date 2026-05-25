from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from src.api.schemas import NotImplementedDetail, RecommendationRequest

router = APIRouter(tags=["recommendations"])


@router.post(
    "/recommendations",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=NotImplementedDetail,
)
def create_recommendations(_body: RecommendationRequest) -> JSONResponse:
    """Placeholder until Phase 4 wires filter + Grok pipeline."""
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={
            "detail": "Recommendation engine not implemented yet. Complete Phase 4.",
            "phase": "4",
        },
    )
