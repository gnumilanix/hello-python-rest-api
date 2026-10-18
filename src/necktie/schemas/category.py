"""Category API schemas, grouped per domain."""

from pydantic import BaseModel


class CategoryBase(BaseModel):
    """Shared category fields."""

    name_key: str


class Category(CategoryBase):
    """Category with a single localized name."""

    id: int
    name: str


class CategoryNames(BaseModel):
    """Category names in every supported language."""

    en: str
    yue: str
    zh: str


class CategoryRef(BaseModel):
    """Category reference with a single localized name (nested in responses)."""

    id: int
    name: str


class CategoryTranslated(BaseModel):
    """Category reference with all translations."""

    id: int
    name: CategoryNames
