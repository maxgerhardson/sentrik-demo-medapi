# REQUIREMENT: REQ-HIPAA-001, REQ-IEC-006 — Vital signs data access
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.models.vitals import VitalSigns


def record_vitals(db: Session, patient_id: int, device_id: str,
                  heart_rate: float = None, systolic_bp: float = None,
                  diastolic_bp: float = None, spo2: float = None,
                  temperature: float = None, respiratory_rate: float = None,
                  blood_glucose: float = None, recorded_at: datetime = None):
    vitals = VitalSigns(
        patient_id=patient_id,
        device_id=device_id,
        heart_rate=heart_rate,
        systolic_bp=systolic_bp,
        diastolic_bp=diastolic_bp,
        spo2=spo2,
        temperature=temperature,
        respiratory_rate=respiratory_rate,
        blood_glucose=blood_glucose,
        recorded_at=recorded_at or datetime.utcnow(),
    )
    db.add(vitals)
    db.commit()
    db.refresh(vitals)
    return vitals


def get_vitals_for_patient(db: Session, patient_id: int,
                           start_date: str = None, end_date: str = None):
    # FINDING #2 variant: Another SQL injection via string formatting
    query = f"SELECT * FROM vital_signs WHERE patient_id = {patient_id}"
    if start_date:
        query += f" AND recorded_at >= '{start_date}'"
    if end_date:
        query += f" AND recorded_at <= '{end_date}'"
    query += " ORDER BY recorded_at DESC"
    result = db.execute(text(query))
    return result.fetchall()


def get_latest_vitals(db: Session, patient_id: int) -> Optional[VitalSigns]:
    return (
        db.query(VitalSigns)
        .filter(VitalSigns.patient_id == patient_id)
        .order_by(VitalSigns.recorded_at.desc())
        .first()
    )


def get_vitals_by_device(db: Session, device_id: str, limit: int = 50):
    return (
        db.query(VitalSigns)
        .filter(VitalSigns.device_id == device_id)
        .order_by(VitalSigns.recorded_at.desc())
        .limit(limit)
        .all()
    )
