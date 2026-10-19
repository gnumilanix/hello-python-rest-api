"""Mappers between Doctor ORM models and API schemas."""

import asyncio
from typing import TYPE_CHECKING

from necktie.mappers.category import CategoryCatalogEntry
from necktie.mappers.district import DistrictCatalogEntry
from necktie.mappers.operating_hour import to_operating_hour, to_operating_hour_orm
from necktie.models import Doctor as DoctorEntity
from necktie.schemas import (
    CategoryRef,
    DistrictRef,
    Doctor,
    DoctorCreate,
)
from necktie.utils.languages import Language

if TYPE_CHECKING:
    from necktie.services.category import CategoryService
    from necktie.services.district import DistrictService


def _pick_localized(p: DoctorEntity, language: Language) -> tuple[str, str, str | None]:
    """Read the single loaded language's name/address/fee_detail.

    Callers must have loaded only ``language``'s columns (find_by_id_localized);
    reading the other two languages here would trigger a lazy refresh.
    """
    col = language.value
    return (
        getattr(p, f"name_{col}") or "",
        getattr(p, f"address_{col}") or "",
        getattr(p, f"fee_detail_{col}"),
    )


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


def to_doctor_orm(payload: DoctorCreate) -> DoctorEntity:
    """Build a Doctor ORM object from a create payload.

    Reference validity (category_id/district_id) is the service's job; this
    is a pure schema→entity mapping.
    """
    return DoctorEntity(
        category_id=payload.category_id,
        district_id=payload.district_id,
        place_id=payload.place_id,
        phone_numbers=payload.phone_numbers,
        member_exclusive_fee=payload.member_exclusive_fee,
        consultation_fee=payload.consultation_fee,
        is_open_on_public_holidays=payload.is_open_on_public_holidays,
        name_en=payload.name.en,
        name_yue=payload.name.yue,
        name_zh=payload.name.zh,
        address_en=payload.address.en,
        address_yue=payload.address.yue,
        address_zh=payload.address.zh,
        fee_detail_en=payload.fee_detail.en,
        fee_detail_yue=payload.fee_detail.yue,
        fee_detail_zh=payload.fee_detail.zh,
        operating_hours=[
            to_operating_hour_orm(oh) for oh in payload.operating_hours
        ],
    )


class DoctorMapper:
    """Serializes doctors, resolving district/category names itself.

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
        # The if-block above guarantees both are populated.
        if self._district_map is None or self._category_map is None:
            raise RuntimeError("catalogs failed to populate")
        return self._district_map, self._category_map

    async def to_doctor(self, p: DoctorEntity, language: Language) -> Doctor:
        """Serialize a doctor to a localized doctor (single language).

        Category and district names resolve from the Redis catalogs. The
        practitioner entity is expected to have only ``language``'s text
        columns loaded (find_by_id_localized).
        """
        districts, categories = await self._catalogs()
        cat = categories[p.category_id]
        dist = districts[p.district_id]
        name, address, fee_detail = _pick_localized(p, language)
        return Doctor(
            id=p.id,
            category=CategoryRef(id=cat.id, name=_pick_category(cat, language)),
            district=DistrictRef(id=dist.id, name=_pick_district(dist, language)),
            name=name,
            address=address,
            fee_detail=fee_detail,
            place_id=p.place_id,
            phone_numbers=p.phone_numbers,
            member_exclusive_fee=p.member_exclusive_fee,
            consultation_fee=p.consultation_fee,
            is_open_on_public_holidays=p.is_open_on_public_holidays,
            operating_hours=[to_operating_hour(oh) for oh in p.operating_hours],
        )
