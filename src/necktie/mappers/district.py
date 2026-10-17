"""Mappers between District ORM models and API schemas."""

from necktie.models import District
from necktie.schemas import District as DistrictSchema


def to_district(d: District, language: str) -> DistrictSchema:
    """Serialize a district to a localized schema.

    Translations are pre-filtered to ``language`` by the query, so the first
    translation is the localized one.
    """
    t = d.translations[0] if d.translations else None
    return DistrictSchema(id=d.id, sort_order=d.sort_order, name=t.name if t else "")
