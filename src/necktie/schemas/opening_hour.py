"""Opening hour entry in list responses (day name)."""

from datetime import time

from pydantic import BaseModel


class OpeningHourListItem(BaseModel):
    """Opening hour entry in list responses (day name)."""

    day_of_week: str
    open_time: time
    close_time: time
