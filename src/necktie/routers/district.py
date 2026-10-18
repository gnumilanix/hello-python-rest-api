"""District endpoints."""

from fastapi import APIRouter, Depends, Query
from fastapi_cache.decorator import cache

from necktie.routers.deps import get_district_service
from necktie.schemas import District
from necktie.services.district import DistrictService
from necktie.utils.constants import DEFAULT_LANGUAGE

router = APIRouter(prefix="/district", tags=["district"])


@router.get("", response_model=list[District])
@cache(expire=3600, namespace="district")
async def list_districts(
    language: str = Query(DEFAULT_LANGUAGE, description="Response language"),
    service: DistrictService = Depends(get_district_service),
) -> list[District]:
    """List all districts ordered by sort_order, localized."""
    return await service.list_districts(language=language)
