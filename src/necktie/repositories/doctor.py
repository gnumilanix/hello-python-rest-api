"""Data access for doctors (the doctor resource)."""

from collections.abc import Iterable

from sqlalchemy.orm import load_only, selectinload
from sqlmodel import Session, select

from necktie.models import Doctor
from necktie.utils.languages import Language


class DoctorRepository:
    """CRUD queries for the doctors table."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_all(
        self,
        language: Language,
        district_id: int | None,
        category_id: int | None,
        min_fee: int | None,
        max_fee: int | None,
        offset: int,
        limit: int,
    ) -> Iterable[Doctor]:
        """Return doctors matching the filters, paginated, localized to ``language``.

        Only ``language``'s text columns are loaded; the other two languages'
        name/address/fee_detail columns are deferred.
        """
        col = language.value
        stmt = select(Doctor).options(
            selectinload(Doctor.operating_hours),
            load_only(
                Doctor.id,
                Doctor.category_id,
                Doctor.district_id,
                Doctor.place_id,
                Doctor.phone_numbers,
                Doctor.member_exclusive_fee,
                Doctor.consultation_fee,
                Doctor.is_open_on_public_holidays,
                getattr(Doctor, f"name_{col}"),
                getattr(Doctor, f"address_{col}"),
                getattr(Doctor, f"fee_detail_{col}"),
            ),
        )
        if district_id is not None:
            stmt = stmt.where(Doctor.district_id == district_id)
        if category_id is not None:
            stmt = stmt.where(Doctor.category_id == category_id)
        if min_fee is not None:
            stmt = stmt.where(Doctor.consultation_fee >= min_fee)
        if max_fee is not None:
            stmt = stmt.where(Doctor.consultation_fee <= max_fee)
        stmt = stmt.order_by(Doctor.id).offset(offset).limit(limit)
        return self.db.exec(stmt).all()

    def find_by_id(self, doctor_id: int) -> Doctor | None:
        """Return one doctor by id."""
        stmt = (
            select(Doctor)
            .where(Doctor.id == doctor_id)
            .options(selectinload(Doctor.operating_hours))
        )
        return self.db.exec(stmt).first()

    def find_by_id_localized(
        self, doctor_id: int, language: Language
    ) -> Doctor | None:
        """Return one doctor loading only ``language``'s text columns.

        Non-translated columns are always loaded; the other two languages'
        name/address/fee_detail columns are deferred (accessing them would
        trigger a lazy refresh).
        """
        col = language.value
        stmt = (
            select(Doctor)
            .where(Doctor.id == doctor_id)
            .options(
                selectinload(Doctor.operating_hours),
                load_only(
                    Doctor.id,
                    Doctor.category_id,
                    Doctor.district_id,
                    Doctor.place_id,
                    Doctor.phone_numbers,
                    Doctor.member_exclusive_fee,
                    Doctor.consultation_fee,
                    Doctor.is_open_on_public_holidays,
                    getattr(Doctor, f"name_{col}"),
                    getattr(Doctor, f"address_{col}"),
                    getattr(Doctor, f"fee_detail_{col}"),
                ),
            )
        )
        return self.db.exec(stmt).first()

    def add_all(self, doctors: Iterable[Doctor]) -> None:
        """Stage doctors for insert."""
        self.db.add_all(doctors)

    def commit(self) -> None:
        """Commit the current transaction."""
        self.db.commit()
