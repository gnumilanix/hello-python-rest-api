"""Doctor listing localized to the requested language."""

from pydantic import BaseModel

from necktie.schemas.category_ref import CategoryRef
from necktie.schemas.district_ref import DistrictRef
from necktie.schemas.opening_hour_list_item import OpeningHourListItem


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
