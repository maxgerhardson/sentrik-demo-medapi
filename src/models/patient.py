# REQUIREMENT: REQ-HIPAA-001, REQ-HIPAA-007 — Patient PHI model with encryption and integrity
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Date, DateTime, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Patient(Base):
    """SQLAlchemy model for patient records."""
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # FINDING #10: PHI stored as plaintext (HIPAA — no encryption at rest)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    medical_record_number = Column(String(50), unique=True, nullable=False)
    email = Column(String(255))
    phone = Column(String(20))
    address = Column(Text)
    emergency_contact = Column(String(255))
    insurance_id = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
