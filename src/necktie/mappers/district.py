"""Mappers between District ORM models and API schemas."""

from pydantic import BaseModel

from necktie.models import District
from necktie.schemas import District as DistrictSchema
from necktie.schemas.locale import LocaleModel
from necktie.utils.languages import Language


class DistrictCatalogEntry(BaseModel):
    """District with all translations, as cached in Redis."""

    id: int
    sort_order: int
    name_en: str
    name_yue: str
    name_zh: str

    def names(self) -> LocaleModel:
        """The names as an API schema object."""
        return LocaleModel(en=self.name_en, yue=self.name_yue, zh=self.name_zh)


def to_district_catalog_entry(d: District) -> DistrictCatalogEntry:
    """Serialize a district with every translation for the Redis catalog."""
    return DistrictCatalogEntry(
        id=d.id,
        sort_order=d.sort_order,
        name_en=d.name_en,
        name_yue=d.name_yue,
        name_zh=d.name_zh,
    )


def _pick(entry: DistrictCatalogEntry, language: Language) -> str:
    """Pick the name for ``language``."""
    if language is Language.YUE:
        return entry.name_yue
    if language is Language.ZH:
        return entry.name_zh
    return entry.name_en


def to_district(entry: DistrictCatalogEntry, language: Language) -> DistrictSchema:
    """Serialize a catalog entry localized to ``language``."""
    return DistrictSchema(
        id=entry.id, sort_order=entry.sort_order, name=_pick(entry, language)
    )
