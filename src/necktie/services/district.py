"""Business logic for districts."""

from pydantic import TypeAdapter

from necktie.cache.catalogs import CatalogStore
from necktie.mappers import (
    DistrictCatalogEntry,
    to_district,
    to_district_catalog_entry,
)
from necktie.repositories.district import DistrictRepository
from necktie.schemas import District as DistrictSchema
from necktie.utils.languages import Language


class DistrictService:
    """Coordinates district repository access, caching, and mapping."""

    def __init__(self, repository: DistrictRepository) -> None:
        self.repo = repository
        self.catalog = CatalogStore(
            key="necktie:catalog:districts",
            adapter=TypeAdapter(list[DistrictCatalogEntry]),
            load=lambda: [to_district_catalog_entry(d) for d in self.repo.find_all()],
        )

    async def list_districts(self, language: Language) -> list[DistrictSchema]:
        """List districts localized to ``language``, ordered by sort_order."""
        return [to_district(e, language) for e in await self.catalog.get()]

    async def get_translated_map(self) -> dict[int, DistrictCatalogEntry]:
        """Return the district catalog keyed by id for cross-aggregate use."""
        return {e.id: e for e in await self.catalog.get()}

    async def exists(self, district_id: int) -> bool:
        """Whether the district id is present in the cached catalog."""
        return district_id in await self.get_translated_map()
