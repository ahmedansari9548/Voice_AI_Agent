from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.patient import Patient


class PatientRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, values: dict) -> Patient:
        patient = Patient(**values)
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def get(self, patient_id: UUID) -> Patient | None:
        return self.db.scalar(
            select(Patient).where(
                Patient.patient_id == patient_id,
                Patient.deleted_at.is_(None),
            )
        )

    def list(
        self,
        last_name: str | None = None,
        date_of_birth: date | None = None,
        phone_number: str | None = None,
    ) -> list[Patient]:
        query = select(Patient).where(Patient.deleted_at.is_(None))

        if last_name:
            query = query.where(Patient.last_name.ilike(last_name))
        if date_of_birth:
            query = query.where(Patient.date_of_birth == date_of_birth)
        if phone_number:
            query = query.where(Patient.phone_number == phone_number)

        query = query.order_by(Patient.created_at.desc()).limit(100)
        return list(self.db.scalars(query).all())

    def update(self, patient: Patient, values: dict) -> Patient:
        for field, value in values.items():
            setattr(patient, field, value)

        patient.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def soft_delete(self, patient: Patient) -> None:
        now = datetime.now(timezone.utc)
        patient.deleted_at = now
        patient.updated_at = now
        self.db.commit()
