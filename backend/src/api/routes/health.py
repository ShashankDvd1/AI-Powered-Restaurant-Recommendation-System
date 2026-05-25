from fastapi import APIRouter

from src.api.schemas import HealthResponse
from src.config import get_settings
from src.data.store import get_data_path, is_data_ready

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    path = get_data_path()
    ready = is_data_ready()
    count: int | None = None

    if ready:
        try:
            from src.data.store import get_restaurant_dataframe

            count = len(get_restaurant_dataframe())
        except Exception:
            count = None

    return HealthResponse(
        status="ok",
        data_ready=ready,
        data_path=str(path),
        restaurant_count=count,
    )
