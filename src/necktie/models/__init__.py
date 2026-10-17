"""SQLModel ORM models, one class per module.

Translatable fields live in dedicated ``*_translations`` tables keyed by
(parent_id, language_code) so the API can serve multiple languages.
"""

from necktie.models.category import Category
from necktie.models.category_translation import CategoryTranslation
from necktie.models.district import District
from necktie.models.district_translation import DistrictTranslation
from necktie.models.operating_hour import OperatingHour
from necktie.models.practitioner import Practitioner
from necktie.models.practitioner_translation import PractitionerTranslation

__all__ = [
    "Category",
    "CategoryTranslation",
    "District",
    "DistrictTranslation",
    "OperatingHour",
    "Practitioner",
    "PractitionerTranslation",
]
