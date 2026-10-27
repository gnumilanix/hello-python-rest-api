"""Operating hour ORM model."""

from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Integer
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator
from sqlmodel import Field, Relationship, SQLModel

from necktie.utils.day_of_week import DayOfWeek

if TYPE_CHECKING:
    from necktie.models.doctor import Doctor


class DayOfWeekType(TypeDecorator[DayOfWeek]):
    """Store ISO integers while keeping named enum values in the domain model."""

    impl = Integer
    cache_ok = True

    def process_bind_param(
        self, value: DayOfWeek | None, dialect: Dialect
    ) -> int | None:
        return value.iso_number if value is not None else None

    def process_result_value(
        self, value: int | None, dialect: Dialect
    ) -> DayOfWeek | None:
        return DayOfWeek.from_iso(value) if value is not None else None


class OperatingHour(SQLModel, table=True):
    """One open/close interval for a doctor."""

    __tablename__ = "operating_hours"
    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 1 AND 7", name="ck_day_of_week"),
    )

    id: int | None = Field(default=None, primary_key=True)
    doctor_id: int = Field(foreign_key="doctors.id", ondelete="CASCADE")
    day_of_week: DayOfWeek = Field(sa_type=DayOfWeekType)
    open_time: time
    close_time: time

    doctor: "Doctor" = Relationship(back_populates="operating_hours")
