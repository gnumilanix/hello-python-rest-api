"""Operating hour API schemas, grouped per domain."""

from datetime import time

from pydantic import BaseModel, Field


class OperatingHourBase(BaseModel):
    """Shared operating hour fields."""

    open_time: time
    close_time: time


class OperatingHour(OperatingHourBase):
    """Operating hour in list responses (day name)."""

    day_of_week: str


class OperatingHourDetail(OperatingHourBase):
    """Operating hour in detail responses (ISO day number)."""

    day_of_week: int


class OperatingHourCreate(OperatingHourBase):
    """Operating hour supplied when creating a doctor."""

    day_of_week: int = Field(ge=1, le=7, description="ISO day: 1=Mon, 7=Sun")
