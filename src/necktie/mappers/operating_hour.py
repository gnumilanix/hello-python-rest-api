"""Mappers for operating hours."""

from necktie.models import OperatingHour
from necktie.schemas import OperatingHourIn


def to_operating_hour_orm(oh: OperatingHourIn) -> OperatingHour:
    """Build an OperatingHour ORM object from create payload."""
    return OperatingHour(
        day_of_week=oh.day_of_week,
        open_time=oh.open_time,
        close_time=oh.close_time,
    )
