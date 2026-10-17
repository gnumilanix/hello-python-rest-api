"""Operating hour entry with day name."""

from datetime import time

from pydantic import BaseModel


class OperatingHour(BaseModel):
    """Operating hour entry in list responses (day name)."""

    day_of_week: str
    open_time: time
    close_time: time
