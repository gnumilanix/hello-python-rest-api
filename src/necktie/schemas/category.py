"""Category API schemas, grouped per domain."""

from pydantic import BaseModel, Field

from necktie.schemas.locale import LocaleModel


class CategoryBase(BaseModel):
    """Shared category fields."""

    name_key: str


class Category(CategoryBase):
    """Category with a single localized name."""

    id: int
    name: str


class CategoryNames(LocaleModel):
    """Category names, capped to the VARCHAR(255) columns."""

    en: str = Field(min_length=1, max_length=255)
    yue: str = Field(min_length=1, max_length=255)
    zh: str = Field(min_length=1, max_length=255)


class CategoryRef(BaseModel):
    """Category reference with a single localized name (nested in responses)."""

    id: int
    name: str


class CategoryTranslated(BaseModel):
    """Category reference with all translations."""

    id: int
    name: CategoryNames
