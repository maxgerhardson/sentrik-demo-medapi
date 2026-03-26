"""Tests for vital signs processing."""
import pytest
from src.services.vitals_processor import (
    check_vital_ranges,
    calculate_statistics,
    _calculate_std_dev,
    validate_device_reading,
)


def test_check_vital_ranges_normal():
    """Normal vitals should produce no alerts."""
    record = {
        "heart_rate": 72,
        "spo2": 98,
        "temperature": 36.6,
        "systolic_bp": 120,
        "diastolic_bp": 80,
        "respiratory_rate": 16,
        "blood_glucose": 100,
    }
    alerts = check_vital_ranges(record)
    assert len(alerts) == 0


def test_check_vital_ranges_critical_heart_rate():
    """Critically high heart rate should trigger critical alert."""
    record = {"heart_rate": 210}
    alerts = check_vital_ranges(record)
    assert len(alerts) == 1
    assert alerts[0]["severity"] == "critical"
    assert alerts[0]["metric"] == "heart_rate"


def test_check_vital_ranges_low_spo2():
    """Low SpO2 should trigger critical alert."""
    record = {"spo2": 85}
    alerts = check_vital_ranges(record)
    assert len(alerts) == 1
    assert alerts[0]["severity"] == "critical"


def test_check_vital_ranges_high_temperature():
    """High temperature should trigger critical alert."""
    record = {"temperature": 41.0}
    alerts = check_vital_ranges(record)
    assert len(alerts) == 1
    assert alerts[0]["severity"] == "critical"


def test_check_vital_ranges_warning_spo2():
    """SpO2 between 90-95 should trigger warning."""
    record = {"spo2": 93}
    alerts = check_vital_ranges(record)
    assert len(alerts) == 1
    assert alerts[0]["severity"] == "warning"


def test_calculate_std_dev_single_value():
    """Standard deviation of a single value should be 0."""
    assert _calculate_std_dev([42]) == 0.0


def test_calculate_std_dev_known_values():
    """Standard deviation of known values."""
    result = _calculate_std_dev([2, 4, 4, 4, 5, 5, 7, 9])
    assert round(result, 2) == 2.14


def test_validate_device_reading_valid():
    """Valid reading should pass validation."""
    record = {"patient_id": 1, "device_id": "DEV-001"}
    valid, errors = validate_device_reading(record)
    assert valid is True
    assert len(errors) == 0


def test_validate_device_reading_missing_patient():
    """Missing patient_id should fail validation."""
    record = {"device_id": "DEV-001"}
    valid, errors = validate_device_reading(record)
    assert valid is False
    assert "patient_id is required" in errors


def test_validate_device_reading_missing_device():
    """Missing device_id should fail validation."""
    record = {"patient_id": 1}
    valid, errors = validate_device_reading(record)
    assert valid is False
    assert "device_id is required" in errors
