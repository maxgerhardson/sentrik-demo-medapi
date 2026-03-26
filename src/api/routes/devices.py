"""Device registration and management endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.repositories import device_repo

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.post("/register")
def register_device(device_serial: str, device_type: str,
                    manufacturer: str = None, model: str = None,
                    firmware_version: str = None, patient_id: int = None,
                    db: Session = Depends(get_db)):
    existing = device_repo.get_device_by_serial(db, device_serial)
    if existing:
        raise HTTPException(status_code=409, detail="Device already registered")

    device = device_repo.register_device(
        db, device_serial=device_serial, device_type=device_type,
        manufacturer=manufacturer, model=model,
        firmware_version=firmware_version, patient_id=patient_id,
    )
    return _serialize(device)


@router.get("/{device_id}")
def get_device(device_id: int, db: Session = Depends(get_db)):
    device = device_repo.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return _serialize(device)


@router.get("/serial/{serial}")
def get_device_by_serial(serial: str, db: Session = Depends(get_db)):
    device = device_repo.get_device_by_serial(db, serial)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return _serialize(device)


@router.get("/patient/{patient_id}")
def get_patient_devices(patient_id: int, db: Session = Depends(get_db)):
    devices = device_repo.get_devices_for_patient(db, patient_id)
    return {"devices": [_serialize(d) for d in devices]}


@router.post("/{device_id}/deactivate")
def deactivate_device(device_id: int, db: Session = Depends(get_db)):
    device = device_repo.deactivate_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"deactivated": True}


def _serialize(device):
    return {
        "id": device.id,
        "device_serial": device.device_serial,
        "device_type": device.device_type,
        "manufacturer": device.manufacturer,
        "model": device.model,
        "firmware_version": device.firmware_version,
        "patient_id": device.patient_id,
        "is_active": device.is_active,
        "last_sync": str(device.last_sync) if device.last_sync else None,
        "registered_at": str(device.registered_at) if device.registered_at else None,
    }
