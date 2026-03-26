# REQUIREMENT: REQ-HIPAA-003, REQ-OWASP-001 — Patient management with access control and input validation
"""Patient management endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.database import get_db, search_patients, apply_filter
from src.db.repositories import patient_repo

router = APIRouter(prefix="/api/patients", tags=["patients"])


# FINDING #4: No authentication required — PHI accessible without auth
# FINDING #8: Missing docstrings on public endpoint functions

@router.get("/")
def list_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    patients = patient_repo.get_patients(db, skip=skip, limit=limit)
    return {"patients": [_serialize(p) for p in patients]}


@router.get("/{patient_id}")
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = patient_repo.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return _serialize(patient)


@router.post("/")
def create_patient(first_name: str, last_name: str, date_of_birth: str,
                   medical_record_number: str, db: Session = Depends(get_db)):
    # FINDING #4: No input validation on patient data
    patient = patient_repo.create_patient(
        db, first_name=first_name, last_name=last_name,
        date_of_birth=date_of_birth, medical_record_number=medical_record_number,
    )
    return _serialize(patient)


@router.put("/{patient_id}")
def update_patient(patient_id: int, db: Session = Depends(get_db), **updates):
    patient = patient_repo.update_patient(db, patient_id, **updates)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return _serialize(patient)


@router.delete("/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = patient_repo.delete_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"deleted": True}


@router.get("/search/{query}")
def search(query: str, db: Session = Depends(get_db)):
    # FINDING #2: Passes user input directly to SQL string formatting
    results = search_patients(db, query)
    return {"results": [dict(r._mapping) for r in results]}


@router.get("/filter/{expression}")
def filter_patients(expression: str, db: Session = Depends(get_db)):
    # FINDING #20: Uses eval() on user-provided filter expression
    results = apply_filter(db, "patients", expression)
    return {"results": [dict(r._mapping) for r in results]}


def _serialize(patient):
    return {
        "id": patient.id,
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "date_of_birth": str(patient.date_of_birth),
        "medical_record_number": patient.medical_record_number,
        "email": patient.email,
        "phone": patient.phone,
        "created_at": str(patient.created_at) if patient.created_at else None,
    }
