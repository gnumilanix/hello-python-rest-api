"""Mappers for operating hours."""

from necktie.models import OperatingHour
from necktie.schemas import OperatingHour as OperatingHourSchema
from necktie.schemas import OperatingHourCreate


def to_operating_hour_orm(oh: OperatingHourCreate) -> OperatingHour:
    """Build an OperatingHour ORM object from create payload."""
    return OperatingHour(
        day_of_week=oh.day_of_week,
        open_time=oh.open_time,
        close_time=oh.close_time,
    )


def to_operating_hour(oh: OperatingHour) -> OperatingHourSchema:
    """Serialize an operating hour with the ISO day number."""
    return OperatingHourSchema(
        day_of_week=oh.day_of_week,
        open_time=oh.open_time,
        close_time=oh.close_time,
    )
