"""Mappers between Category ORM models and API schemas."""

from necktie.mappers.translation import pick_translation
from necktie.models import Category
from necktie.schemas import Category as CategorySchema


def to_category(c: Category, language: str) -> CategorySchema:
    """Serialize a category to a localized schema."""
    t = pick_translation(c.translations, language)
    return CategorySchema(id=c.id, name_key=c.name_key, name=t.name if t else "")
