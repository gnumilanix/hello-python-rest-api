"""Data access for districts."""

from collections.abc import Iterable

from sqlmodel import Session, select

from necktie.models import District


class DistrictRepository:
    """Read queries for the district table."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_all(self) -> Iterable[District]:
        """Return all districts ordered by sort_order."""
        stmt = select(District).order_by(District.sort_order)
        return self.db.exec(stmt).all()
