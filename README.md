# Voice AI Agent — Patient Registration System

A phone-based patient registration system built for the **Voice AI Agent — Patient Registration** take-home assessment. Callers speak with a Vapi-powered assistant, provide U.S. patient demographics, review the collected information, and explicitly authorize submission. A FastAPI backend validates and stores patient records in persistent PostgreSQL and exposes a REST API for patient management.

> **Frontend scope:** No separate web frontend or patient-facing dashboard was developed. The user interface is the **voice conversation over the phone**; the backend can be inspected through its REST API and Swagger documentation.

## Live links

- **Repository:** https://github.com/ahmedansari9548/Voice_AI_Agent
- **Deployed API:** https://voiceaiagent-production-7ed6.up.railway.app
- **Interactive API documentation:** https://voiceaiagent-production-7ed6.up.railway.app/docs
- **Health endpoint:** https://voiceaiagent-production-7ed6.up.railway.app/health
- **U.S. phone number:** `+1 640 XXX XXXX` **(replace with the complete assigned Vapi number before submission)**

## Technology stack

| Component | Technology | Reason |
| --- | --- | --- |
| Voice / telephony | Vapi | Real phone number, conversational assistant, and function-tool invocation |
| API | Python 3.12, FastAPI | Typed request validation and auto-generated OpenAPI docs |
| Data validation | Pydantic | Server-side demographic field validation |
| Database | PostgreSQL on Railway | Persistent storage across calls and application restarts |
| Persistence layer | SQLAlchemy | Structured database models and queries |
| Hosting | Railway | Public HTTPS API and managed database |
| Testing | pytest, httpx | Automated API tests |

## Architecture

```text
Caller (U.S. telephone number)
        |
        v
Vapi Patient Registration Assistant
  - Conversational collection of required fields
  - Clarifications and corrections
  - Final readback and explicit confirmation
        |
        | Function tool: register_patient
        v
POST /vapi/tools  [X-API-Key authentication]
        |
        v
FastAPI application
  - Authentication middleware
  - Pydantic validation
  - Patient service and repository
        |
        v
Railway PostgreSQL
  - Patient records
  - Voice-registration/tool-call tracking

REST clients --> /patients endpoints --> same service/database
```

The voice tool calls the backend only after the caller confirms the collected details. The backend performs its own validation; the conversational model is not the sole validation boundary. Tool-call tracking supports safe handling of repeated registration calls.

## Patient information

**Required:** first name, last name, date of birth, sex, U.S. phone number, address line 1, city, state, ZIP code.

**Optional:** email, address line 2, insurance provider, insurance member ID, preferred language, emergency contact name, emergency contact phone.

Patient records have a generated UUID and creation/update timestamps. Deletion is a **soft delete** using a `deleted_at` timestamp rather than permanently removing the row.

## API

All patient endpoints require an `X-API-Key` request header. The health endpoint and API documentation are public.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `GET` | `/patients` | List patients; supports demographic filtering where implemented |
| `GET` | `/patients/{patient_id}` | Retrieve one patient |
| `POST` | `/patients` | Create a patient |
| `PUT` | `/patients/{patient_id}` | Update patient (partial updates supported by the implementation) |
| `DELETE` | `/patients/{patient_id}` | Soft-delete patient |
| `POST` | `/vapi/tools` | Receive Vapi function-tool calls |

The API uses a consistent response envelope, such as:

```json
{
  "data": { "status": "ok" },
  "error": null
}
```

See the deployed [Swagger UI](https://voiceaiagent-production-7ed6.up.railway.app/docs) for the authoritative request and response schemas.

## Local setup

**Prerequisites:** Python 3.12, PostgreSQL database, and (for voice calls) a Vapi account with a provisioned U.S. number.

```bash
git clone https://github.com/ahmedansari9548/Voice_AI_Agent.git
cd Voice_AI_Agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the repository root:

```dotenv
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DB_NAME
API_KEY=GENERATE_A_LONG_RANDOM_SECRET
```

Use your actual PostgreSQL connection URL and generate a strong secret. **Do not commit `.env`, credentials, or real patient data.** The local `API_KEY`, Railway `API_KEY`, and Vapi tool credential must match.

Start the API:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

Local docs: http://127.0.0.1:8000/docs

## Vapi configuration

1. Create a Vapi assistant for patient registration and attach a U.S. phone number as its inbound assistant.
2. Configure the assistant to collect required fields, clarify invalid values, read all details back, and request explicit consent **before** saving.
3. Attach a Function tool with the exact name `register_patient`.
4. Set the tool's server URL to `https://voiceaiagent-production-7ed6.up.railway.app/vapi/tools`.
5. Configure tool authentication so the outgoing request includes `X-API-Key: <API_KEY>` **without** a `Bearer` prefix, and select that credential on the tool itself.
6. Save the assistant and start a **new** test call after configuration changes.

## Verify the deployment

Check health:

```bash
curl https://voiceaiagent-production-7ed6.up.railway.app/health
```

List patients (requires the API key):

```bash
curl -H "X-API-Key: $API_KEY" \
  https://voiceaiagent-production-7ed6.up.railway.app/patients
```

Run the automated tests locally:

```bash
python -m pytest -v
```

**Recommended acceptance checks:**

- Register a fictional patient by calling the assigned phone number.
- Confirm that the assistant reads the information back and waits for affirmative consent.
- Confirm the tool returns a patient identifier and the record is retrievable with `GET /patients`.
- Reject confirmation and verify no patient record is created.
- Check that unauthenticated patient requests are rejected.
- Verify update, retrieval, and soft-delete behavior.
- Restart the application and verify the record remains in PostgreSQL.

## Project structure

```text
app/
  main.py
  api/
    router.py
    endpoints/             # Patient CRUD and Vapi webhook
  core/
    security.py            # API-key authentication
  db/
    database.py            # Database connection
  models/                  # Patient and voice-registration models
  schemas/                 # Pydantic schemas
  services/                # Business logic
  repositories/            # Database access
  integrations/
    vapi.py                # Vapi tool handling
```

## Limitations and trade-offs

- **No separate frontend was built.** The deliverable prioritizes phone-based registration, backend API, and database persistence.
- The application uses API-key authentication suitable for this assessment; a healthcare production system would require stronger identity/access controls, audit policies, and a full privacy/compliance review before handling real patient information.
- Voice transcription can mishear names, dates, and addresses. Readback and explicit confirmation reduce this risk but do not eliminate it.
- The duplicate-patient recognition/update conversation is an optional enhancement, not a claimed feature.
- Use **fictional patient data only** for demonstrations and testing.

## Submission note

The voice-to-database registration flow was successfully exercised during development. The reviewer should independently verify the live phone number and deployment availability at review time. The full dialable number must be filled in above before submission.
