"""Doctor API schemas, grouped per domain."""

from pydantic import BaseModel, Field

from necktie.schemas.category import CategoryRef
from necktie.schemas.district import DistrictRef
from necktie.schemas.locale import LocaleModel, NullableLocaleModel
from necktie.schemas.operating_hour import (
    OperatingHour,
    OperatingHourCreate,
)
from necktie.utils import DefaultPhoneList


class DoctorBase(BaseModel):
    """Shared doctor fields."""

    place_id: str | None = None
    phone_numbers: list[str] = Field(min_length=1)
    member_exclusive_fee: int | None = None
    consultation_fee: int
    is_open_on_public_holidays: bool = False


class Doctor(DoctorBase):
    """Doctor localized to the requested language."""

    id: int
    category: CategoryRef
    district: DistrictRef
    name: str
    address: str
    fee_detail: str | None
    operating_hours: list[OperatingHour]


class DoctorCreate(DoctorBase):
    """Payload for creating a doctor."""

    category_id: int
    district_id: int
    phone_numbers: DefaultPhoneList
    name: LocaleModel
    address: LocaleModel
    fee_detail: NullableLocaleModel = Field(
        default_factory=NullableLocaleModel
    )
    operating_hours: list[OperatingHourCreate] = Field(default_factory=list)
