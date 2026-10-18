"""District ORM model."""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from necktie.models.doctor import Doctor


class District(SQLModel, table=True):
    __tablename__ = "district"

    id: int | None = Field(default=None, primary_key=True)
    sort_order: int
    name_en: str
    name_yue: str
    name_zh: str

    doctors: list["Doctor"] = Relationship(back_populates="district")
