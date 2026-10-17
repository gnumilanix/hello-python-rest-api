"""District ORM model."""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from necktie.models.district_translation import DistrictTranslation
    from necktie.models.practitioner import Practitioner


class District(SQLModel, table=True):
    __tablename__ = "district"

    id: int | None = Field(default=None, primary_key=True)
    sort_order: int

    translations: list["DistrictTranslation"] = Relationship(
        back_populates="district", cascade_delete=True
    )
    practitioners: list["Practitioner"] = Relationship(back_populates="district")
