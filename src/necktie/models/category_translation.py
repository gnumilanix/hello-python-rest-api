"""Category translation ORM model."""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from necktie.models.constants import LANGUAGE_CODE_LENGTH

if TYPE_CHECKING:
    from necktie.models.category import Category


class CategoryTranslation(SQLModel, table=True):
    __tablename__ = "category_translations"

    category_id: int = Field(
        foreign_key="category.id", primary_key=True, ondelete="CASCADE"
    )
    language_code: str = Field(max_length=LANGUAGE_CODE_LENGTH, primary_key=True)
    name: str

    category: "Category" = Relationship(back_populates="translations")
