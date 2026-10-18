"""Data access for categories."""

from collections.abc import Iterable

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from necktie.models import Category


class CategoryRepository:
    """Read queries for the category table."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_all(self) -> Iterable[Category]:
        """Return all categories with every translation, ordered by id."""
        stmt = (
            select(Category)
            .options(selectinload(Category.translations))
            .order_by(Category.id)
        )
        return self.db.exec(stmt).all()
