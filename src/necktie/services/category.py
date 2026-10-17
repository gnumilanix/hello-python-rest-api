"""Business logic for categories."""

from necktie.mappers.translation import pick_translation
from necktie.repositories.category import CategoryRepository
from necktie.schemas import Category as CategorySchema


class CategoryService:
    """Coordinates category repository access and mapping."""

    def __init__(self, repository: CategoryRepository) -> None:
        self.repo = repository

    def list_categories(self, language: str = "en-US") -> list[CategorySchema]:
        """List categories localized to ``language``."""
        items = []
        for c in self.repo.find_all():
            t = pick_translation(c.translations, language)
            items.append(
                CategorySchema(id=c.id, name_key=c.name_key, name=t.name if t else "")
            )
        return items
