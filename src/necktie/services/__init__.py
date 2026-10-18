"""Services, one module per aggregate."""

from necktie.services.doctor import (
    CategoryNotFoundError,
    DistrictNotFoundError,
    DoctorNotFoundError,
    DoctorService,
)

__all__ = [
    "CategoryNotFoundError",
    "DistrictNotFoundError",
    "DoctorNotFoundError",
    "DoctorService",
]
