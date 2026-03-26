"""Clinical reporting endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.repositories import vitals_repo
from src.services.vitals_processor import generate_patient_summary, format_vitals_for_export

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/patient/{patient_id}/summary")
def patient_report(patient_id: int, days: int = 30,
                   db: Session = Depends(get_db)):
    summary = generate_patient_summary(db, patient_id, days)
    return summary


@router.get("/patient/{patient_id}/export/{format}")
def export_report(patient_id: int, format: str = "json",
                  db: Session = Depends(get_db)):
    vitals = vitals_repo.get_vitals_for_patient(db, patient_id)
    content = format_vitals_for_export(vitals, format)
    return {"format": format, "content": content}
