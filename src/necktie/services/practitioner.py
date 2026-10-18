"""Business logic for the doctor resource."""

from starlette.concurrency import run_in_threadpool

from necktie.mappers import PractitionerMapper, to_operating_hour_orm
from necktie.models import Practitioner
from necktie.repositories import PractitionerRepository
from necktie.schemas import Doctor, DoctorCreate, DoctorDetail
from necktie.services.category import CategoryService
from necktie.services.district import DistrictService
from necktie.utils.languages import Language


class PractitionerNotFoundError(Exception):
    """Raised when a practitioner id does not exist."""


class CategoryNotFoundError(Exception):
    """Raised when a category id does not exist."""


class DistrictNotFoundError(Exception):
    """Raised when a district id does not exist."""


class PractitionerService:
    """Coordinates repository access, catalog-backed mapping, and writes."""

    def __init__(
        self,
        repository: PractitionerRepository,
        districts: DistrictService,
        categories: CategoryService,
    ) -> None:
        self.repo = repository
        self.districts = districts
        self.categories = categories
        self.mapper = PractitionerMapper(districts, categories)

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
        doctors = await run_in_threadpool(
            self.repo.find_all,
            district_id,
            category_id,
            min_fee,
            max_fee,
            offset,
            limit,
        )
        return [await self.mapper.to_detail(p) for p in doctors]

    async def get_doctor(self, doctor_id: int, language: Language) -> Doctor:
        """Get one doctor localized, raising PractitionerNotFoundError if missing."""
        doctor = await run_in_threadpool(self.repo.find_by_id, doctor_id)
        if doctor is None:
            raise PractitionerNotFoundError(doctor_id)
        return await self.mapper.to_doctor(doctor, language)

    async def create_doctor(self, payload: DoctorCreate) -> DoctorDetail:
        """Create one doctor."""
        await self._validate(payload)
        doctor = await run_in_threadpool(self._save, payload)
        return await self.mapper.to_detail(doctor)

    async def create_doctors_batch(
        self, payloads: list[DoctorCreate]
    ) -> list[DoctorDetail]:
        """Create many doctors in one transaction."""
        for payload in payloads:
            await self._validate(payload)
        doctors = await run_in_threadpool(self._save_all, payloads)
        return [await self.mapper.to_detail(d) for d in doctors]

    async def _validate(self, payload: DoctorCreate) -> None:
        """Check the referenced category and district against the catalogs."""
        if not await self.categories.exists(payload.category_id):
            raise CategoryNotFoundError(payload.category_id)
        if not await self.districts.exists(payload.district_id):
            raise DistrictNotFoundError(payload.district_id)

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
        """Build the ORM object (references validated beforehand by _validate)."""
        return Practitioner(
            category_id=payload.category_id,
            district_id=payload.district_id,
            place_id=payload.place_id,
            phone_numbers=payload.phone_numbers,
            member_exclusive_fee=payload.member_exclusive_fee,
            consultation_fee=payload.consultation_fee,
            is_open_on_public_holidays=payload.is_open_on_public_holidays,
            name_en=payload.name.en,
            name_yue=payload.name.yue,
            name_zh=payload.name.zh,
            address_en=payload.address.en,
            address_yue=payload.address.yue,
            address_zh=payload.address.zh,
            fee_detail_en=payload.fee_detail.en,
            fee_detail_yue=payload.fee_detail.yue,
            fee_detail_zh=payload.fee_detail.zh,
            operating_hours=[
                to_operating_hour_orm(oh) for oh in payload.operating_hours
            ],
        )
