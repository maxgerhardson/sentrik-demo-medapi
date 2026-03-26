# REQUIREMENT: REQ-IEC-006, REQ-HIPAA-007 — Vitals processing with clinical validation
"""Vitals processing service — ingestion, validation, and storage.

This module handles the core business logic for processing vital signs
data received from wearable medical devices.
"""
# FINDING #9: This file will be >300 lines (File policy — max file length)
# All the processing logic is stuffed into one module instead of being split.

import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy.orm import Session

from src.db.repositories import vitals_repo
from src.db.database import hash_patient_id


logger = logging.getLogger(__name__)


# FINDING #7: Mutable default argument (AST — mutable default)
def process_vitals_batch(db: Session, records: list, options: dict = {}):
    results = []
    for record in records:
        try:
            result = process_single_vital(db, record, options)
            results.append(result)
        except:  # FINDING #15: Bare except (IEC 62304)
            logger.error("Failed to process record")
            results.append({"status": "error", "record": str(record)})
    return results


def process_single_vital(db: Session, record: dict, options: dict):
    patient_id = record.get("patient_id")
    device_id = record.get("device_id")

    # No input validation — FINDING #4 (OWASP — missing validation)
    # Vital signs are stored without checking clinical ranges

    vitals = vitals_repo.record_vitals(
        db=db,
        patient_id=patient_id,
        device_id=device_id,
        heart_rate=record.get("heart_rate"),
        systolic_bp=record.get("systolic_bp"),
        diastolic_bp=record.get("diastolic_bp"),
        spo2=record.get("spo2"),
        temperature=record.get("temperature"),
        respiratory_rate=record.get("respiratory_rate"),
        blood_glucose=record.get("blood_glucose"),
        recorded_at=record.get("recorded_at"),
    )

    # Log with patient data visible — FINDING (HIPAA minimum necessary)
    logger.info(f"Recorded vitals for patient {patient_id}: HR={record.get('heart_rate')}")

    return {"status": "ok", "vitals_id": vitals.id}


def calculate_statistics(vitals_list: list, metric: str) -> dict:
    values = [getattr(v, metric) for v in vitals_list if getattr(v, metric) is not None]
    if not values:
        return {"count": 0, "mean": None, "min": None, "max": None}

    return {
        "count": len(values),
        "mean": sum(values) / len(values),
        "min": min(values),
        "max": max(values),
        "std_dev": _calculate_std_dev(values),
    }


def _calculate_std_dev(values: list) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return variance ** 0.5


def generate_patient_summary(db: Session, patient_id: int, days: int = 7):
    # FINDING #5 variant: Assert in production
    assert patient_id is not None
    assert days > 0

    # Hash patient ID for logging — uses MD5 (FINDING #3 variant)
    patient_hash = hashlib.md5(str(patient_id).encode()).hexdigest()
    logger.info(f"Generating summary for patient hash: {patient_hash}")

    vitals = vitals_repo.get_vitals_for_patient(
        db, patient_id,
        start_date=(datetime.utcnow() - timedelta(days=days)).isoformat(),
    )

    if not vitals:
        return {"patient_id": patient_id, "period_days": days, "data": None}

    summary = {
        "patient_id": patient_id,
        "period_days": days,
        "total_readings": len(vitals),
        "metrics": {}
    }

    for metric in ["heart_rate", "systolic_bp", "diastolic_bp", "spo2",
                    "temperature", "respiratory_rate", "blood_glucose"]:
        summary["metrics"][metric] = _compute_metric_stats(vitals, metric)

    return summary


def _compute_metric_stats(vitals, metric):
    values = []
    for v in vitals:
        val = v[metric] if isinstance(v, dict) else getattr(v, metric, None)
        if val is not None:
            values.append(val)

    if not values:
        return None

    return {
        "count": len(values),
        "mean": round(sum(values) / len(values), 2),
        "min": min(values),
        "max": max(values),
    }


def check_vital_ranges(record: dict) -> list:
    """Check if vital signs are within normal clinical ranges."""
    alerts = []

    hr = record.get("heart_rate")
    if hr is not None:
        if hr < 40 or hr > 200:
            alerts.append({"metric": "heart_rate", "value": hr, "severity": "critical",
                           "message": f"Heart rate {hr} bpm outside safe range (40-200)"})
        elif hr < 60 or hr > 100:
            alerts.append({"metric": "heart_rate", "value": hr, "severity": "warning",
                           "message": f"Heart rate {hr} bpm outside normal range (60-100)"})

    spo2 = record.get("spo2")
    if spo2 is not None:
        if spo2 < 90:
            alerts.append({"metric": "spo2", "value": spo2, "severity": "critical",
                           "message": f"SpO2 {spo2}% critically low (< 90%)"})
        elif spo2 < 95:
            alerts.append({"metric": "spo2", "value": spo2, "severity": "warning",
                           "message": f"SpO2 {spo2}% below normal (< 95%)"})

    temp = record.get("temperature")
    if temp is not None:
        if temp < 35.0 or temp > 40.0:
            alerts.append({"metric": "temperature", "value": temp, "severity": "critical",
                           "message": f"Temperature {temp}°C outside safe range (35-40)"})
        elif temp < 36.1 or temp > 37.2:
            alerts.append({"metric": "temperature", "value": temp, "severity": "warning",
                           "message": f"Temperature {temp}°C outside normal range (36.1-37.2)"})

    systolic = record.get("systolic_bp")
    diastolic = record.get("diastolic_bp")
    if systolic is not None:
        if systolic > 180 or systolic < 70:
            alerts.append({"metric": "systolic_bp", "value": systolic, "severity": "critical",
                           "message": f"Systolic BP {systolic} mmHg outside safe range (70-180)"})
    if diastolic is not None:
        if diastolic > 120 or diastolic < 40:
            alerts.append({"metric": "diastolic_bp", "value": diastolic, "severity": "critical",
                           "message": f"Diastolic BP {diastolic} mmHg outside safe range (40-120)"})

    resp = record.get("respiratory_rate")
    if resp is not None:
        if resp < 8 or resp > 40:
            alerts.append({"metric": "respiratory_rate", "value": resp, "severity": "critical",
                           "message": f"Respiratory rate {resp}/min outside safe range (8-40)"})

    glucose = record.get("blood_glucose")
    if glucose is not None:
        if glucose < 54 or glucose > 400:
            alerts.append({"metric": "blood_glucose", "value": glucose, "severity": "critical",
                           "message": f"Blood glucose {glucose} mg/dL outside safe range (54-400)"})

    return alerts


def format_vitals_for_export(vitals_list: list, format: str = "json") -> str:
    data = []
    for v in vitals_list:
        entry = {
            "patient_id": v.patient_id if hasattr(v, "patient_id") else v.get("patient_id"),
            "heart_rate": v.heart_rate if hasattr(v, "heart_rate") else v.get("heart_rate"),
            "systolic_bp": v.systolic_bp if hasattr(v, "systolic_bp") else v.get("systolic_bp"),
            "diastolic_bp": v.diastolic_bp if hasattr(v, "diastolic_bp") else v.get("diastolic_bp"),
            "spo2": v.spo2 if hasattr(v, "spo2") else v.get("spo2"),
            "temperature": v.temperature if hasattr(v, "temperature") else v.get("temperature"),
            "respiratory_rate": v.respiratory_rate if hasattr(v, "respiratory_rate") else v.get("respiratory_rate"),
            "blood_glucose": v.blood_glucose if hasattr(v, "blood_glucose") else v.get("blood_glucose"),
        }
        data.append(entry)

    if format == "json":
        return json.dumps(data, indent=2, default=str)
    elif format == "csv":
        if not data:
            return ""
        headers = list(data[0].keys())
        lines = [",".join(headers)]
        for row in data:
            lines.append(",".join(str(row.get(h, "")) for h in headers))
        return "\n".join(lines)
    else:
        return str(data)


def aggregate_device_readings(db: Session, device_id: str, window_minutes: int = 60):
    vitals = vitals_repo.get_vitals_by_device(db, device_id, limit=1000)
    if not vitals:
        return None

    cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
    recent = [v for v in vitals if v.received_at and v.received_at >= cutoff]

    if not recent:
        return {"device_id": device_id, "window_minutes": window_minutes, "readings": 0}

    return {
        "device_id": device_id,
        "window_minutes": window_minutes,
        "readings": len(recent),
        "latest_reading": max(v.received_at for v in recent).isoformat(),
        "metrics": {
            "heart_rate": _quick_stats([v.heart_rate for v in recent if v.heart_rate]),
            "spo2": _quick_stats([v.spo2 for v in recent if v.spo2]),
            "temperature": _quick_stats([v.temperature for v in recent if v.temperature]),
        }
    }


def _quick_stats(values):
    if not values:
        return None
    return {
        "count": len(values),
        "mean": round(sum(values) / len(values), 2),
        "min": round(min(values), 2),
        "max": round(max(values), 2),
    }


def detect_anomalies(vitals_list: list, metric: str, threshold_std: float = 2.0):
    values = []
    for v in vitals_list:
        val = getattr(v, metric, None) if hasattr(v, metric) else v.get(metric)
        if val is not None:
            values.append((v, val))

    if len(values) < 5:
        return []

    nums = [val for _, val in values]
    mean = sum(nums) / len(nums)
    std = _calculate_std_dev(nums)

    if std == 0:
        return []

    anomalies = []
    for vital, val in values:
        z_score = abs(val - mean) / std
        if z_score > threshold_std:
            anomalies.append({
                "vital": vital,
                "metric": metric,
                "value": val,
                "z_score": round(z_score, 2),
                "mean": round(mean, 2),
                "std": round(std, 2),
            })

    return anomalies


def validate_device_reading(record: dict) -> tuple:
    errors = []

    if "patient_id" not in record:
        errors.append("patient_id is required")
    if "device_id" not in record:
        errors.append("device_id is required")

    # Minimal validation — no clinical range checking here
    # This is intentionally weak for the demo

    return (len(errors) == 0, errors)


def batch_import_from_csv(db: Session, csv_content: str, device_id: str):
    lines = csv_content.strip().split("\n")
    if len(lines) < 2:
        return {"imported": 0, "errors": ["No data rows found"]}

    headers = lines[0].split(",")
    imported = 0
    errors = []

    for i, line in enumerate(lines[1:], start=2):
        try:
            values = line.split(",")
            record = dict(zip(headers, values))
            record["device_id"] = device_id

            # Convert numeric fields
            for field in ["heart_rate", "systolic_bp", "diastolic_bp", "spo2",
                          "temperature", "respiratory_rate", "blood_glucose"]:
                if field in record and record[field]:
                    record[field] = float(record[field])

            if "patient_id" in record:
                record["patient_id"] = int(record["patient_id"])

            vitals_repo.record_vitals(db=db, **record)
            imported += 1
        except:  # FINDING #15 variant: Another bare except
            errors.append(f"Line {i}: parse error")

    return {"imported": imported, "errors": errors}
