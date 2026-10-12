import json
import logging

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.voice_registration import VoiceRegistration
from app.schemas.patient import PatientCreate

logger = logging.getLogger(__name__)


def process_tool_call(db: Session, tool_call: dict) -> dict:
    tool_id = tool_call.get("id")
    function = tool_call.get("function") or {}

    name = tool_call.get("name") or function.get("name")
    arguments = tool_call.get("parameters")

    if arguments is None:
        arguments = function.get("arguments", {})

    if not isinstance(tool_id, str) or not tool_id:
        return {
            "toolCallId": str(tool_id or ""),
            "error": "Missing tool call ID",
        }

    if name != "register_patient":
        return {
            "toolCallId": tool_id,
            "error": "Unknown tool",
        }

    try:
        if isinstance(arguments, str):
            arguments = json.loads(arguments)

        if not isinstance(arguments, dict):
            raise ValueError("Arguments must be an object")

        # Confirmation must be explicit in the tool arguments.
        # The assistant prompt instructs the model to set this
        # only after hearing the caller's affirmative confirmation.
        confirmed = arguments.pop("confirmed", None)

        if confirmed is not True:
            return {
                "toolCallId": tool_id,
                "error": "Registration not confirmed by caller",
            }

        # Repeated tool calls return the original registration.
        previous = db.get(VoiceRegistration, tool_id)

        if previous is not None:
            return {
                "toolCallId": tool_id,
                "result": json.dumps({
                    "status": "success",
                    "patient_id": str(previous.patient_id),
                    "message": "Registration already completed",
                }),
            }

        payload = PatientCreate.model_validate(arguments)

        # Reuse the same validated patient model used by the
        # PatientService. Commit both records atomically.
        patient = Patient(**payload.model_dump(mode="python"))
        db.add(patient)
        db.flush()

        registration = VoiceRegistration(
            tool_call_id=tool_id,
            patient_id=patient.patient_id,
        )
        db.add(registration)
        db.commit()

        logger.info(
            "Voice registration completed: patient_id=%s",
            patient.patient_id,
        )

        return {
            "toolCallId": tool_id,
            "result": json.dumps({
                "status": "success",
                "patient_id": str(patient.patient_id),
                "message": "Patient registered successfully",
            }),
        }

    except (ValidationError, ValueError, json.JSONDecodeError) as exc:
        db.rollback()
        return {
            "toolCallId": tool_id,
            "error": f"Invalid patient information: {str(exc)[:350]}",
        }

    except IntegrityError:
        db.rollback()

        # Another request may have completed the same tool call.
        previous = db.get(VoiceRegistration, tool_id)

        if previous is not None:
            return {
                "toolCallId": tool_id,
                "result": json.dumps({
                    "status": "success",
                    "patient_id": str(previous.patient_id),
                    "message": "Registration already completed",
                }),
            }

        logger.exception("Voice registration integrity error")
        return {
            "toolCallId": tool_id,
            "error": "Registration could not be completed",
        }

    except SQLAlchemyError:
        db.rollback()
        logger.exception("Voice registration database failure")
        return {
            "toolCallId": tool_id,
            "error": "Database unavailable; registration not confirmed",
        }
