"""Translations supplied when creating a doctor."""

from pydantic import BaseModel, Field


class DoctorTranslationIn(BaseModel):
    """Translations supplied when creating a doctor."""

    language_code: str = Field(min_length=2, max_length=10)
    name: str
    address: str
    fee_detail: str | None = None
