"""Data access for districts."""

from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlmodel import Session

from necktie.models import District


class DistrictRepository:
    """Read queries for the district table."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_all(self) -> Iterable[District]:
        """Return all districts ordered by sort_order, with translations."""
        stmt = (
            select(District)
            .options(selectinload(District.translations))
            .order_by(District.sort_order)
        )
        return self.db.scalars(stmt).all()
