"""Localized doctor response schema."""

from pydantic import BaseModel

from necktie.schemas.category_ref import CategoryRef
from necktie.schemas.district_ref import DistrictRef
from necktie.schemas.operating_hour import OperatingHour


class Doctor(BaseModel):
    """Doctor localized to the requested language."""

    id: int
    category: CategoryRef
    district: DistrictRef
    name: str
    address: str
    fee_detail: str | None
    place_id: str | None
    phone_numbers: list[str]
    member_exclusive_fee: int | None
    consultation_fee: int | None
    is_open_on_public_holidays: bool
    operating_hours: list[OperatingHour]
