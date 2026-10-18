"""Unit tests for phone-number validators (no app, no infra)."""

import pytest

from necktie.utils.validators import validate_phone_numbers


class TestValidatePhoneNumbers:
    def test_valid_hk_mobile(self) -> None:
        assert validate_phone_numbers(["91234567"]) == ["91234567"]

    def test_valid_hk_landline(self) -> None:
        assert validate_phone_numbers(["23456789"]) == ["23456789"]

    def test_valid_with_country_code(self) -> None:
        assert validate_phone_numbers(["+85291234567"]) == ["+85291234567"]

    def test_multiple_valid(self) -> None:
        numbers = ["91234567", "23456789"]
        assert validate_phone_numbers(numbers) == numbers

    def test_invalid_number_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid phone number"):
            validate_phone_numbers(["not-a-number"])

    def test_too_few_digits_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid phone number"):
            validate_phone_numbers(["123"])

    def test_first_invalid_number_reported(self) -> None:
        with pytest.raises(ValueError, match="bad"):
            validate_phone_numbers(["91234567", "bad"])

    def test_other_region(self) -> None:
        # A US number without a country code is valid under US but not HK.
        assert validate_phone_numbers(["2025550123"], region="US")
        with pytest.raises(ValueError):
            validate_phone_numbers(["2025550123"], region="HK")
