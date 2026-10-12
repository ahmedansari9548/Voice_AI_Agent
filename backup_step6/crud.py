from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Patient
from .schemas import PatientCreate


def create_patient(db: Session, payload: PatientCreate) -> Patient:
    patient = Patient(**payload.model_dump(mode="python"))
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def get_patient(db: Session, patient_id: UUID) -> Patient | None:
    return db.scalar(
        select(Patient).where(
            Patient.patient_id == patient_id,
            Patient.deleted_at.is_(None),
        )
    )


def list_patients(
    db: Session,
    last_name: str | None = None,
    date_of_birth: date | None = None,
    phone_number: str | None = None,
) -> list[Patient]:
    stmt = select(Patient).where(Patient.deleted_at.is_(None))

    if last_name is not None:
        stmt = stmt.where(Patient.last_name.ilike(last_name))
    if date_of_birth is not None:
        stmt = stmt.where(Patient.date_of_birth == date_of_birth)
    if phone_number is not None:
        stmt = stmt.where(Patient.phone_number == phone_number)

    stmt = stmt.order_by(Patient.created_at.desc()).limit(100)
    return list(db.scalars(stmt).all())


def update_patient(
    db: Session,
    patient: Patient,
    payload: PatientCreate,
) -> Patient:
    for key, value in payload.model_dump(mode="python").items():
        setattr(patient, key, value)

    patient.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(patient)
    return patient


def delete_patient(db: Session, patient: Patient) -> None:
    now = datetime.now(timezone.utc)
    patient.deleted_at = now
    patient.updated_at = now
    db.commit()
