"""Data access for practitioners (the doctor resource)."""

from collections.abc import Iterable

from sqlalchemy import exists
from sqlmodel import Session, select

from necktie.models import Category, District, Practitioner
from necktie.routers.helpers import (
    with_localized_relations,
    with_practitioner_relations,
)


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
        stmt = with_practitioner_relations(select(Practitioner))
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

    def find_by_id_localized(
        self, practitioner_id: int, language: str
    ) -> Practitioner | None:
        """Return one practitioner loading only ``language`` translations."""
        stmt = with_localized_relations(
            select(Practitioner).where(Practitioner.id == practitioner_id),
            language,
        )
        return self.db.exec(stmt).first()

    def add_all(self, practitioners: Iterable[Practitioner]) -> None:
        """Stage practitioners for insert."""
        self.db.add_all(practitioners)

    def category_exists(self, category_id: int) -> bool:
        """Whether the category id is valid."""
        return bool(
            self.db.exec(select(exists().where(Category.id == category_id))).first()
        )

    def district_exists(self, district_id: int) -> bool:
        """Whether the district id is valid."""
        return bool(
            self.db.exec(select(exists().where(District.id == district_id))).first()
        )

    def commit(self) -> None:
        """Commit the current transaction."""
        self.db.commit()
