"""Business logic for districts."""

from necktie.mappers import to_district
from necktie.repositories.district import DistrictRepository
from necktie.schemas import District as DistrictSchema
from necktie.utils import cache


class DistrictService:
    """Coordinates district repository access and mapping."""

    def __init__(self, repository: DistrictRepository) -> None:
        self.repo = repository

    def list_districts(self, language: str) -> list[DistrictSchema]:
        """List districts localized to ``language``, ordered by sort_order (cached)."""
        key = cache.build_key("districts", {"language": language})
        return cache.get_or_fetch(
            key,
            lambda: [to_district(d) for d in self.repo.find_all_localized(language)],
            decode=lambda data: [DistrictSchema.model_validate(d) for d in data],
        )
