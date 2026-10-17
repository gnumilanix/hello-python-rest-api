"""Mappers for operating hours."""

from necktie.enums import DayOfWeek
from necktie.models import OperatingHour
from necktie.schemas import OperatingHourDetail, OperatingHourIn
from necktie.schemas.operating_hour import OperatingHour as OperatingHourSchema


def to_operating_hour_orm(oh: OperatingHourIn) -> OperatingHour:
    """Build an OperatingHour ORM object from create payload."""
    return OperatingHour(
        day_of_week=oh.day_of_week,
        open_time=oh.open_time,
        close_time=oh.close_time,
    )


def to_operating_hour(oh: OperatingHour) -> OperatingHourSchema:
    """Serialize an operating hour with a day name (list responses)."""
    return OperatingHourSchema(
        day_of_week=DayOfWeek(oh.day_of_week).label,
        open_time=oh.open_time,
        close_time=oh.close_time,
    )


def to_operating_hour_detail(oh: OperatingHour) -> OperatingHourDetail:
    """Serialize an operating hour with the ISO day number (detail responses)."""
    return OperatingHourDetail(
        day_of_week=oh.day_of_week,
        open_time=oh.open_time,
        close_time=oh.close_time,
    )
