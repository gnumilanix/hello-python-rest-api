"""Named weekdays for the API, mapped to ISO numbers in storage."""

from enum import StrEnum


class DayOfWeek(StrEnum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

    @property
    def iso_number(self) -> int:
        return list(type(self)).index(self) + 1

    @classmethod
    def from_iso(cls, number: int) -> "DayOfWeek":
        if not 1 <= number <= 7:
            raise ValueError("ISO weekday must be between 1 and 7")
        return list(cls)[number - 1]