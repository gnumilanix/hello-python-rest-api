"""Category endpoints."""

from fastapi import APIRouter, Depends, Query
from fastapi_cache.decorator import cache

from necktie.routers.deps import get_category_service
from necktie.schemas import Category
from necktie.services.category import CategoryService
from necktie.utils.languages import Language

router = APIRouter(prefix="/category", tags=["category"])


@router.get("", response_model=list[Category])
@cache(expire=3600, namespace="category")
async def list_categories(
    language: Language = Query(Language.default(), description="Response language"),
    service: CategoryService = Depends(get_category_service),
) -> list[Category]:
    """List all categories, localized."""
    return await service.list_categories(language=language)
