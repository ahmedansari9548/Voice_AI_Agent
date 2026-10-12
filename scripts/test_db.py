from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.patient import Patient
from app.schemas.patient import PatientCreate

payload = PatientCreate.model_validate({
    "first_name": "John",
    "last_name": "Smith",
    "date_of_birth": "03/15/1995",
    "sex": "Male",
    "phone_number": "4155550132",
    "email": "john@example.com",
    "address_line_1": "123 Example Street",
    "city": "San Francisco",
    "state": "CA",
    "zip_code": "94105"
})

with SessionLocal() as db:
    patient = Patient(**payload.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)

    patient_id = patient.patient_id
    print("Created patient ID:", patient_id)

with SessionLocal() as db:
    saved = db.scalar(
        select(Patient).where(
            Patient.patient_id == patient_id
        )
    )

    assert saved is not None
    assert saved.first_name == "John"
    assert saved.last_name == "Smith"

    print("Retrieved patient:", saved)
    print("Persistence test: PASSED")
