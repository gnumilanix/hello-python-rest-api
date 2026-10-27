"""Doctor endpoints.

The resource is exposed as ``/doctor`` while the underlying table is
``doctors``. Routes delegate to the service layer; this module only
handles HTTP concerns (params, status codes, error mapping).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

from necktie.routers.deps import get_doctor_service
from necktie.schemas import Doctor, DoctorCreate
from necktie.schemas.doctor import DoctorPatch
from necktie.services import (
    CategoryNotFoundError,
    DistrictNotFoundError,
    DoctorNotFoundError,
    DoctorService,
)
from necktie.utils.languages import Language

router = APIRouter(prefix="/doctor", tags=["doctor"])


@router.get("", response_model=list[Doctor])
@cache(namespace="doctor")
async def list_doctors(
    language: Language = Query(Language.default(), description="Response language"),
    district: int | None = Query(None, description="District id"),
    category: int | None = Query(None, description="Category id"),
    min_fee: int | None = Query(None, ge=0, description="Min consultation fee"),
    max_fee: int | None = Query(None, ge=0, description="Max consultation fee"),
    page: int = Query(0, ge=0, description="Page number (0-based)"),
    size: int = Query(20, ge=10, le=100, description="Page size (10-100)"),
    service: DoctorService = Depends(get_doctor_service),
) -> list[Doctor]:
    """List doctors localized to ``language``, filterable and paginated."""
    return await service.list_doctors(
        language=language,
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
    language: Language = Query(Language.default(), description="Response language"),
    service: DoctorService = Depends(get_doctor_service),
) -> Doctor:
    """Get one doctor localized to ``language``."""
    try:
        return await service.get_doctor(doctor_id, language=language)
    except DoctorNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Doctor not found") from None


@router.post("", response_model=Doctor, status_code=status.HTTP_201_CREATED)
async def create_doctor(
    payload: DoctorCreate, service: DoctorService = Depends(get_doctor_service)
) -> Doctor:
    """Create a single doctor."""
    try:
        result = await service.create_doctor(payload)
    except (CategoryNotFoundError, DistrictNotFoundError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from None
    await FastAPICache.clear(namespace="doctor")
    return result


@router.put("/{doctor_id}")
async def replace_doctor(
    doctor_id: int,
    payload: DoctorCreate,
    service: Annotated[DoctorService, Depends(get_doctor_service)],
) -> Doctor:
    """Replace an existing listing; omitted optional fields reset to defaults."""
    try:
        result = await service.update_doctor(doctor_id, payload)
    except DoctorNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Doctor not found") from None
    except (CategoryNotFoundError, DistrictNotFoundError) as error:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from None
    await FastAPICache.clear(namespace="doctor")
    return result


@router.patch("/{doctor_id}")
async def patch_doctor(
    doctor_id: int,
    payload: DoctorPatch,
    service: Annotated[DoctorService, Depends(get_doctor_service)],
) -> Doctor:
    """Update supplied fields and translations of an existing listing."""
    try:
        result = await service.update_doctor(doctor_id, payload)
    except DoctorNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Doctor not found") from None
    except (CategoryNotFoundError, DistrictNotFoundError) as error:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from None
    await FastAPICache.clear(namespace="doctor")
    return result


@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_doctor(
    doctor_id: int,
    service: Annotated[DoctorService, Depends(get_doctor_service)],
) -> Response:
    """Delete an existing listing and its hours."""
    try:
        await service.delete_doctor(doctor_id)
    except DoctorNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Doctor not found") from None
    await FastAPICache.clear(namespace="doctor")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/batch",
    response_model=list[Doctor],
    status_code=status.HTTP_201_CREATED,
)
async def create_doctors_batch(
    payload: list[DoctorCreate],
    service: DoctorService = Depends(get_doctor_service),
) -> list[Doctor]:
    """Create multiple doctors in one transaction."""
    try:
        result = await service.create_doctors_batch(payload)
    except (CategoryNotFoundError, DistrictNotFoundError) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from None
    await FastAPICache.clear(namespace="doctor")
    return result
