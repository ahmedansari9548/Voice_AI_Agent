from datetime import date

from fastapi import APIRouter, Depends

from app.api.dependencies import get_patient_service
from app.schemas.patient import PatientListResponse
from app.services.patient_service import PatientService

router = APIRouter()


@router.get("/patients", response_model=PatientListResponse)
def list_patients(
    last_name: str | None = None,
    date_of_birth: date | None = None,
    phone_number: str | None = None,
    service: PatientService = Depends(get_patient_service),
):
    patients = service.list(
        last_name=last_name,
        date_of_birth=date_of_birth,
        phone_number=phone_number,
    )
    return {"data": patients, "error": None}
