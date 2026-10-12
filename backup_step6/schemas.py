import re
from datetime import date, datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import (
    BaseModel, ConfigDict, EmailStr, Field,
    field_validator, model_validator,
)

US_STATES = set(
    "AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS "
    "KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY "
    "NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA "
    "WV WI WY DC".split()
)

NAME_RE = re.compile(r"[A-Za-z'-]{1,50}\Z")
ZIP_RE = re.compile(r"\d{5}(-\d{4})?\Z")
PHONE_RE = re.compile(r"[2-9]\d{2}[2-9]\d{6}\Z")
MEMBER_RE = re.compile(r"[A-Za-z0-9]+\Z")


class Sex(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"
    DECLINE = "Decline to Answer"


class PatientFields(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    date_of_birth: date
    sex: Sex
    phone_number: str
    address_line_1: str = Field(min_length=1, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    state: str
    zip_code: str

    email: EmailStr | None = None
    address_line_2: str | None = Field(default=None, max_length=255)
    insurance_provider: str | None = Field(default=None, max_length=150)
    insurance_member_id: str | None = Field(default=None, max_length=100)
    preferred_language: str = Field(default="English", min_length=1, max_length=50)
    emergency_contact_name: str | None = Field(default=None, max_length=120)
    emergency_contact_phone: str | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def check_name(cls, value: str) -> str:
        if not NAME_RE.fullmatch(value):
            raise ValueError("Use letters, apostrophes or hyphens only")
        return value

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def parse_dob(cls, value: Any) -> Any:
        if isinstance(value, str):
            return datetime.strptime(value, "%m/%d/%Y").date()
        return value

    @field_validator("date_of_birth")
    @classmethod
    def check_dob(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return value

    @field_validator("phone_number", "emergency_contact_phone")
    @classmethod
    def check_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        digits = re.sub(r"\D", "", value)
        if len(digits) == 11 and digits.startswith("1"):
            digits = digits[1:]
        if not PHONE_RE.fullmatch(digits):
            raise ValueError("Enter a valid 10-digit US phone number")
        return digits

    @field_validator("state")
    @classmethod
    def check_state(cls, value: str) -> str:
        value = value.strip().upper()
        if value not in US_STATES:
            raise ValueError("Invalid US state abbreviation")
        return value

    @field_validator("zip_code")
    @classmethod
    def check_zip(cls, value: str) -> str:
        if not ZIP_RE.fullmatch(value):
            raise ValueError("Use a 5-digit ZIP or ZIP+4")
        return value

    @field_validator("address_line_1", "city", "preferred_language")
    @classmethod
    def check_nonempty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Cannot be blank")
        return value

    @field_validator("insurance_member_id")
    @classmethod
    def check_member_id(cls, value: str | None) -> str | None:
        if value is not None and not MEMBER_RE.fullmatch(value):
            raise ValueError("Insurance member ID must be alphanumeric")
        return value


class PatientCreate(PatientFields):
    pass


class PatientUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    sex: Sex | None = None
    phone_number: str | None = None
    address_line_1: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    email: EmailStr | None = None
    address_line_2: str | None = None
    insurance_provider: str | None = None
    insurance_member_id: str | None = None
    preferred_language: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_supplied_fields(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values
        if not values:
            raise ValueError("Provide at least one field to update")
        return values


class PatientRead(PatientFields):
    model_config = ConfigDict(from_attributes=True)

    patient_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Any = None


class PatientResponse(BaseModel):
    data: PatientRead | None
    error: ErrorDetail | None = None


class PatientListResponse(BaseModel):
    data: list[PatientRead]
    error: ErrorDetail | None = None


class DeleteResponse(BaseModel):
    data: dict[str, Any]
    error: ErrorDetail | None = None
