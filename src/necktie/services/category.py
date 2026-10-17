"""Business logic for categories."""

from necktie.mappers import to_category
from necktie.repositories.category import CategoryRepository
from necktie.schemas import Category as CategorySchema
from necktie.utils import cache


class CategoryService:
    """Coordinates category repository access and mapping."""

    def __init__(self, repository: CategoryRepository) -> None:
        self.repo = repository

    def list_categories(self, language: str) -> list[CategorySchema]:
        """List categories localized to ``language`` (cached)."""
        key = cache.build_key("categories", {"language": language})
        return cache.get_or_fetch(
            key,
            lambda: [to_category(c) for c in self.repo.find_all_localized(language)],
            decode=lambda data: [CategorySchema.model_validate(c) for c in data],
        )
