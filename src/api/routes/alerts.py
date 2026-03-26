# REQUIREMENT: REQ-IEC-006, REQ-OWASP-008 — Clinical alerting endpoints
"""Clinical alert endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.repositories import vitals_repo
from src.services.alert_engine import evaluate_alert, prioritize_alerts
from src.services.vitals_processor import check_vital_ranges

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/patient/{patient_id}/check")
def check_alerts(patient_id: int, db: Session = Depends(get_db)):
    latest = vitals_repo.get_latest_vitals(db, patient_id)
    if not latest:
        return {"alerts": [], "message": "No vitals data available"}

    vitals_dict = {
        "heart_rate": latest.heart_rate,
        "systolic_bp": latest.systolic_bp,
        "diastolic_bp": latest.diastolic_bp,
        "spo2": latest.spo2,
        "temperature": latest.temperature,
        "respiratory_rate": latest.respiratory_rate,
        "blood_glucose": latest.blood_glucose,
    }

    range_alerts = check_vital_ranges(vitals_dict)
    clinical_alerts = evaluate_alert(patient_id, vitals_dict)
    all_alerts = prioritize_alerts(range_alerts + clinical_alerts)

    return {
        "patient_id": patient_id,
        "alert_count": len(all_alerts),
        "alerts": all_alerts,
    }
