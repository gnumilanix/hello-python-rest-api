"""Mappers between District ORM models and API schemas."""

from necktie.mappers.translation import pick_translation
from necktie.models import District
from necktie.schemas import District as DistrictSchema


def to_district(d: District, language: str) -> DistrictSchema:
    """Serialize a district to a localized schema."""
    t = pick_translation(d.translations, language)
    return DistrictSchema(
        id=d.id, sort_order=d.sort_order, name=t.name if t else ""
    )
