# REQUIREMENT: REQ-IEC-005 — Device registry data access
from typing import Optional
from sqlalchemy.orm import Session
from src.models.device import Device


def register_device(db: Session, device_serial: str, device_type: str,
                    manufacturer: str = None, model: str = None,
                    firmware_version: str = None, patient_id: int = None):
    device = Device(
        device_serial=device_serial,
        device_type=device_type,
        manufacturer=manufacturer,
        model=model,
        firmware_version=firmware_version,
        patient_id=patient_id,
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def get_device(db: Session, device_id: int) -> Optional[Device]:
    return db.query(Device).filter(Device.id == device_id).first()


def get_device_by_serial(db: Session, serial: str) -> Optional[Device]:
    return db.query(Device).filter(Device.device_serial == serial).first()


def get_devices_for_patient(db: Session, patient_id: int):
    return db.query(Device).filter(Device.patient_id == patient_id).all()


def deactivate_device(db: Session, device_id: int):
    device = db.query(Device).filter(Device.id == device_id).first()
    if device:
        device.is_active = False
        db.commit()
    return device
