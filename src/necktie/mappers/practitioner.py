"""Mappers between Practitioner ORM models and API schemas."""

from collections.abc import Mapping

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
)
from necktie.utils.constants import DEFAULT_LANGUAGE


def _localized(names: Mapping[str, str], language: str) -> str:
    """Pick ``language`` from a name map, falling back to the default language."""
    return names.get(language) or names.get(DEFAULT_LANGUAGE, "")


def to_doctor(
    p: Practitioner,
    language: str,
    categories: Mapping[int, CategoryCatalogEntry],
    districts: Mapping[int, DistrictCatalogEntry],
) -> Doctor:
    """Serialize a practitioner to a localized doctor (single language).

    Practitioner translations are pre-filtered to the requested language by
    the query; category and district names resolve from the Redis catalogs.
    """
    cat = categories[p.category_id]
    dist = districts[p.district_id]
    own = p.translations[0] if p.translations else None
    return Doctor(
        id=p.id,
        category=CategoryRef(id=cat.id, name=_localized(cat.name, language)),
        district=DistrictRef(id=dist.id, name=_localized(dist.name, language)),
        name=own.name if own else "",
        address=own.address if own else "",
        fee_detail=own.fee_detail if own else None,
        place_id=p.place_id,
        phone_numbers=p.phone_numbers,
        member_exclusive_fee=p.member_exclusive_fee,
        consultation_fee=p.consultation_fee,
        is_open_on_public_holidays=p.is_open_on_public_holidays,
        operating_hours=[to_operating_hour(oh) for oh in p.operating_hours],
    )


def to_detail(
    p: Practitioner,
    categories: Mapping[int, CategoryCatalogEntry],
    districts: Mapping[int, DistrictCatalogEntry],
) -> DoctorDetail:
    """Serialize a practitioner with every translation."""
    cat = categories[p.category_id]
    dist = districts[p.district_id]
    return DoctorDetail(
        id=p.id,
        category=CategoryTranslated(id=cat.id, name=cat.name),
        district=DistrictTranslated(id=dist.id, name=dist.name),
        name={t.language_code: t.name for t in p.translations},
        address={t.language_code: t.address for t in p.translations},
        fee_detail={t.language_code: t.fee_detail for t in p.translations},
        place_id=p.place_id,
        phone_numbers=p.phone_numbers,
        member_exclusive_fee=p.member_exclusive_fee,
        consultation_fee=p.consultation_fee,
        is_open_on_public_holidays=p.is_open_on_public_holidays,
        operating_hours=[to_operating_hour_detail(oh) for oh in p.operating_hours],
    )
