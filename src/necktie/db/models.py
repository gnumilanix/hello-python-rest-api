"""SQLAlchemy ORM models for the necktie database.

Translatable fields live in dedicated ``*_translations`` tables keyed by
(parent_id, language_code) so the API can serve multiple languages.
"""

from datetime import time

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from necktie.db.base import Base

LANGUAGE_CODE_LENGTH = 10


class District(Base):
    __tablename__ = "district"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sort_order: Mapped[int] = mapped_column(Integer)

    translations: Mapped[list["DistrictTranslation"]] = relationship(
        back_populates="district", cascade="all, delete-orphan"
    )
    practitioners: Mapped[list["Practitioner"]] = relationship(
        back_populates="district"
    )


class DistrictTranslation(Base):
    __tablename__ = "district_translations"

    district_id: Mapped[int] = mapped_column(
        ForeignKey("district.id", ondelete="CASCADE"), primary_key=True
    )
    language_code: Mapped[str] = mapped_column(
        String(LANGUAGE_CODE_LENGTH), primary_key=True
    )
    name: Mapped[str] = mapped_column(Text)

    district: Mapped[District] = relationship(back_populates="translations")


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_key: Mapped[str] = mapped_column(Text, unique=True)

    translations: Mapped[list["CategoryTranslation"]] = relationship(
        back_populates="category", cascade="all, delete-orphan"
    )
    practitioners: Mapped[list["Practitioner"]] = relationship(
        back_populates="category"
    )


class CategoryTranslation(Base):
    __tablename__ = "category_translations"

    category_id: Mapped[int] = mapped_column(
        ForeignKey("category.id", ondelete="CASCADE"), primary_key=True
    )
    language_code: Mapped[str] = mapped_column(
        String(LANGUAGE_CODE_LENGTH), primary_key=True
    )
    name: Mapped[str] = mapped_column(Text)

    category: Mapped[Category] = relationship(back_populates="translations")


class Practitioner(Base):
    """A practitioner listing.

    A practitioner with multiple clinics is intentionally stored as one row
    per clinic (name clashes make deduplication unreliable), so there is no
    separate clinic table.
    """

    __tablename__ = "practitioners"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    district_id: Mapped[int] = mapped_column(ForeignKey("district.id"))
    place_id: Mapped[str | None] = mapped_column(Text)  # Google Places ID
    phone_numbers: Mapped[str | None] = mapped_column(Text)  # comma-separated
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    member_exclusive_fee: Mapped[int | None] = mapped_column(Integer)
    consultation_fee: Mapped[int | None] = mapped_column(Integer)
    # HK clinics either open or close on public holidays as a whole,
    # regardless of the weekday a holiday falls on.
    is_open_on_public_holidays: Mapped[bool] = mapped_column(
        Boolean, default=False
    )

    category: Mapped[Category] = relationship(back_populates="practitioners")
    district: Mapped[District] = relationship(back_populates="practitioners")
    translations: Mapped[list["PractitionerTranslation"]] = relationship(
        back_populates="practitioner", cascade="all, delete-orphan"
    )
    operating_hours: Mapped[list["OperatingHour"]] = relationship(
        back_populates="practitioner", cascade="all, delete-orphan"
    )

    @property
    def phone_number_list(self) -> list[str]:
        """Return phone numbers as a list (stored comma-separated)."""
        if not self.phone_numbers:
            return []
        return [p.strip() for p in self.phone_numbers.split(",") if p.strip()]


class PractitionerTranslation(Base):
    __tablename__ = "practitioners_translations"

    practitioner_id: Mapped[int] = mapped_column(
        ForeignKey("practitioners.id", ondelete="CASCADE"), primary_key=True
    )
    language_code: Mapped[str] = mapped_column(
        String(LANGUAGE_CODE_LENGTH), primary_key=True
    )
    name: Mapped[str] = mapped_column(Text)
    address: Mapped[str] = mapped_column(Text)
    fee_detail: Mapped[str | None] = mapped_column(Text)

    practitioner: Mapped[Practitioner] = relationship(
        back_populates="translations"
    )


class OperatingHour(Base):
    """One open/close interval for a practitioner.

    day_of_week follows ISO 8601: 1 = Monday, 7 = Sunday.
    """

    __tablename__ = "operating_hours"
    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 1 AND 7", name="ck_day_of_week"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    practitioner_id: Mapped[int] = mapped_column(
        ForeignKey("practitioners.id", ondelete="CASCADE")
    )
    day_of_week: Mapped[int] = mapped_column(Integer)
    open_time: Mapped[time] = mapped_column(Time)
    close_time: Mapped[time] = mapped_column(Time)

    practitioner: Mapped[Practitioner] = relationship(
        back_populates="operating_hours"
    )
