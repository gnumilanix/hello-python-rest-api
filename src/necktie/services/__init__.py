"""Services, one module per aggregate."""

from necktie.services.practitioner import (
    CategoryNotFoundError,
    DistrictNotFoundError,
    PractitionerNotFoundError,
    PractitionerService,
)

__all__ = [
    "CategoryNotFoundError",
    "DistrictNotFoundError",
    "PractitionerNotFoundError",
    "PractitionerService",
]
