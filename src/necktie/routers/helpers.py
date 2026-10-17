"""Query helpers for practitioner routes."""

from sqlalchemy.orm import selectinload

from necktie.models import Category, District, Practitioner


def with_practitioner_relations(stmt):
    """Eager-load all relationships needed to serialize a practitioner."""
    return stmt.options(
        selectinload(Practitioner.translations),
        selectinload(Practitioner.operating_hours),
        selectinload(Practitioner.category).selectinload(Category.translations),
        selectinload(Practitioner.district).selectinload(District.translations),
    )
