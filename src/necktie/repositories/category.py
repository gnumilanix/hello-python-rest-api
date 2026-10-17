"""Data access for categories."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlmodel import Session

from necktie.models import Category


class CategoryRepository:
    """Read queries for the category table."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_all(self) -> Sequence[Category]:
        """Return all categories with their translations."""
        stmt = select(Category).options(selectinload(Category.translations))
        return self.db.scalars(stmt).all()
