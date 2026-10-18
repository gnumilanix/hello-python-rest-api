"""Doctor API schemas, grouped per domain."""

from pydantic import BaseModel, Field

from necktie.schemas.category import CategoryRef, CategoryTranslated
from necktie.schemas.district import DistrictRef, DistrictTranslated
from necktie.schemas.operating_hour import (
    OperatingHour,
    OperatingHourCreate,
    OperatingHourDetail,
)
from necktie.utils import DefaultPhoneList


class DoctorText(BaseModel):
    """Required translatable text: every supported language present."""

    en: str
    yue: str
    zh: str


class DoctorTextOptional(BaseModel):
    """Optional translatable text (e.g. fee_detail): every field may be absent."""

    en: str | None = None
    yue: str | None = None
    zh: str | None = None


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


class DoctorDetail(DoctorBase):
    """Full doctor record with every translation."""

    id: int
    category: CategoryTranslated
    district: DistrictTranslated
    name: DoctorText
    address: DoctorText
    fee_detail: DoctorTextOptional
    operating_hours: list[OperatingHourDetail]


class DoctorCreate(DoctorBase):
    """Payload for creating a doctor."""

    category_id: int
    district_id: int
    phone_numbers: DefaultPhoneList
    name: DoctorText
    address: DoctorText
    fee_detail: DoctorTextOptional = Field(default_factory=DoctorTextOptional)
    operating_hours: list[OperatingHourCreate] = Field(default_factory=list)
