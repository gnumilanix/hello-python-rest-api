"""Query helpers for practitioner routes."""

from sqlalchemy.orm import selectinload, with_loader_criteria

from necktie.models import (
    Category,
    CategoryTranslation,
    District,
    DistrictTranslation,
    Practitioner,
    PractitionerTranslation,
)


def with_practitioner_relations(stmt):
    """Eager-load all relationships needed to serialize a practitioner."""
    return stmt.options(
        selectinload(Practitioner.translations),
        selectinload(Practitioner.operating_hours),
        selectinload(Practitioner.category).selectinload(Category.translations),
        selectinload(Practitioner.district).selectinload(District.translations),
    )


def with_localized_relations(stmt, language: str):
    """Eager-load only the translation rows matching ``language``.

    Narrows the loaded translations at query time so unrelated language rows
    are not fetched for localized responses.
    """
    return stmt.options(
        selectinload(Practitioner.translations),
        selectinload(Practitioner.operating_hours),
        selectinload(Practitioner.category).selectinload(Category.translations),
        selectinload(Practitioner.district).selectinload(District.translations),
        with_loader_criteria(
            PractitionerTranslation,
            PractitionerTranslation.language_code == language,
        ),
        with_loader_criteria(
            CategoryTranslation, CategoryTranslation.language_code == language
        ),
        with_loader_criteria(
            DistrictTranslation, DistrictTranslation.language_code == language
        ),
    )
