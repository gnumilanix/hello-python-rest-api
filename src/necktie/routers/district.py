"""District endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from necktie.db.session import get_db
from necktie.repositories import DistrictRepository
from necktie.schemas import District
from necktie.services.district import DistrictService

router = APIRouter(prefix="/district", tags=["district"])

DEFAULT_LANGUAGE = "en-US"


def get_service(db: Session = Depends(get_db)) -> DistrictService:
    """Build the service with its repository for this request."""
    return DistrictService(DistrictRepository(db))


@router.get("", response_model=list[District])
def list_districts(
    language: str = Query(DEFAULT_LANGUAGE, description="Response language"),
    service: DistrictService = Depends(get_service),
) -> list[District]:
    """List all districts ordered by sort_order, localized."""
    return service.list_districts(language=language)
