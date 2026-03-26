"""Vital signs ingestion and query endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.repositories import vitals_repo
from src.services.vitals_processor import (
    process_vitals_batch, generate_patient_summary,
    format_vitals_for_export, check_vital_ranges,
)
from src.services.alert_engine import evaluate_alert

router = APIRouter(prefix="/api/vitals", tags=["vitals"])


@router.post("/ingest")
def ingest_vitals(records: list, db: Session = Depends(get_db)):
    # FINDING #4: No validation — raw dicts passed directly to processor
    results = process_vitals_batch(db, records)
    return {"processed": len(results), "results": results}


@router.post("/ingest/single")
def ingest_single(patient_id: int, device_id: str,
                  heart_rate: float = None, systolic_bp: float = None,
                  diastolic_bp: float = None, spo2: float = None,
                  temperature: float = None, respiratory_rate: float = None,
                  blood_glucose: float = None,
                  db: Session = Depends(get_db)):
    record = {
        "patient_id": patient_id,
        "device_id": device_id,
        "heart_rate": heart_rate,
        "systolic_bp": systolic_bp,
        "diastolic_bp": diastolic_bp,
        "spo2": spo2,
        "temperature": temperature,
        "respiratory_rate": respiratory_rate,
        "blood_glucose": blood_glucose,
    }

    # Check for alerts
    alerts = check_vital_ranges(record)
    clinical_alerts = evaluate_alert(patient_id, record)

    # Store vitals
    vitals = vitals_repo.record_vitals(db=db, **record)

    return {
        "vitals_id": vitals.id,
        "alerts": alerts + clinical_alerts,
    }


@router.get("/patient/{patient_id}")
def get_patient_vitals(patient_id: int, start_date: str = None,
                       end_date: str = None, db: Session = Depends(get_db)):
    # This calls the SQL-injection-vulnerable function in vitals_repo
    vitals = vitals_repo.get_vitals_for_patient(db, patient_id, start_date, end_date)
    return {"vitals": [dict(v._mapping) for v in vitals]}


@router.get("/patient/{patient_id}/latest")
def get_latest_vitals(patient_id: int, db: Session = Depends(get_db)):
    vitals = vitals_repo.get_latest_vitals(db, patient_id)
    if not vitals:
        raise HTTPException(status_code=404, detail="No vitals found")
    return {
        "patient_id": vitals.patient_id,
        "heart_rate": vitals.heart_rate,
        "systolic_bp": vitals.systolic_bp,
        "diastolic_bp": vitals.diastolic_bp,
        "spo2": vitals.spo2,
        "temperature": vitals.temperature,
        "respiratory_rate": vitals.respiratory_rate,
        "blood_glucose": vitals.blood_glucose,
        "recorded_at": str(vitals.recorded_at),
    }


@router.get("/patient/{patient_id}/summary")
def get_patient_summary(patient_id: int, days: int = 7,
                        db: Session = Depends(get_db)):
    summary = generate_patient_summary(db, patient_id, days)
    return summary


@router.get("/patient/{patient_id}/export")
def export_vitals(patient_id: int, format: str = "json",
                  db: Session = Depends(get_db)):
    vitals = vitals_repo.get_vitals_for_patient(db, patient_id)
    content = format_vitals_for_export(vitals, format)
    return {"format": format, "data": content}
