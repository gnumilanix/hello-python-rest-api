"""Category ORM model."""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from necktie.models.doctor import Doctor


class Category(SQLModel, table=True):
    __tablename__ = "category"

    id: int | None = Field(default=None, primary_key=True)
    name_key: str = Field(unique=True)
    name_en: str
    name_yue: str
    name_zh: str

    doctors: list["Doctor"] = Relationship(back_populates="category")
