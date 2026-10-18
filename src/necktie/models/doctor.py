"""Practitioner ORM model."""

from typing import TYPE_CHECKING

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from necktie.models.category import Category
    from necktie.models.district import District
    from necktie.models.operating_hour import OperatingHour


class Practitioner(SQLModel, table=True):
    """A practitioner listing (see README "Domain assumptions")."""

    __tablename__ = "practitioners"

    id: int | None = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="category.id")
    district_id: int = Field(foreign_key="district.id")
    place_id: str | None = None
    phone_numbers: list[str] = Field(
        default_factory=list, sa_column=Column(JSONB, nullable=False)
    )
    member_exclusive_fee: int | None = None
    consultation_fee: int
    is_open_on_public_holidays: bool = False
    name_en: str
    name_yue: str
    name_zh: str
    address_en: str
    address_yue: str
    address_zh: str
    fee_detail_en: str | None = None
    fee_detail_yue: str | None = None
    fee_detail_zh: str | None = None

    category: "Category" = Relationship(back_populates="practitioners")
    district: "District" = Relationship(back_populates="practitioners")
    operating_hours: list["OperatingHour"] = Relationship(
        back_populates="practitioner", cascade_delete=True
    )
