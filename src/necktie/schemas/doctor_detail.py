"""Full doctor record with every translation."""

from pydantic import BaseModel

from necktie.schemas.category_translated import CategoryTranslated
from necktie.schemas.district_translated import DistrictTranslated
from necktie.schemas.opening_hour_detail import OpeningHourDetail


class DoctorDetail(BaseModel):
    """Full doctor record with every translation."""

    id: int
    category: CategoryTranslated
    district: DistrictTranslated
    name: dict[str, str]
    address: dict[str, str]
    fee_detail: dict[str, str | None]
    place_id: str | None
    phone_numbers: list[str]
    member_exclusive_fee: int | None
    consultation_fee: int | None
    is_open_on_public_holidays: bool
    opening_hours: list[OpeningHourDetail]
