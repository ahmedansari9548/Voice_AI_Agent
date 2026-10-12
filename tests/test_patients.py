
import os
import uuid

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.main import app
from app.db.database import SessionLocal
from app.models.patient import Patient

load_dotenv()

API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise RuntimeError("API_KEY is missing from your .env file")

client = TestClient(
    app,
    headers={"X-API-Key": API_KEY},
)


def sample_patient():
    """Generate unique fictional patient data for testing."""
    return {
        "first_name": "Alice",
        "last_name": "Tester",
        "date_of_birth": "04/20/1992",
        "sex": "Female",
        "phone_number": "4155550198",
        "address_line_1": "100 Test Avenue",
        "city": "San Francisco",
        "state": "CA",
        "zip_code": "94105",
        "email": "alice@example.com",
        "preferred_language": "English",
    }


@pytest.fixture
def registered_patient():
    """Create a patient and clean up the record after the test."""
    response = client.post("/patients", json=sample_patient())

    assert response.status_code == 201, response.text

    patient_id = response.json()["data"]["patient_id"]

    yield patient_id

    # Cleanup is restricted to the patient created by this fixture.
    with SessionLocal() as db:
        db.execute(
            delete(Patient).where(
                Patient.patient_id == uuid.UUID(patient_id)
            )
        )
        db.commit()


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "data": {"status": "ok"},
        "error": None,
    }


def test_create_patient(registered_patient):
    response = client.get(f"/patients/{registered_patient}")

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["first_name"] == "Alice"
    assert data["last_name"] == "Tester"
    assert data["state"] == "CA"
    assert data["patient_id"] == registered_patient
    assert data["created_at"] is not None


def test_get_patient(registered_patient):
    response = client.get(f"/patients/{registered_patient}")

    assert response.status_code == 200
    assert response.json()["error"] is None
    assert response.json()["data"]["patient_id"] == registered_patient


def test_list_patients(registered_patient):
    response = client.get("/patients")

    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)

    assert any(
        patient["patient_id"] == registered_patient
        for patient in response.json()["data"]
    )


def test_filter_patients(registered_patient):
    response = client.get(
        "/patients",
        params={"phone_number": "4155550198"},
    )

    assert response.status_code == 200

    assert any(
        patient["patient_id"] == registered_patient
        for patient in response.json()["data"]
    )


def test_update_patient(registered_patient):
    response = client.put(
        f"/patients/{registered_patient}",
        json={
            "city": "Boston",
            "state": "MA",
        },
    )

    assert response.status_code == 200, response.text

    data = response.json()["data"]

    assert data["city"] == "Boston"
    assert data["state"] == "MA"
    assert data["first_name"] == "Alice"


def test_invalid_update(registered_patient):
    response = client.put(
        f"/patients/{registered_patient}",
        json={"zip_code": "INVALID"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_soft_delete(registered_patient):
    response = client.delete(f"/patients/{registered_patient}")

    assert response.status_code == 200
    assert response.json()["data"]["deleted"] is True

    response = client.get(f"/patients/{registered_patient}")

    assert response.status_code == 404

    # Verify the database record still exists but is marked deleted.
    with SessionLocal() as db:
        patient = db.get(Patient, uuid.UUID(registered_patient))

        assert patient is not None
        assert patient.deleted_at is not None


def test_invalid_registration():
    payload = sample_patient()
    payload["zip_code"] = "ABC"

    response = client.post("/patients", json=payload)

    assert response.status_code == 422
    assert response.json()["data"] is None
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_future_date_of_birth():
    payload = sample_patient()
    payload["date_of_birth"] = "12/31/2099"

    response = client.post("/patients", json=payload)

    assert response.status_code == 422


def test_invalid_state():
    payload = sample_patient()
    payload["state"] = "ZZ"

    response = client.post("/patients", json=payload)

    assert response.status_code == 422


def test_missing_patient():
    fake_id = uuid.uuid4()

    response = client.get(f"/patients/{fake_id}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_unauthorized_access():
    response = client.get(
        "/patients",
        headers={"X-API-Key": "incorrect-api-key"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_invalid_uuid():
    response = client.get("/patients/not-a-valid-uuid")

    assert response.status_code == 422
