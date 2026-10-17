"""ISO 8601 day-of-week enum (1=Monday, 7=Sunday)."""

from enum import IntEnum


class DayOfWeek(IntEnum):
    """ISO 8601 day of week; ``.label`` gives the English name."""

    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

    @property
    def label(self) -> str:
        """English day name."""
        return self.name.capitalize()
