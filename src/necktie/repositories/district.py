"""Data access for districts."""

from collections.abc import Iterable

from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlmodel import Session, select

from necktie.models import District, DistrictTranslation


class DistrictRepository:
    """Read queries for the district table."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_all_localized(self, language: str) -> Iterable[District]:
        """Return all districts ordered by sort_order, loading only ``language``."""
        stmt = (
            select(District)
            .options(
                selectinload(District.translations),
                with_loader_criteria(
                    DistrictTranslation, DistrictTranslation.language_code == language
                ),
            )
            .order_by(District.sort_order)
        )
        return self.db.exec(stmt).all()
