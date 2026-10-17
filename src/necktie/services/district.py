"""Business logic for districts."""

from necktie.mappers.translation import pick_translation
from necktie.repositories.district import DistrictRepository
from necktie.schemas import District as DistrictSchema


class DistrictService:
    """Coordinates district repository access and mapping."""

    def __init__(self, repository: DistrictRepository) -> None:
        self.repo = repository

    def list_districts(self, language: str) -> list[DistrictSchema]:
        """List districts localized to ``language``, ordered by sort_order."""
        items = []
        for d in self.repo.find_all():
            t = pick_translation(d.translations, language)
            items.append(
                DistrictSchema(
                    id=d.id, sort_order=d.sort_order, name=t.name if t else ""
                )
            )
        return items
