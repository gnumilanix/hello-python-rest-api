"""Doctor API schemas, grouped per domain."""

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

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


class DoctorAddressPatch(NullableLocaleModel):
    """Change supplied translations without clearing required text."""

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def reject_null_translations(self) -> Self:
        for language in self.model_fields_set:
            if getattr(self, language) is None:
                raise ValueError(f"{language} cannot be null")
        return self


class DoctorNamePatch(DoctorAddressPatch):
    """Partial name translations, capped to the database column length."""

    en: str | None = Field(default=None, min_length=1, max_length=255)
    yue: str | None = Field(default=None, min_length=1, max_length=255)
    zh: str | None = Field(default=None, min_length=1, max_length=255)


class DoctorPatch(BaseModel):
    """Only supplied fields change; hours and phone lists are replaced."""

    model_config = ConfigDict(extra="forbid")

    category_id: int | None = None
    district_id: int | None = None
    place_id: str | None = Field(default=None, max_length=255)
    phone_numbers: DefaultPhoneList | None = None
    member_exclusive_fee: int | None = None
    consultation_fee: int | None = None
    is_open_on_public_holidays: bool | None = None
    name: DoctorNamePatch | None = None
    address: DoctorAddressPatch | None = None
    fee_detail: DoctorFeeDetailInput | None = None
    operating_hours: list[OperatingHourInput] | None = None

    @model_validator(mode="after")
    def reject_null_required_fields(self) -> Self:
        nullable = {"place_id", "member_exclusive_fee", "fee_detail"}
        for field in self.model_fields_set - nullable:
            if getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self
