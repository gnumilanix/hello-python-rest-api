"""Mappers between District ORM models and API schemas."""

from pydantic import BaseModel

from necktie.models import District
from necktie.schemas import District as DistrictSchema
from necktie.utils.constants import DEFAULT_LANGUAGE


class DistrictCatalogEntry(BaseModel):
    """District with all translations, as cached in Redis."""

    id: int
    sort_order: int
    name: dict[str, str]


def to_district_catalog_entry(d: District) -> DistrictCatalogEntry:
    """Serialize a district with every translation for the Redis catalog."""
    return DistrictCatalogEntry(
        id=d.id,
        sort_order=d.sort_order,
        name={t.language_code: t.name for t in d.translations},
    )


def to_district(entry: DistrictCatalogEntry, language: str) -> DistrictSchema:
    """Serialize a catalog entry localized to ``language``."""
    name = entry.name.get(language) or entry.name.get(DEFAULT_LANGUAGE, "")
    return DistrictSchema(id=entry.id, sort_order=entry.sort_order, name=name)
