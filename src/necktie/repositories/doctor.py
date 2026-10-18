"""Data access for practitioners (the doctor resource)."""

from collections.abc import Iterable

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from necktie.models import Practitioner


class PractitionerRepository:
    """CRUD queries for the practitioners table."""

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
    ) -> Iterable[Practitioner]:
        """Return practitioners matching the filters, paginated."""
        stmt = select(Practitioner).options(selectinload(Practitioner.operating_hours))
        if district_id is not None:
            stmt = stmt.where(Practitioner.district_id == district_id)
        if category_id is not None:
            stmt = stmt.where(Practitioner.category_id == category_id)
        if min_fee is not None:
            stmt = stmt.where(Practitioner.consultation_fee >= min_fee)
        if max_fee is not None:
            stmt = stmt.where(Practitioner.consultation_fee <= max_fee)
        stmt = stmt.order_by(Practitioner.id).offset(offset).limit(limit)
        return self.db.exec(stmt).all()

    def find_by_id(self, practitioner_id: int) -> Practitioner | None:
        """Return one practitioner by id."""
        stmt = (
            select(Practitioner)
            .where(Practitioner.id == practitioner_id)
            .options(selectinload(Practitioner.operating_hours))
        )
        return self.db.exec(stmt).first()

    def add_all(self, practitioners: Iterable[Practitioner]) -> None:
        """Stage practitioners for insert."""
        self.db.add_all(practitioners)

    def commit(self) -> None:
        """Commit the current transaction."""
        self.db.commit()
