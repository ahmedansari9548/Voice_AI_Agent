from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.dependencies import get_patient_service
from app.schemas.patient import DeleteResponse
from app.services.patient_service import PatientService

router = APIRouter()


@router.delete("/patients/{patient_id}", response_model=DeleteResponse)
def delete_patient(
    patient_id: UUID,
    service: PatientService = Depends(get_patient_service),
):
    result = service.delete(patient_id)
    return {"data": result, "error": None}
