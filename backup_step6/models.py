import uuid
from datetime import date, datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Index,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Patient(Base):
    __tablename__ = "patients"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    first_name: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    last_name: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    date_of_birth: Mapped[date] = mapped_column(
        Date, nullable=False
    )
    sex: Mapped[str] = mapped_column(
        String(20), nullable=False
    )
    phone_number: Mapped[str] = mapped_column(
        String(10), nullable=False
    )

    email: Mapped[str | None] = mapped_column(
        String(254), nullable=True
    )
    address_line_1: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    address_line_2: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    city: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    state: Mapped[str] = mapped_column(
        String(2), nullable=False
    )
    zip_code: Mapped[str] = mapped_column(
        String(10), nullable=False
    )

    insurance_provider: Mapped[str | None] = mapped_column(
        String(150), nullable=True
    )
    insurance_member_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    preferred_language: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="English",
        server_default="English",
    )
    emergency_contact_name: Mapped[str | None] = mapped_column(
        String(120), nullable=True
    )
    emergency_contact_phone: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint(
            "sex IN ('Male', 'Female', 'Other', "
            "'Decline to Answer')",
            name="ck_patients_sex",
        ),
        CheckConstraint(
            "date_of_birth <= CURRENT_DATE",
            name="ck_patients_dob",
        ),
        CheckConstraint(
            "first_name ~ '^[A-Za-z''-]{1,50}$'",
            name="ck_patients_first_name",
        ),
        CheckConstraint(
            "last_name ~ '^[A-Za-z''-]{1,50}$'",
            name="ck_patients_last_name",
        ),
        CheckConstraint(
            "phone_number ~ '^[0-9]{10}$'",
            name="ck_patients_phone",
        ),
        CheckConstraint(
            "emergency_contact_phone IS NULL OR "
            "emergency_contact_phone ~ '^[0-9]{10}$'",
            name="ck_patients_emergency_phone",
        ),
        CheckConstraint(
            "zip_code ~ '^[0-9]{5}(-[0-9]{4})?$'",
            name="ck_patients_zip",
        ),
        CheckConstraint(
            "char_length(trim(address_line_1)) > 0",
            name="ck_patients_address",
        ),
        CheckConstraint(
            "char_length(trim(city)) > 0",
            name="ck_patients_city",
        ),
        Index("ix_patients_last_name", "last_name"),
        Index("ix_patients_dob", "date_of_birth"),
        Index("ix_patients_phone", "phone_number"),
    )

    def __repr__(self):
        return (
            f"<Patient(id={self.patient_id}, "
            f"name={self.first_name} {self.last_name})>"
        )
