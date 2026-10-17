"""Mappers for practitioner translations."""

from necktie.models import PractitionerTranslation
from necktie.schemas import DoctorTranslationIn


def to_translation_orm(t: DoctorTranslationIn) -> PractitionerTranslation:
    """Build a PractitionerTranslation ORM object from create payload."""
    return PractitionerTranslation(
        language_code=t.language_code,
        name=t.name,
        address=t.address,
        fee_detail=t.fee_detail,
    )
