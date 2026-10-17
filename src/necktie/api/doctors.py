"""Doctor endpoints.

The resource is exposed as ``/doctor`` while the underlying table is
``practitioners``. List responses are localized to a single language;
detail responses include every translation.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlmodel import Session

from necktie.api.schemas import (
    CategoryRef,
    CategoryTranslated,
    DistrictRef,
    DistrictTranslated,
    DoctorCreate,
    DoctorDetail,
    DoctorListItem,
    OpeningHourDetail,
    OpeningHourListItem,
)
from necktie.db import (
    Category,
    District,
    OperatingHour,
    Practitioner,
    PractitionerTranslation,
)
from necktie.db.session import get_db

router = APIRouter(prefix="/doctor", tags=["doctor"])

DAY_NAMES = {
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
    7: "Sunday",
}

DEFAULT_LANGUAGE = "en-US"


def _pick(translations: list, language: str):
    """Return the translation for ``language``, falling back to the first."""
    for t in translations:
        if t.language_code == language:
            return t
    return translations[0] if translations else None


def _with_relations(stmt):
    return stmt.options(
        selectinload(Practitioner.translations),
        selectinload(Practitioner.operating_hours),
        selectinload(Practitioner.category).selectinload(Category.translations),
        selectinload(Practitioner.district).selectinload(District.translations),
    )


def _to_list_item(p: Practitioner, language: str) -> DoctorListItem:
    cat = _pick(p.category.translations, language)
    dist = _pick(p.district.translations, language)
    own = _pick(p.translations, language)
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


def _to_detail(p: Practitioner) -> DoctorDetail:
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


@router.get("", response_model=list[DoctorListItem])
def list_doctors(
    district: int | None = Query(None, description="District id"),
    category: int | None = Query(None, description="Category id"),
    min_fee: int | None = Query(None, ge=0, description="Min consultation fee"),
    max_fee: int | None = Query(None, ge=0, description="Max consultation fee"),
    language: str = Query(DEFAULT_LANGUAGE, description="Response language"),
    db: Session = Depends(get_db),
) -> list[DoctorListItem]:
    """List doctors, filterable by district, category, fee range, language."""
    stmt = _with_relations(select(Practitioner))
    if district is not None:
        stmt = stmt.where(Practitioner.district_id == district)
    if category is not None:
        stmt = stmt.where(Practitioner.category_id == category)
    if min_fee is not None:
        stmt = stmt.where(Practitioner.consultation_fee >= min_fee)
    if max_fee is not None:
        stmt = stmt.where(Practitioner.consultation_fee <= max_fee)
    doctors = db.scalars(stmt).all()
    return [_to_list_item(p, language) for p in doctors]


@router.get("/{doctor_id}", response_model=DoctorDetail)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)) -> DoctorDetail:
    """Get one doctor with all translations."""
    stmt = _with_relations(select(Practitioner).where(Practitioner.id == doctor_id))
    doctor = db.scalars(stmt).first()
    if doctor is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Doctor not found")
    return _to_detail(doctor)


def _create(db: Session, payload: DoctorCreate) -> Practitioner:
    if db.get(Category, payload.category_id) is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Category {payload.category_id} does not exist",
        )
    if db.get(District, payload.district_id) is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"District {payload.district_id} does not exist",
        )
    doctor = Practitioner(
        category_id=payload.category_id,
        district_id=payload.district_id,
        place_id=payload.place_id,
        phone_numbers=", ".join(payload.phone_numbers) or None,
        is_active=payload.is_active,
        member_exclusive_fee=payload.member_exclusive_fee,
        consultation_fee=payload.consultation_fee,
        is_open_on_public_holidays=payload.is_open_on_public_holidays,
        translations=[
            PractitionerTranslation(
                language_code=t.language_code,
                name=t.name,
                address=t.address,
                fee_detail=t.fee_detail,
            )
            for t in payload.translations
        ],
        operating_hours=[
            OperatingHour(
                day_of_week=oh.day_of_week,
                open_time=oh.open_time,
                close_time=oh.close_time,
            )
            for oh in payload.opening_hours
        ],
    )
    db.add(doctor)
    return doctor


@router.post("", response_model=DoctorDetail, status_code=status.HTTP_201_CREATED)
def create_doctor(payload: DoctorCreate, db: Session = Depends(get_db)) -> DoctorDetail:
    """Create a single doctor."""
    doctor = _create(db, payload)
    db.commit()
    return _to_detail(doctor)


@router.post(
    "/batch",
    response_model=list[DoctorDetail],
    status_code=status.HTTP_201_CREATED,
)
def create_doctors_batch(
    payload: list[DoctorCreate], db: Session = Depends(get_db)
) -> list[DoctorDetail]:
    """Create multiple doctors in one transaction."""
    doctors = [_create(db, item) for item in payload]
    db.commit()
    return [_to_detail(d) for d in doctors]
