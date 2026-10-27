"""Mappers for operating hours."""

from necktie.models import OperatingHour
from necktie.schemas import OperatingHour as OperatingHourSchema
from necktie.schemas import OperatingHourInput


def to_operating_hour_orm(oh: OperatingHourInput) -> OperatingHour:
    """Build an OperatingHour ORM object from create payload.

    doctor_id is set by SQLAlchemy via the relationship on save.
    """
    return OperatingHour(
        doctor_id=0,  # placeholder; overwritten by the relationship on save
        day_of_week=oh.day_of_week,
        open_time=oh.open_time,
        close_time=oh.close_time,
    )


def to_operating_hour(oh: OperatingHour) -> OperatingHourSchema:
    """Serialize an operating hour with a named weekday."""
    return OperatingHourSchema(
        day_of_week=oh.day_of_week,
        open_time=oh.open_time,
        close_time=oh.close_time,
    )
