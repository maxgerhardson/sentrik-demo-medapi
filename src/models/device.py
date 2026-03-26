# REQUIREMENT: REQ-IEC-005 — Medical device registration model
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from src.models.patient import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_serial = Column(String(100), unique=True, nullable=False)
    device_type = Column(String(50), nullable=False)    # e.g., "pulse_oximeter", "bp_monitor"
    manufacturer = Column(String(100))
    model = Column(String(100))
    firmware_version = Column(String(20))
    patient_id = Column(Integer, ForeignKey("patients.id"))
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime)
    registered_at = Column(DateTime, default=datetime.utcnow)
