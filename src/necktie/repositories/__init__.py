"""Repositories, one module per aggregate."""

from necktie.repositories.category import CategoryRepository
from necktie.repositories.district import DistrictRepository
from necktie.repositories.doctor import DoctorRepository

__all__ = ["CategoryRepository", "DistrictRepository", "DoctorRepository"]
