"""Pydantic schemas grouped per domain model."""

from necktie.schemas.category import (
    Category,
    CategoryBase,
    CategoryRef,
    CategoryTranslated,
)
from necktie.schemas.district import (
    District,
    DistrictBase,
    DistrictRef,
    DistrictTranslated,
)
from necktie.schemas.doctor import (
    Doctor,
    DoctorBase,
    DoctorCreate,
)
from necktie.schemas.operating_hour import (
    OperatingHour,
    OperatingHourBase,
    OperatingHourInput,
)

__all__ = [
    "Category",
    "CategoryBase",
    "CategoryRef",
    "CategoryTranslated",
    "District",
    "DistrictBase",
    "DistrictRef",
    "DistrictTranslated",
    "Doctor",
    "DoctorBase",
    "DoctorCreate",
    "OperatingHour",
    "OperatingHourBase",
    "OperatingHourInput",
]
