"""District API schemas, grouped per domain."""

from pydantic import BaseModel, Field

from necktie.schemas.locale import LocaleModel


class DistrictBase(BaseModel):
    """Shared district fields."""

    sort_order: int


class District(DistrictBase):
    """District with a single localized name."""

    id: int
    name: str


class DistrictNames(LocaleModel):
    """District names, capped to the VARCHAR(255) columns."""

    en: str = Field(min_length=1, max_length=255)
    yue: str = Field(min_length=1, max_length=255)
    zh: str = Field(min_length=1, max_length=255)


class DistrictRef(BaseModel):
    """District reference with a single localized name (nested in responses)."""

    id: int
    name: str


class DistrictTranslated(BaseModel):
    """District reference with all translations."""

    id: int
    name: DistrictNames
