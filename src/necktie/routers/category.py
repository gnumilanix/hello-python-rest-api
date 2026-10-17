"""Category endpoints."""

from fastapi import APIRouter, Depends, Query

from necktie.routers.deps import get_category_service
from necktie.schemas import Category
from necktie.services.category import CategoryService

router = APIRouter(prefix="/category", tags=["category"])

DEFAULT_LANGUAGE = "en-US"


@router.get("", response_model=list[Category])
def list_categories(
    language: str = Query(DEFAULT_LANGUAGE, description="Response language"),
    service: CategoryService = Depends(get_category_service),
) -> list[Category]:
    """List all categories, localized."""
    return service.list_categories(language=language)
