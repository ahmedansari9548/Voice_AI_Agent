from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.patient_service import PatientService


def get_patient_service(
    db: Session = Depends(get_db),
) -> PatientService:
    return PatientService(db)
