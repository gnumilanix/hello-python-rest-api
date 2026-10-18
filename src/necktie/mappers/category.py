"""Mappers between Category ORM models and API schemas."""

from pydantic import BaseModel

from necktie.models import Category
from necktie.schemas import Category as CategorySchema
from necktie.schemas.category import CategoryNames
from necktie.utils.languages import Language


class CategoryCatalogEntry(BaseModel):
    """Category with all translations, as cached in Redis."""

    id: int
    name_key: str
    name_en: str
    name_yue: str
    name_zh: str

    def names(self) -> CategoryNames:
        """The names as an API schema object."""
        return CategoryNames(en=self.name_en, yue=self.name_yue, zh=self.name_zh)


def to_category_catalog_entry(c: Category) -> CategoryCatalogEntry:
    """Serialize a category with every translation for the Redis catalog."""
    return CategoryCatalogEntry(
        id=c.id,
        name_key=c.name_key,
        name_en=c.name_en,
        name_yue=c.name_yue,
        name_zh=c.name_zh,
    )


def _pick(entry: CategoryCatalogEntry, language: Language) -> str:
    """Pick the name for ``language``."""
    if language is Language.YUE:
        return entry.name_yue
    if language is Language.ZH:
        return entry.name_zh
    return entry.name_en


def to_category(entry: CategoryCatalogEntry, language: Language) -> CategorySchema:
    """Serialize a catalog entry localized to ``language``."""
    return CategorySchema(
        id=entry.id, name_key=entry.name_key, name=_pick(entry, language)
    )
