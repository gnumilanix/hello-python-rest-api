"""SQLModel ORM models, one class per module.

Translatable fields are fixed per-language columns (en/yue/zh); the product
serves Hong Kong only, so the language set is closed.
"""

from necktie.models.category import Category
from necktie.models.district import District
from necktie.models.doctor import Doctor
from necktie.models.operating_hour import OperatingHour

__all__ = [
    "Category",
    "District",
    "OperatingHour",
    "Doctor",
]
