"""Practitioner ORM model."""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from necktie.models.category import Category
    from necktie.models.district import District
    from necktie.models.operating_hour import OperatingHour
    from necktie.models.practitioner_translation import PractitionerTranslation


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
    member_exclusive_fee: int | None = None
    consultation_fee: int | None = None
    # HK clinics either open or close on public holidays as a whole,
    # regardless of the weekday a holiday falls on.
    is_open_on_public_holidays: bool = False

    category: "Category" = Relationship(back_populates="practitioners")
    district: "District" = Relationship(back_populates="practitioners")
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
