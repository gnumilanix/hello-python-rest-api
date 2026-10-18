"""Business logic for the doctor resource."""

import asyncio

from starlette.concurrency import run_in_threadpool

from necktie.mappers import (
    CategoryCatalogEntry,
    DistrictCatalogEntry,
    to_detail,
    to_doctor,
    to_operating_hour_orm,
    to_translation_orm,
)
from necktie.models import Practitioner
from necktie.repositories import PractitionerRepository
from necktie.schemas import Doctor, DoctorCreate, DoctorDetail
from necktie.services.category import CategoryService
from necktie.services.district import DistrictService


class PractitionerNotFoundError(Exception):
    """Raised when a practitioner id does not exist."""


class CategoryNotFoundError(Exception):
    """Raised when a category id does not exist."""


class DistrictNotFoundError(Exception):
    """Raised when a district id does not exist."""


class PractitionerService:
    """Coordinates repository access, cached catalogs, and ORM→schema mapping."""

    def __init__(
        self,
        repository: PractitionerRepository,
        districts: DistrictService,
        categories: CategoryService,
    ) -> None:
        self.repo = repository
        self.districts = districts
        self.categories = categories

    async def list_doctors(
        self,
        district_id: int | None,
        category_id: int | None,
        min_fee: int | None,
        max_fee: int | None,
        offset: int,
        limit: int,
    ) -> list[DoctorDetail]:
        """List doctors with all translations, paginated."""
        districts, categories = await self._catalogs()
        doctors = await run_in_threadpool(
            self.repo.find_all,
            district_id,
            category_id,
            min_fee,
            max_fee,
            offset,
            limit,
        )
        return [to_detail(p, categories, districts) for p in doctors]

    async def get_doctor(self, doctor_id: int, language: str) -> Doctor:
        """Get one doctor localized, raising PractitionerNotFoundError if missing."""
        districts, categories = await self._catalogs()
        doctor = await run_in_threadpool(
            self.repo.find_by_id_localized, doctor_id, language
        )
        if doctor is None:
            raise PractitionerNotFoundError(doctor_id)
        return to_doctor(doctor, language, categories, districts)

    async def create_doctor(self, payload: DoctorCreate) -> DoctorDetail:
        """Create one doctor."""
        doctor = await run_in_threadpool(self._save, payload)
        districts, categories = await self._catalogs()
        return to_detail(doctor, categories, districts)

    async def create_doctors_batch(
        self, payloads: list[DoctorCreate]
    ) -> list[DoctorDetail]:
        """Create many doctors in one transaction."""
        doctors = await run_in_threadpool(self._save_all, payloads)
        districts, categories = await self._catalogs()
        return [to_detail(d, categories, districts) for d in doctors]

    async def _catalogs(
        self,
    ) -> tuple[dict[int, DistrictCatalogEntry], dict[int, CategoryCatalogEntry]]:
        """Fetch the district and category catalogs concurrently."""
        districts, categories = await asyncio.gather(
            self.districts.get_translated_map(),
            self.categories.get_translated_map(),
        )
        return districts, categories

    def _save(self, payload: DoctorCreate) -> Practitioner:
        """Build and insert one doctor (runs in a worker thread)."""
        doctor = self._build(payload)
        self.repo.add_all([doctor])
        self.repo.commit()
        return doctor

    def _save_all(self, payloads: list[DoctorCreate]) -> list[Practitioner]:
        """Build and insert many doctors in one transaction (worker thread)."""
        doctors = [self._build(p) for p in payloads]
        self.repo.add_all(doctors)
        self.repo.commit()
        return doctors

    def _build(self, payload: DoctorCreate) -> Practitioner:
        """Validate references and build the ORM object."""
        if not self.repo.category_exists(payload.category_id):
            raise CategoryNotFoundError(payload.category_id)
        if not self.repo.district_exists(payload.district_id):
            raise DistrictNotFoundError(payload.district_id)
        return Practitioner(
            category_id=payload.category_id,
            district_id=payload.district_id,
            place_id=payload.place_id,
            phone_numbers=payload.phone_numbers,
            member_exclusive_fee=payload.member_exclusive_fee,
            consultation_fee=payload.consultation_fee,
            is_open_on_public_holidays=payload.is_open_on_public_holidays,
            translations=[to_translation_orm(t) for t in payload.translations],
            operating_hours=[
                to_operating_hour_orm(oh) for oh in payload.operating_hours
            ],
        )
