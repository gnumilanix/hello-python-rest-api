"""District endpoints."""

from fastapi import APIRouter, Depends, Query

from necktie.routers.deps import get_district_service
from necktie.schemas import District
from necktie.services.district import DistrictService

router = APIRouter(prefix="/district", tags=["district"])

DEFAULT_LANGUAGE = "en-US"


@router.get("", response_model=list[District])
def list_districts(
    language: str = Query(DEFAULT_LANGUAGE, description="Response language"),
    service: DistrictService = Depends(get_district_service),
) -> list[District]:
    """List all districts ordered by sort_order, localized."""
    return service.list_districts(language=language)
