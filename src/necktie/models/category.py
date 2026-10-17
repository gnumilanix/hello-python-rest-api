"""Category ORM model."""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from necktie.models.category_translation import CategoryTranslation
    from necktie.models.practitioner import Practitioner


class Category(SQLModel, table=True):
    __tablename__ = "category"

    id: int | None = Field(default=None, primary_key=True)
    name_key: str = Field(unique=True)

    translations: list["CategoryTranslation"] = Relationship(
        back_populates="category", cascade_delete=True
    )
    practitioners: list["Practitioner"] = Relationship(back_populates="category")
