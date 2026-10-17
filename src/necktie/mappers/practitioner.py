"""Mappers between Practitioner ORM models and API schemas."""

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


def to_doctor(p: Practitioner) -> Doctor:
    """Serialize a practitioner to a localized doctor (single language).

    Translations are pre-filtered to the requested language by the query, so
    the first translation of each relation is the localized one.
    """
    cat = p.category.translations[0] if p.category.translations else None
    dist = p.district.translations[0] if p.district.translations else None
    own = p.translations[0] if p.translations else None
    return Doctor(
        id=p.id,
        category=CategoryRef(id=p.category.id, name=cat.name if cat else ""),
        district=DistrictRef(id=p.district.id, name=dist.name if dist else ""),
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


def to_detail(p: Practitioner) -> DoctorDetail:
    """Serialize a practitioner with every translation."""
    return DoctorDetail(
        id=p.id,
        category=CategoryTranslated(
            id=p.category.id,
            name={t.language_code: t.name for t in p.category.translations},
        ),
        district=DistrictTranslated(
            id=p.district.id,
            name={t.language_code: t.name for t in p.district.translations},
        ),
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
