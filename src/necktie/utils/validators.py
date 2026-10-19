"""Generic field validators."""

from typing import Annotated

import phonenumbers
from pydantic import AfterValidator, Field

from necktie.utils.constants import DEFAULT_PHONE_REGION


def validate_phone_numbers(
    numbers: list[str], region: str = DEFAULT_PHONE_REGION
) -> list[str]:
    """Validate each number is a valid phone number for ``region``.

    Raises ValueError listing the first invalid number.
    """
    for n in numbers:
        try:
            parsed = phonenumbers.parse(n, region)
        except phonenumbers.NumberParseException as e:
            raise ValueError(f"Invalid phone number: {n}") from e
        if not phonenumbers.is_valid_number(parsed):
            raise ValueError(f"Invalid phone number: {n}")
    return numbers


def _validate_default_phone_numbers(numbers: list[str]) -> list[str]:
    """Validate numbers against the default region."""
    return validate_phone_numbers(numbers, region=DEFAULT_PHONE_REGION)


DefaultPhoneList = Annotated[
    list[str],
    Field(
        min_length=1,
        description=f"List of validated {DEFAULT_PHONE_REGION} phone numbers",
    ),
    AfterValidator(_validate_default_phone_numbers),
]
