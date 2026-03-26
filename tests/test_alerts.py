"""Tests for clinical alert engine."""
import pytest
from src.services.alert_engine import (
    evaluate_alert,
    get_default_config,
    prioritize_alerts,
    _create_alert,
)


def test_evaluate_alert_normal_vitals():
    """Normal vitals should produce no alerts."""
    vitals = {
        "heart_rate": 72,
        "spo2": 98,
        "temperature": 36.6,
        "systolic_bp": 120,
        "diastolic_bp": 80,
        "respiratory_rate": 16,
        "blood_glucose": 100,
    }
    alerts = evaluate_alert(patient_id=1, vitals=vitals)
    assert len(alerts) == 0


def test_evaluate_alert_critical_heart_rate():
    """Critically high heart rate should trigger alert."""
    vitals = {"heart_rate": 210}
    alerts = evaluate_alert(patient_id=1, vitals=vitals)
    assert len(alerts) >= 1
    assert any(a["severity"] == "critical" for a in alerts)


def test_evaluate_alert_low_spo2():
    """Critically low SpO2 should trigger alert."""
    vitals = {"spo2": 85}
    alerts = evaluate_alert(patient_id=1, vitals=vitals)
    assert len(alerts) >= 1
    assert any(a["metric"] == "spo2" for a in alerts)


def test_evaluate_alert_hypertensive_crisis():
    """Very high blood pressure should trigger crisis alert."""
    vitals = {"systolic_bp": 190, "diastolic_bp": 130}
    alerts = evaluate_alert(patient_id=1, vitals=vitals)
    assert len(alerts) >= 1
    assert any("crisis" in a.get("message", "").lower() for a in alerts)


def test_prioritize_alerts():
    """Critical alerts should come before warnings."""
    alerts = [
        {"severity": "warning", "message": "Warning 1"},
        {"severity": "critical", "message": "Critical 1"},
        {"severity": "info", "message": "Info 1"},
    ]
    result = prioritize_alerts(alerts)
    assert result[0]["severity"] == "critical"
    assert result[-1]["severity"] == "info"


def test_create_alert_structure():
    """Alert should have required fields."""
    alert = _create_alert(1, "heart_rate", 210, "critical", "Very high HR")
    assert alert["patient_id"] == 1
    assert alert["metric"] == "heart_rate"
    assert alert["severity"] == "critical"
    assert "timestamp" in alert
    assert alert["acknowledged"] is False


def test_get_default_config():
    """Default config should have all required thresholds."""
    config = get_default_config()
    assert "hr_critical_high" in config
    assert "spo2_critical" in config
    assert "temp_critical_high" in config
