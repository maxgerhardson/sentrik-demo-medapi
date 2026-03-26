# REQUIREMENT: REQ-HIPAA-001, REQ-HIPAA-003 — Patient data access with access control
from typing import Optional
from sqlalchemy.orm import Session
from src.models.patient import Patient


def get_patient(db: Session, patient_id: int) -> Optional[Patient]:
    # FINDING #5: Assert in production code (IEC 62304)
    assert patient_id > 0
    return db.query(Patient).filter(Patient.id == patient_id).first()


def get_patients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Patient).offset(skip).limit(limit).all()


def create_patient(db: Session, first_name: str, last_name: str,
                   date_of_birth, medical_record_number: str, **kwargs):
    patient = Patient(
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        medical_record_number=medical_record_number,
        **kwargs
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def update_patient(db: Session, patient_id: int, **updates):
    assert patient_id > 0
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if patient:
        for key, value in updates.items():
            setattr(patient, key, value)
        db.commit()
        db.refresh(patient)
    return patient


def delete_patient(db: Session, patient_id: int):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if patient:
        db.delete(patient)
        db.commit()
    return patient
