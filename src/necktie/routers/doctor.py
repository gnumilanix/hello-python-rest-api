"""Doctor endpoints.

The resource is exposed as ``/doctor`` while the underlying table is
``practitioners``. Routes delegate to the service layer; this module only
handles HTTP concerns (params, status codes, error mapping).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

from necktie.routers.deps import get_doctor_service
from necktie.schemas import Doctor, DoctorCreate, DoctorDetail
from necktie.services import (
    CategoryNotFoundError,
    DistrictNotFoundError,
    PractitionerNotFoundError,
    PractitionerService,
)
from necktie.utils.constants import DEFAULT_LANGUAGE

router = APIRouter(prefix="/doctor", tags=["doctor"])


@router.get("", response_model=list[DoctorDetail])
@cache(namespace="doctor")
async def list_doctors(
    district: int | None = Query(None, description="District id"),
    category: int | None = Query(None, description="Category id"),
    min_fee: int | None = Query(None, ge=0, description="Min consultation fee"),
    max_fee: int | None = Query(None, ge=0, description="Max consultation fee"),
    page: int = Query(0, ge=0, description="Page number (0-based)"),
    size: int = Query(20, ge=10, le=100, description="Page size (10-100)"),
    service: PractitionerService = Depends(get_doctor_service),
) -> list[DoctorDetail]:
    """List doctors with all translations, filterable and paginated."""
    return await service.list_doctors(
        district_id=district,
        category_id=category,
        min_fee=min_fee,
        max_fee=max_fee,
        offset=page * size,
        limit=size,
    )


@router.get("/{doctor_id}", response_model=Doctor)
@cache(namespace="doctor")
async def get_doctor(
    doctor_id: int,
    language: str = Query(DEFAULT_LANGUAGE, description="Response language"),
    service: PractitionerService = Depends(get_doctor_service),
) -> Doctor:
    """Get one doctor localized to ``language``."""
    try:
        return await service.get_doctor(doctor_id, language=language)
    except PractitionerNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Doctor not found") from None


@router.post("", response_model=DoctorDetail, status_code=status.HTTP_201_CREATED)
async def create_doctor(
    payload: DoctorCreate, service: PractitionerService = Depends(get_doctor_service)
) -> DoctorDetail:
    """Create a single doctor."""
    try:
        result = await service.create_doctor(payload)
    except (CategoryNotFoundError, DistrictNotFoundError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from None
    await FastAPICache.clear(namespace="doctor")
    return result


@router.post(
    "/batch",
    response_model=list[DoctorDetail],
    status_code=status.HTTP_201_CREATED,
)
async def create_doctors_batch(
    payload: list[DoctorCreate],
    service: PractitionerService = Depends(get_doctor_service),
) -> list[DoctorDetail]:
    """Create multiple doctors in one transaction."""
    try:
        result = await service.create_doctors_batch(payload)
    except (CategoryNotFoundError, DistrictNotFoundError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from None
    await FastAPICache.clear(namespace="doctor")
    return result
