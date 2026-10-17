"""Mappers between Practitioner ORM models and API schemas."""

from necktie.enums import DayOfWeek
from necktie.mappers.translation import pick_translation
from necktie.models import Practitioner
from necktie.schemas import (
    CategoryRef,
    CategoryTranslated,
    DistrictRef,
    DistrictTranslated,
    Doctor,
    DoctorDetail,
    OpeningHour,
    OpeningHourDetail,
)


def to_list_item(p: Practitioner, language: str) -> Doctor:
    """Serialize a practitioner to a localized doctor."""
    cat = pick_translation(p.category.translations, language)
    dist = pick_translation(p.district.translations, language)
    own = pick_translation(p.translations, language)
    return Doctor(
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
            OpeningHour(
                day_of_week=DayOfWeek(oh.day_of_week).label,
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
