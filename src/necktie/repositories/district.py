"""Data access for districts."""

from collections.abc import Iterable

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from necktie.models import District


class DistrictRepository:
    """Read queries for the district table."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def find_all(self) -> Iterable[District]:
        """Return all districts ordered by sort_order."""
        stmt = select(District).order_by(District.sort_order)
        result = await self.db.exec(stmt)
        return result.all()
