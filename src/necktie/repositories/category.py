"""Data access for categories."""

from collections.abc import Iterable

from sqlmodel import Session, select

from necktie.models import Category


class CategoryRepository:
    """Read queries for the category table."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_all(self) -> Iterable[Category]:
        """Return all categories ordered by id."""
        stmt = select(Category).order_by(Category.id)
        return self.db.exec(stmt).all()
