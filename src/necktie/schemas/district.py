"""District API schemas, grouped per domain."""

from pydantic import BaseModel


class DistrictBase(BaseModel):
    """Shared district fields."""

    sort_order: int


class District(DistrictBase):
    """District with a single localized name."""

    id: int
    name: str


class DistrictNames(BaseModel):
    """District names in every supported language."""

    en: str
    yue: str
    zh: str


class DistrictRef(BaseModel):
    """District reference with a single localized name (nested in responses)."""

    id: int
    name: str


class DistrictTranslated(BaseModel):
    """District reference with all translations."""

    id: int
    name: DistrictNames
