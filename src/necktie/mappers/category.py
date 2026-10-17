"""Mappers between Category ORM models and API schemas."""

from necktie.models import Category
from necktie.schemas import Category as CategorySchema


def to_category(c: Category, language: str) -> CategorySchema:
    """Serialize a category to a localized schema.

    Translations are pre-filtered to ``language`` by the query, so the first
    translation is the localized one.
    """
    t = c.translations[0] if c.translations else None
    return CategorySchema(id=c.id, name_key=c.name_key, name=t.name if t else "")
