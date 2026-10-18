"""Category endpoints."""

from fastapi import APIRouter, Depends, Query
from fastapi_cache.decorator import cache

from necktie.routers.deps import get_category_service
from necktie.schemas import Category
from necktie.services.category import CategoryService
from necktie.utils.constants import DEFAULT_LANGUAGE

router = APIRouter(prefix="/category", tags=["category"])


@router.get("", response_model=list[Category])
@cache(expire=3600, namespace="category")
async def list_categories(
    language: str = Query(DEFAULT_LANGUAGE, description="Response language"),
    service: CategoryService = Depends(get_category_service),
) -> list[Category]:
    """List all categories, localized."""
    return await service.list_categories(language=language)
