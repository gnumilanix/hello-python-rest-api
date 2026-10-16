"""Pydantic schemas for the doctor endpoints."""

from datetime import time

from pydantic import BaseModel, Field


class CategoryRef(BaseModel):
    """Category reference with a single localized name."""

    id: int
    name: str


class DistrictRef(BaseModel):
    """District reference with a single localized name."""

    id: int
    name: str


class OpeningHourListItem(BaseModel):
    """Opening hour entry in list responses (day name)."""

    day_of_week: str
    open_time: time
    close_time: time


class DoctorListItem(BaseModel):
    """Doctor listing localized to the requested language."""

    id: int
    category: CategoryRef
    district: DistrictRef
    address: str
    place_id: str | None
    phone_numbers: list[str]
    is_active: bool
    member_exclusive_fee: int | None
    consultation_fee: int | None
    is_open_on_public_holidays: bool
    opening_hours: list[OpeningHourListItem]


class CategoryTranslated(BaseModel):
    """Category reference with all translations."""

    id: int
    name: dict[str, str]


class DistrictTranslated(BaseModel):
    """District reference with all translations."""

    id: int
    name: dict[str, str]


class OpeningHourDetail(BaseModel):
    """Opening hour entry in detail responses (ISO day number)."""

    day_of_week: int
    open_time: time
    close_time: time


class DoctorDetail(BaseModel):
    """Full doctor record with every translation."""

    id: int
    category: CategoryTranslated
    district: DistrictTranslated
    address: dict[str, str]
    place_id: str | None
    phone_numbers: list[str]
    is_active: bool
    member_exclusive_fee: int | None
    consultation_fee: int | None
    is_open_on_public_holidays: bool
    opening_hours: list[OpeningHourDetail]


class DoctorTranslationIn(BaseModel):
    """Translations supplied when creating a doctor."""

    language_code: str = Field(min_length=2, max_length=10)
    name: str
    address: str
    fee_detail: str | None = None


class OpeningHourIn(BaseModel):
    """Opening hour supplied when creating a doctor."""

    day_of_week: int = Field(ge=1, le=7, description="ISO day: 1=Mon, 7=Sun")
    open_time: time
    close_time: time


class DoctorCreate(BaseModel):
    """Payload for creating a doctor."""

    category_id: int
    district_id: int
    place_id: str | None = None
    phone_numbers: list[str] = Field(default_factory=list)
    is_active: bool = True
    member_exclusive_fee: int | None = None
    consultation_fee: int | None = None
    is_open_on_public_holidays: bool = False
    translations: list[DoctorTranslationIn] = Field(min_length=1)
    opening_hours: list[OpeningHourIn] = Field(default_factory=list)
