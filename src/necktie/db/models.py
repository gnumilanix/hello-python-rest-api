"""SQLModel ORM models for the necktie database.

Translatable fields live in dedicated ``*_translations`` tables keyed by
(parent_id, language_code) so the API can serve multiple languages.
"""

from datetime import time

from sqlalchemy import CheckConstraint, Text
from sqlmodel import Field, Relationship, SQLModel

LANGUAGE_CODE_LENGTH = 10


class District(SQLModel, table=True):
    __tablename__ = "district"

    id: int | None = Field(default=None, primary_key=True)
    sort_order: int

    translations: list["DistrictTranslation"] = Relationship(
        back_populates="district", cascade_delete=True
    )
    practitioners: list["Practitioner"] = Relationship(back_populates="district")


class DistrictTranslation(SQLModel, table=True):
    __tablename__ = "district_translations"

    district_id: int = Field(
        foreign_key="district.id", primary_key=True, ondelete="CASCADE"
    )
    language_code: str = Field(max_length=LANGUAGE_CODE_LENGTH, primary_key=True)
    name: str

    district: District | None = Relationship(back_populates="translations")


class Category(SQLModel, table=True):
    __tablename__ = "category"

    id: int | None = Field(default=None, primary_key=True)
    name_key: str = Field(unique=True)

    translations: list["CategoryTranslation"] = Relationship(
        back_populates="category", cascade_delete=True
    )
    practitioners: list["Practitioner"] = Relationship(back_populates="category")


class CategoryTranslation(SQLModel, table=True):
    __tablename__ = "category_translations"

    category_id: int = Field(
        foreign_key="category.id", primary_key=True, ondelete="CASCADE"
    )
    language_code: str = Field(max_length=LANGUAGE_CODE_LENGTH, primary_key=True)
    name: str

    category: Category | None = Relationship(back_populates="translations")


class Practitioner(SQLModel, table=True):
    """A practitioner listing.

    A practitioner with multiple clinics is intentionally stored as one row
    per clinic (name clashes make deduplication unreliable), so there is no
    separate clinic table.
    """

    __tablename__ = "practitioners"

    id: int | None = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="category.id")
    district_id: int = Field(foreign_key="district.id")
    place_id: str | None = None  # Google Places ID
    # Comma-separated in the DB; use ``phone_number_list`` for a list view.
    phone_numbers: str | None = None
    is_active: bool = True
    member_exclusive_fee: int | None = None
    consultation_fee: int | None = None
    # HK clinics either open or close on public holidays as a whole,
    # regardless of the weekday a holiday falls on.
    is_open_on_public_holidays: bool = False

    category: Category | None = Relationship(back_populates="practitioners")
    district: District | None = Relationship(back_populates="practitioners")
    translations: list["PractitionerTranslation"] = Relationship(
        back_populates="practitioner", cascade_delete=True
    )
    operating_hours: list["OperatingHour"] = Relationship(
        back_populates="practitioner", cascade_delete=True
    )

    @property
    def phone_number_list(self) -> list[str]:
        """Return phone numbers as a list (stored comma-separated)."""
        if not self.phone_numbers:
            return []
        return [p.strip() for p in self.phone_numbers.split(",") if p.strip()]


class PractitionerTranslation(SQLModel, table=True):
    __tablename__ = "practitioners_translations"

    practitioner_id: int = Field(
        foreign_key="practitioners.id", primary_key=True, ondelete="CASCADE"
    )
    language_code: str = Field(max_length=LANGUAGE_CODE_LENGTH, primary_key=True)
    name: str
    address: str = Field(sa_type=Text)
    fee_detail: str | None = Field(default=None, sa_type=Text)

    practitioner: Practitioner | None = Relationship(back_populates="translations")


class OperatingHour(SQLModel, table=True):
    """One open/close interval for a practitioner.

    day_of_week follows ISO 8601: 1 = Monday, 7 = Sunday.
    """

    __tablename__ = "operating_hours"
    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 1 AND 7", name="ck_day_of_week"),
    )

    id: int | None = Field(default=None, primary_key=True)
    practitioner_id: int = Field(foreign_key="practitioners.id", ondelete="CASCADE")
    day_of_week: int
    open_time: time
    close_time: time

    practitioner: Practitioner | None = Relationship(back_populates="operating_hours")
