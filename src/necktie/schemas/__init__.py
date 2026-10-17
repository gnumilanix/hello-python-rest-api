"""Pydantic schemas for the doctor endpoints, one class per module."""

from necktie.schemas.category import Category
from necktie.schemas.category_ref import CategoryRef
from necktie.schemas.category_translated import CategoryTranslated
from necktie.schemas.district import District
from necktie.schemas.district_ref import DistrictRef
from necktie.schemas.district_translated import DistrictTranslated
from necktie.schemas.doctor import Doctor
from necktie.schemas.doctor_create import DoctorCreate
from necktie.schemas.doctor_detail import DoctorDetail
from necktie.schemas.doctor_translation_in import DoctorTranslationIn
from necktie.schemas.operating_hour import OperatingHour
from necktie.schemas.operating_hour_detail import OperatingHourDetail
from necktie.schemas.operating_hour_in import OperatingHourIn

__all__ = [
    "Category",
    "CategoryRef",
    "CategoryTranslated",
    "District",
    "DistrictRef",
    "DistrictTranslated",
    "Doctor",
    "DoctorCreate",
    "DoctorDetail",
    "DoctorTranslationIn",
    "OperatingHour",
    "OperatingHourDetail",
    "OperatingHourIn",
]
