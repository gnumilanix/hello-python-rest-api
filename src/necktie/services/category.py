"""Business logic for categories."""

from pydantic import TypeAdapter

from necktie.cache.catalogs import CatalogStore
from necktie.mappers import (
    CategoryCatalogEntry,
    to_category,
    to_category_catalog_entry,
)
from necktie.repositories.category import CategoryRepository
from necktie.schemas import Category as CategorySchema
from necktie.utils.languages import Language


class CategoryService:
    """Coordinates category repository access, caching, and mapping."""

    def __init__(self, repository: CategoryRepository) -> None:
        self.repo = repository
        self.catalog = CatalogStore(
            key="necktie:catalog:categories",
            adapter=TypeAdapter(list[CategoryCatalogEntry]),
            load=self._load,
        )

    async def _load(self) -> list[CategoryCatalogEntry]:
        """Load all categories from the DB for the catalog."""
        return [to_category_catalog_entry(c) for c in await self.repo.find_all()]

    async def list_categories(self, language: Language) -> list[CategorySchema]:
        """List categories localized to ``language``."""
        return [to_category(e, language) for e in await self.catalog.get()]

    async def get_translated_map(self) -> dict[int, CategoryCatalogEntry]:
        """Return the category catalog keyed by id for cross-aggregate use."""
        return {e.id: e for e in await self.catalog.get()}

    async def exists(self, category_id: int) -> bool:
        """Whether the category id is present in the cached catalog."""
        return category_id in await self.get_translated_map()
