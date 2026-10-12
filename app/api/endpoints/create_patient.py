from fastapi import APIRouter, Depends

from app.api.dependencies import get_patient_service
from app.schemas.patient import PatientCreate, PatientResponse
from app.services.patient_service import PatientService

router = APIRouter()


@router.post("/patients", status_code=201, response_model=PatientResponse)
def create_patient(
    payload: PatientCreate,
    service: PatientService = Depends(get_patient_service),
):
    patient = service.create(payload)
    return {"data": patient, "error": None}
