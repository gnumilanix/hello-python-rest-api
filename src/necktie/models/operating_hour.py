"""Operating hour ORM model."""

from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from necktie.models.practitioner import Practitioner


class OperatingHour(SQLModel, table=True):
    """One open/close interval for a practitioner.

    day_of_week follows ISO 8601: 1 = Monday, 7 = Sunday.
    """

    __tablename__ = "operating_hours"
    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 1 AND 7", name="ck_day_of_week"),
    )

    id: int | None = Field(default=None, primary_key=True)
    practitioner_id: int = Field(foreign_key="practitioners.id", ondelete="CASCADE")
    day_of_week: int
    open_time: time
    close_time: time

    practitioner: "Practitioner" = Relationship(back_populates="operating_hours")
