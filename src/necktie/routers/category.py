"""Category endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from necktie.db.session import get_db
from necktie.repositories import CategoryRepository
from necktie.schemas import Category
from necktie.services.category import CategoryService

router = APIRouter(prefix="/category", tags=["category"])

DEFAULT_LANGUAGE = "en-US"


def get_service(db: Session = Depends(get_db)) -> CategoryService:
    """Build the service with its repository for this request."""
    return CategoryService(CategoryRepository(db))


@router.get("", response_model=list[Category])
def list_categories(
    language: str = Query(DEFAULT_LANGUAGE, description="Response language"),
    service: CategoryService = Depends(get_service),
) -> list[Category]:
    """List all categories, localized."""
    return service.list_categories(language=language)
