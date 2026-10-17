"""Business logic for categories."""

from necktie.mappers import to_category
from necktie.repositories.category import CategoryRepository
from necktie.schemas import Category as CategorySchema


class CategoryService:
    """Coordinates category repository access and mapping."""

    def __init__(self, repository: CategoryRepository) -> None:
        self.repo = repository

    def list_categories(self, language: str) -> list[CategorySchema]:
        """List categories localized to ``language``."""
        return [
            to_category(c) for c in self.repo.find_all_localized(language)
        ]
