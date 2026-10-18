"""Business logic for categories."""

from fastapi_cache import FastAPICache
from pydantic import TypeAdapter
from starlette.concurrency import run_in_threadpool

from necktie.cache.lifespan import CACHE_TTL_SECONDS
from necktie.mappers import (
    CategoryCatalogEntry,
    to_category,
    to_category_catalog_entry,
)
from necktie.repositories.category import CategoryRepository
from necktie.schemas import Category as CategorySchema

_CATALOG_ADAPTER = TypeAdapter(list[CategoryCatalogEntry])


class CategoryService:
    """Coordinates category repository access, caching, and mapping."""

    CATALOG_KEY = "necktie:catalog:categories"

    def __init__(self, repository: CategoryRepository) -> None:
        self.repo = repository

    async def list_categories(self, language: str) -> list[CategorySchema]:
        """List categories localized to ``language``."""
        return [to_category(e, language) for e in await self._get_catalog()]

    async def get_translated_map(self) -> dict[int, CategoryCatalogEntry]:
        """Return the category catalog keyed by id for cross-aggregate use."""
        return {e.id: e for e in await self._get_catalog()}

    async def _get_catalog(self) -> list[CategoryCatalogEntry]:
        """Load the catalog from Redis, populating it from the DB on a miss."""
        backend = FastAPICache.get_backend()
        cached = await backend.get(self.CATALOG_KEY)
        if cached is not None:
            return _CATALOG_ADAPTER.validate_json(cached)
        categories = await run_in_threadpool(self.repo.find_all)
        entries = [to_category_catalog_entry(c) for c in categories]
        await backend.set(
            self.CATALOG_KEY,
            _CATALOG_ADAPTER.dump_json(entries),
            expire=CACHE_TTL_SECONDS,
        )
        return entries
