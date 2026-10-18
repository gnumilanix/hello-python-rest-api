"""Query helpers for practitioner routes."""

from sqlalchemy.orm import selectinload, with_loader_criteria

from necktie.models import Practitioner, PractitionerTranslation


def with_practitioner_relations(stmt):
    """Eager-load all relationships needed to serialize a practitioner."""
    return stmt.options(
        selectinload(Practitioner.translations),
        selectinload(Practitioner.operating_hours),
    )


def with_localized_relations(stmt, language: str):
    """Eager-load only the translation rows matching ``language``.

    Narrows the loaded translations at query time so unrelated language rows
    are not fetched for localized responses.
    """
    return stmt.options(
        selectinload(Practitioner.translations),
        selectinload(Practitioner.operating_hours),
        with_loader_criteria(
            PractitionerTranslation,
            PractitionerTranslation.language_code == language,
        ),
    )
