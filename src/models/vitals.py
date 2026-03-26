# REQUIREMENT: REQ-HIPAA-001, REQ-IEC-006 — Vital signs data model with clinical validation
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from src.models.patient import Base


class VitalSigns(Base):
    __tablename__ = "vital_signs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    device_id = Column(String(100))
    heart_rate = Column(Float)          # bpm
    systolic_bp = Column(Float)         # mmHg
    diastolic_bp = Column(Float)        # mmHg
    spo2 = Column(Float)               # percentage
    temperature = Column(Float)         # celsius
    respiratory_rate = Column(Float)    # breaths/min
    blood_glucose = Column(Float)       # mg/dL
    recorded_at = Column(DateTime, nullable=False)
    received_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String(50), default="wearable")
