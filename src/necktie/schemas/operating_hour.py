"""Operating hour API schemas, grouped per domain."""

from datetime import time

from pydantic import BaseModel

from necktie.utils.day_of_week import DayOfWeek


class OperatingHourBase(BaseModel):
    """Shared operating hour fields."""

    open_time: time
    close_time: time


class OperatingHour(OperatingHourBase):
    """Operating hour in responses with a named weekday."""

    day_of_week: DayOfWeek


class OperatingHourInput(OperatingHourBase):
    """Operating hour supplied when creating a doctor."""

    day_of_week: DayOfWeek
