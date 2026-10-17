"""District translation ORM model."""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from necktie.models.constants import LANGUAGE_CODE_LENGTH

if TYPE_CHECKING:
    from necktie.models.district import District


class DistrictTranslation(SQLModel, table=True):
    __tablename__ = "district_translations"

    district_id: int = Field(
        foreign_key="district.id", primary_key=True, ondelete="CASCADE"
    )
    language_code: str = Field(max_length=LANGUAGE_CODE_LENGTH, primary_key=True)
    name: str

    district: "District" = Relationship(back_populates="translations")
