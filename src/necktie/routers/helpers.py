"""Mappers between practitioner ORM models and API schemas."""

from sqlalchemy.orm import selectinload

from necktie.models import Category, District, Practitioner
from necktie.schemas import (
    CategoryRef,
    CategoryTranslated,
    DistrictRef,
    DistrictTranslated,
    DoctorDetail,
    DoctorListItem,
    OpeningHourDetail,
    OpeningHourListItem,
)

DAY_NAMES = {
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
    7: "Sunday",
}


def pick_translation(translations: list, language: str):
    """Return the translation for ``language``, falling back to the first."""
    for t in translations:
        if t.language_code == language:
            return t
    return translations[0] if translations else None


def with_practitioner_relations(stmt):
    """Eager-load all relationships needed to serialize a practitioner."""
    return stmt.options(
        selectinload(Practitioner.translations),
        selectinload(Practitioner.operating_hours),
        selectinload(Practitioner.category).selectinload(Category.translations),
        selectinload(Practitioner.district).selectinload(District.translations),
    )


def to_list_item(p: Practitioner, language: str) -> DoctorListItem:
    """Serialize a practitioner to a localized list item."""
    cat = pick_translation(p.category.translations, language)
    dist = pick_translation(p.district.translations, language)
    own = pick_translation(p.translations, language)
    return DoctorListItem(
        id=p.id,
        category=CategoryRef(id=p.category.id, name=cat.name if cat else ""),
        district=DistrictRef(id=p.district.id, name=dist.name if dist else ""),
        address=own.address if own else "",
        place_id=p.place_id,
        phone_numbers=p.phone_number_list,
        is_active=p.is_active,
        member_exclusive_fee=p.member_exclusive_fee,
        consultation_fee=p.consultation_fee,
        is_open_on_public_holidays=p.is_open_on_public_holidays,
        opening_hours=[
            OpeningHourListItem(
                day_of_week=DAY_NAMES.get(oh.day_of_week, str(oh.day_of_week)),
                open_time=oh.open_time,
                close_time=oh.close_time,
            )
            for oh in p.operating_hours
        ],
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
        address={t.language_code: t.address for t in p.translations},
        place_id=p.place_id,
        phone_numbers=p.phone_number_list,
        is_active=p.is_active,
        member_exclusive_fee=p.member_exclusive_fee,
        consultation_fee=p.consultation_fee,
        is_open_on_public_holidays=p.is_open_on_public_holidays,
        opening_hours=[
            OpeningHourDetail(
                day_of_week=oh.day_of_week,
                open_time=oh.open_time,
                close_time=oh.close_time,
            )
            for oh in p.operating_hours
        ],
    )
