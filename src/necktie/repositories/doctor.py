"""Data access for doctors (the doctor resource)."""

from collections.abc import Iterable

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from necktie.models import Doctor

class DoctorRepository:
    """CRUD queries for the doctors table."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_all(
        self,
        district_id: int | None,
        category_id: int | None,
        min_fee: int | None,
        max_fee: int | None,
        offset: int,
        limit: int,
    ) -> Iterable[Doctor]:
        """Return doctors matching the filters, paginated."""
        stmt = select(Doctor).options(selectinload(Doctor.operating_hours))
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

    def add_all(self, doctors: Iterable[Doctor]) -> None:
        """Stage doctors for insert."""
        self.db.add_all(doctors)

    def commit(self) -> None:
        """Commit the current transaction."""
        self.db.commit()
