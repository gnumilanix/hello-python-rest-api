"""Payload for creating a doctor."""

from pydantic import BaseModel, Field

from necktie.schemas.doctor_translation_in import DoctorTranslationIn
from necktie.schemas.opening_hour_in import OpeningHourIn


class DoctorCreate(BaseModel):
    """Payload for creating a doctor."""

    category_id: int
    district_id: int
    place_id: str | None = None
    phone_numbers: list[str] = Field(default_factory=list)
    member_exclusive_fee: int | None = None
    consultation_fee: int | None = None
    is_open_on_public_holidays: bool = False
    translations: list[DoctorTranslationIn] = Field(min_length=1)
    opening_hours: list[OpeningHourIn] = Field(default_factory=list)
