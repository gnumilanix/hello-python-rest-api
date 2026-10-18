"""Mappers between Practitioner ORM models and API schemas."""

import asyncio
from typing import TYPE_CHECKING

from necktie.mappers.category import CategoryCatalogEntry
from necktie.mappers.district import DistrictCatalogEntry
from necktie.mappers.operating_hour import (
    to_operating_hour,
    to_operating_hour_detail,
)
from necktie.models import Practitioner
from necktie.schemas import (
    CategoryRef,
    CategoryTranslated,
    DistrictRef,
    DistrictTranslated,
    Doctor,
    DoctorDetail,
    DoctorText,
    DoctorTextOptional,
)
from necktie.utils.languages import Language

if TYPE_CHECKING:
    from necktie.services.category import CategoryService
    from necktie.services.district import DistrictService


def _pick(
    en: str | None,
    yue: str | None,
    zh: str | None,
    language: Language,
) -> str | None:
    """Pick an optional practitioner text for ``language``.

    Used for fee_detail only (name/address are NOT NULL and read directly).
    """
    if language is Language.YUE:
        return yue
    if language is Language.ZH:
        return zh
    return en


def _pick_category(c: CategoryCatalogEntry, language: Language) -> str:
    """Pick a category name for ``language``."""
    if language is Language.YUE:
        return c.name_yue
    if language is Language.ZH:
        return c.name_zh
    return c.name_en


def _pick_district(d: DistrictCatalogEntry, language: Language) -> str:
    """Pick a district name for ``language``."""
    if language is Language.YUE:
        return d.name_yue
    if language is Language.ZH:
        return d.name_zh
    return d.name_en


class PractitionerMapper:
    """Serializes practitioners, resolving district/category names itself.

    The catalog services are injected via the constructor and queried on
    first use per instance, so call sites never handle reference data.
    """

    def __init__(
        self, districts: "DistrictService", categories: "CategoryService"
    ) -> None:
        self._districts = districts
        self._categories = categories
        self._district_map: dict[int, DistrictCatalogEntry] | None = None
        self._category_map: dict[int, CategoryCatalogEntry] | None = None

    async def _catalogs(
        self,
    ) -> tuple[dict[int, DistrictCatalogEntry], dict[int, CategoryCatalogEntry]]:
        """Fetch both catalogs once per instance, memoized for subsequent calls."""
        if self._district_map is None or self._category_map is None:
            self._district_map, self._category_map = await asyncio.gather(
                self._districts.get_translated_map(),
                self._categories.get_translated_map(),
            )
        return self._district_map, self._category_map

    async def to_doctor(self, p: Practitioner, language: Language) -> Doctor:
        """Serialize a practitioner to a localized doctor (single language).

        Category and district names resolve from the Redis catalogs.
        """
        districts, categories = await self._catalogs()
        cat = categories[p.category_id]
        dist = districts[p.district_id]
        return Doctor(
            id=p.id,
            category=CategoryRef(id=cat.id, name=_pick_category(cat, language)),
            district=DistrictRef(id=dist.id, name=_pick_district(dist, language)),
            name=_pick(p.name_en, p.name_yue, p.name_zh, language) or "",
            address=_pick(p.address_en, p.address_yue, p.address_zh, language) or "",
            fee_detail=_pick(
                p.fee_detail_en, p.fee_detail_yue, p.fee_detail_zh, language
            ),
            place_id=p.place_id,
            phone_numbers=p.phone_numbers,
            member_exclusive_fee=p.member_exclusive_fee,
            consultation_fee=p.consultation_fee,
            is_open_on_public_holidays=p.is_open_on_public_holidays,
            operating_hours=[to_operating_hour(oh) for oh in p.operating_hours],
        )

    async def to_detail(self, p: Practitioner) -> DoctorDetail:
        """Serialize a practitioner with every translation."""
        districts, categories = await self._catalogs()
        cat = categories[p.category_id]
        dist = districts[p.district_id]
        return DoctorDetail(
            id=p.id,
            category=CategoryTranslated(id=cat.id, name=cat.names()),
            district=DistrictTranslated(id=dist.id, name=dist.names()),
            name=DoctorText(en=p.name_en, yue=p.name_yue, zh=p.name_zh),
            address=DoctorText(en=p.address_en, yue=p.address_yue, zh=p.address_zh),
            fee_detail=DoctorTextOptional(
                en=p.fee_detail_en, yue=p.fee_detail_yue, zh=p.fee_detail_zh
            ),
            place_id=p.place_id,
            phone_numbers=p.phone_numbers,
            member_exclusive_fee=p.member_exclusive_fee,
            consultation_fee=p.consultation_fee,
            is_open_on_public_holidays=p.is_open_on_public_holidays,
            operating_hours=[to_operating_hour_detail(oh) for oh in p.operating_hours],
        )
