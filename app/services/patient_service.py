from datetime import date
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.repositories.patient_repository import PatientRepository
from app.schemas.patient import PatientCreate, PatientUpdate


class PatientNotFound(Exception):
    pass


class PatientValidationFailed(Exception):
    def __init__(self, errors):
        self.errors = errors


class PatientService:
    def __init__(self, db: Session):
        self.repository = PatientRepository(db)

    def create(self, payload: PatientCreate):
        return self.repository.create(payload.model_dump(mode="python"))

    def get(self, patient_id: UUID):
        patient = self.repository.get(patient_id)
        if patient is None:
            raise PatientNotFound("Patient not found")
        return patient

    def list(
        self,
        last_name: str | None = None,
        date_of_birth: date | None = None,
        phone_number: str | None = None,
    ):
        return self.repository.list(
            last_name=last_name,
            date_of_birth=date_of_birth,
            phone_number=phone_number,
        )

    def update(self, patient_id: UUID, updates: PatientUpdate):
        patient = self.get(patient_id)

        current = {
            field: getattr(patient, field)
            for field in PatientCreate.model_fields
        }
        changes = updates.model_dump(exclude_unset=True)

        try:
            validated = PatientCreate.model_validate(
                {**current, **changes}
            )
        except ValidationError as exc:
            raise PatientValidationFailed(exc.errors()) from exc

        return self.repository.update(
            patient,
            validated.model_dump(mode="python"),
        )

    def delete(self, patient_id: UUID):
        patient = self.get(patient_id)
        self.repository.soft_delete(patient)
        return {
            "patient_id": str(patient_id),
            "deleted": True,
        }
