from fastapi import APIRouter
from app.api.endpoints import vapi_webhook


from app.api.endpoints import (
    create_patient,
    list_patients,
    get_patient,
    update_patient,
    delete_patient,
)

api_router = APIRouter()

api_router.include_router(create_patient.router, tags=["Registration"])
api_router.include_router(list_patients.router, tags=["Patients"])
api_router.include_router(get_patient.router, tags=["Patients"])
api_router.include_router(update_patient.router, tags=["Patients"])
api_router.include_router(delete_patient.router, tags=["Patients"])
api_router.include_router(vapi_webhook.router,tags=["Voice Integration"])