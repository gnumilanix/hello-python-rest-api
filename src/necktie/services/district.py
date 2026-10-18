"""Business logic for districts."""

from fastapi_cache import FastAPICache
from pydantic import TypeAdapter
from starlette.concurrency import run_in_threadpool

from necktie.cache.lifespan import CACHE_TTL_SECONDS
from necktie.mappers import (
    DistrictCatalogEntry,
    to_district,
    to_district_catalog_entry,
)
from necktie.repositories.district import DistrictRepository
from necktie.schemas import District as DistrictSchema

_CATALOG_ADAPTER = TypeAdapter(list[DistrictCatalogEntry])


class DistrictService:
    """Coordinates district repository access, caching, and mapping."""

    CATALOG_KEY = "necktie:catalog:districts"

    def __init__(self, repository: DistrictRepository) -> None:
        self.repo = repository

    async def list_districts(self, language: str) -> list[DistrictSchema]:
        """List districts localized to ``language``, ordered by sort_order."""
        return [to_district(e, language) for e in await self._get_catalog()]

    async def get_translated_map(self) -> dict[int, DistrictCatalogEntry]:
        """Return the district catalog keyed by id for cross-aggregate use."""
        return {e.id: e for e in await self._get_catalog()}

    async def _get_catalog(self) -> list[DistrictCatalogEntry]:
        """Load the catalog from Redis, populating it from the DB on a miss."""
        backend = FastAPICache.get_backend()
        cached = await backend.get(self.CATALOG_KEY)
        if cached is not None:
            return _CATALOG_ADAPTER.validate_json(cached)
        districts = await run_in_threadpool(self.repo.find_all)
        entries = [to_district_catalog_entry(d) for d in districts]
        await backend.set(
            self.CATALOG_KEY,
            _CATALOG_ADAPTER.dump_json(entries),
            expire=CACHE_TTL_SECONDS,
        )
        return entries
