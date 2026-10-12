from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.dependencies import get_patient_service
from app.schemas.patient import PatientResponse
from app.services.patient_service import PatientService

router = APIRouter()


@router.get("/patients/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: UUID,
    service: PatientService = Depends(get_patient_service),
):
    patient = service.get(patient_id)
    return {"data": patient, "error": None}
