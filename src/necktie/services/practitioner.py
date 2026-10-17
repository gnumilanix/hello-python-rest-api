"""Business logic for the doctor resource."""

from necktie.mappers import to_detail, to_list_item
from necktie.models import OperatingHour, Practitioner, PractitionerTranslation
from necktie.repositories import PractitionerRepository
from necktie.schemas import DoctorCreate, DoctorDetail, DoctorListItem


class PractitionerNotFoundError(Exception):
    """Raised when a practitioner id does not exist."""


class CategoryNotFoundError(Exception):
    """Raised when a category id does not exist."""


class DistrictNotFoundError(Exception):
    """Raised when a district id does not exist."""


class PractitionerService:
    """Coordinates repository access and ORM→schema mapping."""

    def __init__(self, repository: PractitionerRepository) -> None:
        self.repo = repository

    def list_doctors(
        self,
        district_id: int | None = None,
        category_id: int | None = None,
        min_fee: int | None = None,
        max_fee: int | None = None,
        language: str = "en-US",
    ) -> list[DoctorListItem]:
        """List doctors localized to ``language``."""
        doctors = self.repo.find_all(
            district_id=district_id,
            category_id=category_id,
            min_fee=min_fee,
            max_fee=max_fee,
        )
        return [to_list_item(p, language) for p in doctors]

    def get_doctor(self, doctor_id: int) -> DoctorDetail:
        """Get one doctor, raising PractitionerNotFoundError if missing."""
        doctor = self.repo.find_by_id(doctor_id)
        if doctor is None:
            raise PractitionerNotFoundError(doctor_id)
        return to_detail(doctor)

    def create_doctor(self, payload: DoctorCreate) -> DoctorDetail:
        """Create one doctor."""
        doctor = self._build(payload)
        self.repo.add(doctor)
        self.repo.commit()
        return to_detail(doctor)

    def create_doctors_batch(
        self, payloads: list[DoctorCreate]
    ) -> list[DoctorDetail]:
        """Create many doctors in one transaction."""
        doctors = [self._build(p) for p in payloads]
        for d in doctors:
            self.repo.add(d)
        self.repo.commit()
        return [to_detail(d) for d in doctors]

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
            phone_numbers=", ".join(payload.phone_numbers) or None,
            is_active=payload.is_active,
            member_exclusive_fee=payload.member_exclusive_fee,
            consultation_fee=payload.consultation_fee,
            is_open_on_public_holidays=payload.is_open_on_public_holidays,
            translations=[
                PractitionerTranslation(
                    language_code=t.language_code,
                    name=t.name,
                    address=t.address,
                    fee_detail=t.fee_detail,
                )
                for t in payload.translations
            ],
            operating_hours=[
                OperatingHour(
                    day_of_week=oh.day_of_week,
                    open_time=oh.open_time,
                    close_time=oh.close_time,
                )
                for oh in payload.opening_hours
            ],
        )
