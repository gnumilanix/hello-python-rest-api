"""Unit tests for the language-picker helpers in the doctor mapper (no infra)."""

import pytest
from pydantic import ValidationError

from necktie.mappers.category import CategoryCatalogEntry
from necktie.mappers.district import DistrictCatalogEntry
from necktie.mappers.doctor import _pick_category, _pick_district
from necktie.schemas.locale import LocaleModel, NullableLocaleModel
from necktie.utils.languages import Language


def _category() -> CategoryCatalogEntry:
    return CategoryCatalogEntry(
        id=1,
        name_key="gp",
        name_en="General Practice",
        name_yue="普通科",
        name_zh="普通科",
    )


def _district() -> DistrictCatalogEntry:
    return DistrictCatalogEntry(
        id=1, sort_order=1, name_en="Central", name_yue="中西區", name_zh="中西区"
    )


class TestPickCategory:
    def test_english(self) -> None:
        assert _pick_category(_category(), Language.EN) == "General Practice"

    def test_cantonese(self) -> None:
        assert _pick_category(_category(), Language.YUE) == "普通科"

    def test_mandarin(self) -> None:
        assert _pick_category(_category(), Language.ZH) == "普通科"


class TestPickDistrict:
    def test_english(self) -> None:
        assert _pick_district(_district(), Language.EN) == "Central"

    def test_cantonese(self) -> None:
        assert _pick_district(_district(), Language.YUE) == "中西區"

    def test_mandarin(self) -> None:
        assert _pick_district(_district(), Language.ZH) == "中西区"


class TestLocaleModel:
    def test_valid(self) -> None:
        m = LocaleModel(en="a", yue="b", zh="c")
        assert m.en == "a"

    def test_rejects_empty_string(self) -> None:
        with pytest.raises(ValidationError):
            LocaleModel(en="", yue="b", zh="c")

    def test_nullable_allows_absent(self) -> None:
        m = NullableLocaleModel()
        assert m.en is None

    def test_nullable_rejects_empty_when_present(self) -> None:
        with pytest.raises(ValidationError):
            NullableLocaleModel(en="")
