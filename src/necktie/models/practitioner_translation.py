"""Practitioner translation ORM model."""

from typing import TYPE_CHECKING

from sqlalchemy import Text
from sqlmodel import Field, Relationship, SQLModel

from necktie.models.constants import LANGUAGE_CODE_LENGTH

if TYPE_CHECKING:
    from necktie.models.practitioner import Practitioner


class PractitionerTranslation(SQLModel, table=True):
    __tablename__ = "practitioners_translations"

    practitioner_id: int = Field(
        foreign_key="practitioners.id", primary_key=True, ondelete="CASCADE"
    )
    language_code: str = Field(max_length=LANGUAGE_CODE_LENGTH, primary_key=True)
    name: str
    address: str = Field(sa_type=Text)
    fee_detail: str | None = Field(default=None, sa_type=Text)

    practitioner: "Practitioner" = Relationship(back_populates="translations")
