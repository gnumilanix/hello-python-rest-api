"""Mappers between Category ORM models and API schemas."""

from pydantic import BaseModel

from necktie.models import Category
from necktie.schemas import Category as CategorySchema
from necktie.utils.constants import DEFAULT_LANGUAGE


class CategoryCatalogEntry(BaseModel):
    """Category with all translations, as cached in Redis."""

    id: int
    name_key: str
    name: dict[str, str]


def to_category_catalog_entry(c: Category) -> CategoryCatalogEntry:
    """Serialize a category with every translation for the Redis catalog."""
    return CategoryCatalogEntry(
        id=c.id,
        name_key=c.name_key,
        name={t.language_code: t.name for t in c.translations},
    )


def to_category(entry: CategoryCatalogEntry, language: str) -> CategorySchema:
    """Serialize a catalog entry localized to ``language``."""
    name = entry.name.get(language) or entry.name.get(DEFAULT_LANGUAGE, "")
    return CategorySchema(id=entry.id, name_key=entry.name_key, name=name)
