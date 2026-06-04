from fastapi import APIRouter
from src.data.store import get_unique_cities, get_unique_cuisines

router = APIRouter(prefix="/metadata", tags=["metadata"])


@router.get("/locations", response_model=list[str])
def get_locations() -> list[str]:
    """Retrieve all unique restaurant locations/cities from the dataset."""
    try:
        return get_unique_cities()
    except FileNotFoundError:
        return []


@router.get("/cuisines", response_model=list[str])
def get_cuisines() -> list[str]:
    """Retrieve all unique cuisines from the dataset."""
    try:
        return get_unique_cuisines()
    except FileNotFoundError:
        return []
