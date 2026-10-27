"""Business logic for the doctor resource."""

from necktie.mappers import DoctorMapper, to_doctor_orm
from necktie.mappers.operating_hour import to_operating_hour_orm
from necktie.models import Doctor as DoctorEntity
from necktie.repositories import DoctorRepository
from necktie.schemas import Doctor, DoctorCreate
from necktie.schemas.doctor import DoctorPatch
from necktie.services.category import CategoryService
from necktie.services.district import DistrictService
from necktie.utils.languages import Language


class DoctorNotFoundError(Exception):
    """Raised when a doctor id does not exist."""


class CategoryNotFoundError(Exception):
    """Raised when a category id does not exist."""


class DistrictNotFoundError(Exception):
    """Raised when a district id does not exist."""


class DoctorService:
    """Coordinates repository access, catalog-backed mapping, and writes."""

    def __init__(
        self,
        repository: DoctorRepository,
        districts: DistrictService,
        categories: CategoryService,
    ) -> None:
        self.repo = repository
        self.districts = districts
        self.categories = categories
        self.mapper = DoctorMapper(districts, categories)

    async def list_doctors(
        self,
        language: Language,
        district_id: int | None,
        category_id: int | None,
        min_fee: int | None,
        max_fee: int | None,
        offset: int,
        limit: int,
    ) -> list[Doctor]:
        """List doctors localized to ``language``, paginated."""
        doctors = await self.repo.find_all(
            language,
            district_id,
            category_id,
            min_fee,
            max_fee,
            offset,
            limit,
        )
        return [await self.mapper.to_doctor(p, language) for p in doctors]

    async def get_doctor(self, doctor_id: int, language: Language) -> Doctor:
        """Get one doctor localized, raising DoctorNotFoundError if missing."""
        doctor = await self.repo.find_by_id_localized(doctor_id, language)
        if doctor is None:
            raise DoctorNotFoundError(doctor_id)
        return await self.mapper.to_doctor(doctor, language)

    async def create_doctor(self, payload: DoctorCreate) -> Doctor:
        """Create one doctor."""
        await self._validate(payload)
        doctor = await self._save(payload)
        return await self.mapper.to_doctor(doctor, Language.default())

    async def create_doctors_batch(self, payloads: list[DoctorCreate]) -> list[Doctor]:
        """Create many doctors in one transaction."""
        for payload in payloads:
            await self._validate(payload)
        doctors = await self._save_all(payloads)
        return [await self.mapper.to_doctor(d, Language.default()) for d in doctors]

    async def update_doctor(
        self, doctor_id: int, payload: DoctorCreate | DoctorPatch
    ) -> Doctor:
        """Replace a listing or update only supplied fields in one transaction."""
        doctor = await self.repo.find_by_id(doctor_id)
        if doctor is None:
            raise DoctorNotFoundError(doctor_id)
        await self._validate(payload)
        changes = payload.model_dump(exclude_unset=isinstance(payload, DoctorPatch))
        hours_supplied = "operating_hours" in changes
        changes.pop("operating_hours", None)
        for field in ("name", "address", "fee_detail"):
            if field in changes:
                translations = changes.pop(field)
                if translations is None:
                    translations = dict.fromkeys(("en", "yue", "zh"))
                changes.update(
                    {
                        f"{field}_{language}": value
                        for language, value in translations.items()
                    }
                )
        doctor.sqlmodel_update(changes)
        if hours_supplied:
            doctor.operating_hours = [
                to_operating_hour_orm(hour) for hour in payload.operating_hours or []
            ]
        await self.repo.commit()
        return await self.mapper.to_doctor(doctor, Language.default())

    async def delete_doctor(self, doctor_id: int) -> None:
        """Delete an existing listing and its operating hours."""
        doctor = await self.repo.find_by_id(doctor_id)
        if doctor is None:
            raise DoctorNotFoundError(doctor_id)
        await self.repo.delete(doctor)
        await self.repo.commit()

    async def _validate(self, payload: DoctorCreate | DoctorPatch) -> None:
        """Check the referenced category and district against the catalogs."""
        if payload.category_id is not None and not await self.categories.exists(
            payload.category_id
        ):
            raise CategoryNotFoundError(payload.category_id)
        if payload.district_id is not None and not await self.districts.exists(
            payload.district_id
        ):
            raise DistrictNotFoundError(payload.district_id)

    async def _save(self, payload: DoctorCreate) -> DoctorEntity:
        """Build and insert one doctor."""
        doctor = to_doctor_orm(payload)
        self.repo.add_all([doctor])
        await self.repo.commit()
        return doctor

    async def _save_all(self, payloads: list[DoctorCreate]) -> list[DoctorEntity]:
        """Build and insert many doctors in one transaction."""
        doctors = [to_doctor_orm(p) for p in payloads]
        self.repo.add_all(doctors)
        await self.repo.commit()
        return doctors
