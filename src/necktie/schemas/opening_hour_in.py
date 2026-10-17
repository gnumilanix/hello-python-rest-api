"""Opening hour supplied when creating a doctor."""

from datetime import time

from pydantic import BaseModel, Field


class OpeningHourIn(BaseModel):
    """Opening hour supplied when creating a doctor."""

    day_of_week: int = Field(ge=1, le=7, description="ISO day: 1=Mon, 7=Sun")
    open_time: time
    close_time: time
