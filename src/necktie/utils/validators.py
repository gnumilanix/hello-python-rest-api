"""Generic field validators."""

from typing import Annotated, Any

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


def PhoneList(region: str = DEFAULT_PHONE_REGION) -> Any:
    """Return a self-validating phone-number list type for ``region``.

    Usage: ``phone_numbers: PhoneList()`` (HK) or ``PhoneList(region="US")``.
    """

    def validator_wrapper(numbers: list[str]) -> list[str]:
        return validate_phone_numbers(numbers, region=region)

    return Annotated[
        list[str],
        Field(min_length=1, description=f"List of validated {region} phone numbers"),
        AfterValidator(validator_wrapper),
    ]

