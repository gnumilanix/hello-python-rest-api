"""Generic field validators."""

from typing import Annotated, Any

import langcodes
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


def validate_language_code(code: str) -> str:
    """Validate ``code`` is a well-formed BCP 47 language tag."""
    if not langcodes.tag_is_valid(code):
        raise ValueError(f"Invalid language code: {code}")
    return code


LanguageCode = Annotated[
    str,
    # RFC 5646 §4.4.1: buffers must allow language tags of at least 35 chars.
    Field(min_length=2, max_length=35, description="BCP 47 language tag"),
    AfterValidator(validate_language_code),
]

