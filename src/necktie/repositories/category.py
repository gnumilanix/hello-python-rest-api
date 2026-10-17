"""Data access for categories."""

from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlmodel import Session

from necktie.models import Category, CategoryTranslation


class CategoryRepository:
    """Read queries for the category table."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_all_localized(self, language: str) -> Iterable[Category]:
        """Return all categories loading only ``language`` translations."""
        stmt = select(Category).options(
            selectinload(Category.translations),
            with_loader_criteria(
                CategoryTranslation, CategoryTranslation.language_code == language
            ),
        )
        return self.db.scalars(stmt).all()
