"""Doctor API schemas, grouped per domain."""

from pydantic import BaseModel, Field

from necktie.schemas.category import CategoryRef
from necktie.schemas.district import DistrictRef
from necktie.schemas.locale import LocaleModel, NullableLocaleModel
from necktie.schemas.operating_hour import (
    OperatingHour,
    OperatingHourInput,
)
from necktie.utils import DefaultPhoneList


class DoctorBase(BaseModel):
    """Shared doctor fields."""

    place_id: str | None = Field(default=None, max_length=255)
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


class DoctorNameInput(LocaleModel):
    """A doctor's name, capped to the VARCHAR(255) columns."""

    en: str = Field(min_length=1, max_length=255)
    yue: str = Field(min_length=1, max_length=255)
    zh: str = Field(min_length=1, max_length=255)


class DoctorAddressInput(LocaleModel):
    """A doctor's address in every supported language (TEXT columns, uncapped)."""


class DoctorFeeDetailInput(NullableLocaleModel):
    """A doctor's fee detail in any supported language (TEXT columns, uncapped)."""


class DoctorCreate(DoctorBase):
    """Payload for creating a doctor."""

    category_id: int
    district_id: int
    phone_numbers: DefaultPhoneList
    name: DoctorNameInput
    address: DoctorAddressInput
    fee_detail: DoctorFeeDetailInput = Field(default_factory=DoctorFeeDetailInput)
    operating_hours: list[OperatingHourInput] = Field(default_factory=list)
