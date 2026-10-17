"""Pydantic schemas for the doctor endpoints, one class per module."""

from necktie.schemas.category_ref import CategoryRef
from necktie.schemas.category_translated import CategoryTranslated
from necktie.schemas.district_ref import DistrictRef
from necktie.schemas.district_translated import DistrictTranslated
from necktie.schemas.doctor_create import DoctorCreate
from necktie.schemas.doctor_detail import DoctorDetail
from necktie.schemas.doctor_list_item import DoctorListItem
from necktie.schemas.doctor_translation_in import DoctorTranslationIn
from necktie.schemas.opening_hour_detail import OpeningHourDetail
from necktie.schemas.opening_hour_in import OpeningHourIn
from necktie.schemas.opening_hour_list_item import OpeningHourListItem

__all__ = [
    "CategoryRef",
    "CategoryTranslated",
    "DistrictRef",
    "DistrictTranslated",
    "DoctorCreate",
    "DoctorDetail",
    "DoctorListItem",
    "DoctorTranslationIn",
    "OpeningHourDetail",
    "OpeningHourIn",
    "OpeningHourListItem",
]
