"""Doctor endpoints.

The resource is exposed as ``/doctor`` while the underlying table is
``practitioners``. Routes delegate to the service layer; this module only
handles HTTP concerns (params, status codes, error mapping).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from necktie.db.session import get_db
from necktie.repositories import PractitionerRepository
from necktie.schemas import DoctorCreate, DoctorDetail, DoctorListItem
from necktie.services import (
    CategoryNotFoundError,
    DistrictNotFoundError,
    PractitionerNotFoundError,
    PractitionerService,
)

router = APIRouter(prefix="/doctor", tags=["doctor"])

DEFAULT_LANGUAGE = "en-US"


def get_service(db: Session = Depends(get_db)) -> PractitionerService:
    """Build the service with its repository for this request."""
    return PractitionerService(PractitionerRepository(db))


@router.get("", response_model=list[DoctorListItem])
def list_doctors(
    district: int | None = Query(None, description="District id"),
    category: int | None = Query(None, description="Category id"),
    min_fee: int | None = Query(None, ge=0, description="Min consultation fee"),
    max_fee: int | None = Query(None, ge=0, description="Max consultation fee"),
    language: str = Query(DEFAULT_LANGUAGE, description="Response language"),
    page: int = Query(0, ge=0, description="Page number (0-based)"),
    size: int = Query(20, ge=10, le=100, description="Page size (10-100)"),
    service: PractitionerService = Depends(get_service),
) -> list[DoctorListItem]:
    """List doctors, filterable and paginated."""
    return service.list_doctors(
        district_id=district,
        category_id=category,
        min_fee=min_fee,
        max_fee=max_fee,
        language=language,
        offset=page * size,
        limit=size,
    )


@router.get("/{doctor_id}", response_model=DoctorDetail)
def get_doctor(
    doctor_id: int, service: PractitionerService = Depends(get_service)
) -> DoctorDetail:
    """Get one doctor with all translations."""
    try:
        return service.get_doctor(doctor_id)
    except PractitionerNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Doctor not found") from None


@router.post("", response_model=DoctorDetail, status_code=status.HTTP_201_CREATED)
def create_doctor(
    payload: DoctorCreate, service: PractitionerService = Depends(get_service)
) -> DoctorDetail:
    """Create a single doctor."""
    try:
        return service.create_doctor(payload)
    except (CategoryNotFoundError, DistrictNotFoundError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from None


@router.post(
    "/batch",
    response_model=list[DoctorDetail],
    status_code=status.HTTP_201_CREATED,
)
def create_doctors_batch(
    payload: list[DoctorCreate], service: PractitionerService = Depends(get_service)
) -> list[DoctorDetail]:
    """Create multiple doctors in one transaction."""
    try:
        return service.create_doctors_batch(payload)
    except (CategoryNotFoundError, DistrictNotFoundError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from None
