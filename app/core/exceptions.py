import logging

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.services.patient_service import (
    PatientNotFound,
    PatientValidationFailed,
)

logger = logging.getLogger(__name__)


def error_response(status, code, message, details=None):
    return JSONResponse(
        status_code=status,
        content={
            "data": None,
            "error": {
                "code": code,
                "message": message,
                "details": jsonable_encoder(details),
            },
        },
    )


def validation_details(errors):
    return [
        {
            "field": ".".join(map(str, e["loc"])),
            "message": e["msg"],
        }
        for e in errors
    ]


async def not_found_handler(request: Request, exc: PatientNotFound):
    return error_response(404, "NOT_FOUND", str(exc))


async def patient_validation_handler(
    request: Request, exc: PatientValidationFailed
):
    return error_response(
        422, "VALIDATION_ERROR",
        "Invalid patient update",
        validation_details(exc.errors),
    )


async def request_validation_handler(
    request: Request, exc: RequestValidationError
):
    return error_response(
        422, "VALIDATION_ERROR",
        "Invalid request",
        validation_details(exc.errors()),
    )


async def database_error_handler(request: Request, exc: SQLAlchemyError):
    logger.exception("Database operation failed")
    return error_response(
        500, "DATABASE_ERROR", "Database operation failed"
    )


async def general_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled application error")
    return error_response(
        500, "INTERNAL_ERROR", "Internal server error"
    )
