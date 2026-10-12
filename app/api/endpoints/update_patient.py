from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.dependencies import get_patient_service
from app.schemas.patient import PatientUpdate, PatientResponse
from app.services.patient_service import PatientService

router = APIRouter()


@router.put("/patients/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: UUID,
    payload: PatientUpdate,
    service: PatientService = Depends(get_patient_service),
):
    patient = service.update(patient_id, payload)
    return {"data": patient, "error": None}
