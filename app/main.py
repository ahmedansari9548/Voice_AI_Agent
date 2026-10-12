import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.api.router import api_router
from app.core.exceptions import (
    not_found_handler,
    patient_validation_handler,
    request_validation_handler,
    database_error_handler,
    general_error_handler,
)
from app.core.security import api_key_middleware
from app.services.patient_service import (
    PatientNotFound,
    PatientValidationFailed,
)

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Voice AI Patient Registration API",
    version="1.0.0",
    description="Modular patient registration system with Vapi integration",
)

app.middleware("http")(api_key_middleware)

app.add_exception_handler(PatientNotFound, not_found_handler)
app.add_exception_handler(
    PatientValidationFailed, patient_validation_handler
)
app.add_exception_handler(
    RequestValidationError, request_validation_handler
)
app.add_exception_handler(SQLAlchemyError, database_error_handler)
app.add_exception_handler(Exception, general_error_handler)

app.include_router(api_router)


@app.get("/health", tags=["System"])
def health():
    return {"data": {"status": "ok"}, "error": None}
