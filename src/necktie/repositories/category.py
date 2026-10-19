"""Data access for categories."""

from collections.abc import Iterable

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from necktie.models import Category


class CategoryRepository:
    """Read queries for the category table."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def find_all(self) -> Iterable[Category]:
        """Return all categories ordered by id."""
        stmt = select(Category).order_by(Category.id)
        result = await self.db.exec(stmt)
        return result.all()
