"""Opening hour entry in detail responses (ISO day number)."""

from datetime import time

from pydantic import BaseModel


class OpeningHourDetail(BaseModel):
    """Opening hour entry in detail responses (ISO day number)."""

    day_of_week: int
    open_time: time
    close_time: time
