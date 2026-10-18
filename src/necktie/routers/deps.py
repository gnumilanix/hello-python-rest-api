"""Dependencies for the routers package."""

from fastapi import Depends
from sqlmodel import Session

from necktie.db.session import get_db
from necktie.repositories import (
    CategoryRepository,
    DistrictRepository,
    DoctorRepository,
)
from necktie.services import DoctorService
from necktie.services.category import CategoryService
from necktie.services.district import DistrictService


def get_district_service(db: Session = Depends(get_db)) -> DistrictService:
    """Build the district service with its repository."""
    return DistrictService(DistrictRepository(db))


def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    """Build the category service with its repository."""
    return CategoryService(CategoryRepository(db))


def get_doctor_service(
    db: Session = Depends(get_db),
    districts: DistrictService = Depends(get_district_service),
    categories: CategoryService = Depends(get_category_service),
) -> DoctorService:
    """Build the doctor service with its repository and catalog services."""
    return DoctorService(DoctorRepository(db), districts, categories)
