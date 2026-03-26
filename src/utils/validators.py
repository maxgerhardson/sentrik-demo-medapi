"""Input validators — placeholder.

FINDING #4 context: Validators exist but are NOT used by routes.
The v2 fix will wire these into all API endpoints via Pydantic models.
"""
import re
from datetime import date


def validate_date(date_str: str) -> bool:
    try:
        date.fromisoformat(date_str)
        return True
    except (ValueError, TypeError):
        return False


def validate_mrn(mrn: str) -> bool:
    """Validate medical record number format."""
    return bool(re.match(r'^MRN-\d{6,10}$', mrn))


def validate_email(email: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))


def validate_vital_range(metric: str, value: float) -> bool:
    """Check if a vital sign value is within physically possible ranges."""
    ranges = {
        "heart_rate": (0, 300),
        "systolic_bp": (0, 350),
        "diastolic_bp": (0, 250),
        "spo2": (0, 100),
        "temperature": (25.0, 45.0),
        "respiratory_rate": (0, 80),
        "blood_glucose": (0, 1000),
    }
    if metric not in ranges:
        return True
    low, high = ranges[metric]
    return low <= value <= high
