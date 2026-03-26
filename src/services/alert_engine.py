# REQUIREMENT: REQ-IEC-006, REQ-OWASP-008 — Clinical alert engine with threshold monitoring
"""Clinical alert engine — monitors vital signs and generates alerts.

This module evaluates incoming vital signs against clinical thresholds
and generates alerts for clinicians when values are abnormal.
"""
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


# FINDING #16: Excessive cyclomatic complexity (AST — complexity)
# FINDING #19: Nested function depth >3 (AST — nesting)
def evaluate_alert(patient_id: int, vitals: dict, alert_config: dict = None,
                   history: list = None, device_info: dict = None):
    alerts = []
    config = alert_config or get_default_config()

    hr = vitals.get("heart_rate")
    if hr is not None:
        if hr > config.get("hr_critical_high", 200):
            alerts.append(_create_alert(patient_id, "heart_rate", hr, "critical",
                                        f"Heart rate {hr} dangerously high"))
        elif hr > config.get("hr_high", 100):
            if history:
                recent_hrs = [h.get("heart_rate") for h in history[-5:] if h.get("heart_rate")]
                if recent_hrs:
                    avg = sum(recent_hrs) / len(recent_hrs)
                    if hr > avg * 1.5:
                        def check_sustained():
                            sustained = True
                            for h in history[-3:]:
                                if h.get("heart_rate"):
                                    if h["heart_rate"] < config.get("hr_high", 100):
                                        sustained = False
                                        def check_recovery():
                                            for r in history[-6:-3]:
                                                if r.get("heart_rate"):
                                                    if r["heart_rate"] < config.get("hr_high", 100):
                                                        return True
                                            return False
                                        if check_recovery():
                                            sustained = False
                            return sustained
                        if check_sustained():
                            alerts.append(_create_alert(patient_id, "heart_rate", hr, "high",
                                                        f"Sustained elevated heart rate {hr}"))
            else:
                alerts.append(_create_alert(patient_id, "heart_rate", hr, "warning",
                                            f"Elevated heart rate {hr}"))
        elif hr < config.get("hr_critical_low", 40):
            alerts.append(_create_alert(patient_id, "heart_rate", hr, "critical",
                                        f"Heart rate {hr} dangerously low"))
        elif hr < config.get("hr_low", 60):
            alerts.append(_create_alert(patient_id, "heart_rate", hr, "warning",
                                        f"Low heart rate {hr}"))

    spo2 = vitals.get("spo2")
    if spo2 is not None:
        if spo2 < config.get("spo2_critical", 90):
            alerts.append(_create_alert(patient_id, "spo2", spo2, "critical",
                                        f"SpO2 {spo2}% critically low"))
        elif spo2 < config.get("spo2_warning", 95):
            alerts.append(_create_alert(patient_id, "spo2", spo2, "warning",
                                        f"SpO2 {spo2}% below normal"))

    temp = vitals.get("temperature")
    if temp is not None:
        if temp > config.get("temp_critical_high", 40.0):
            alerts.append(_create_alert(patient_id, "temperature", temp, "critical",
                                        f"Temperature {temp}°C critically high"))
        elif temp > config.get("temp_high", 37.5):
            alerts.append(_create_alert(patient_id, "temperature", temp, "warning",
                                        f"Temperature {temp}°C elevated"))
        elif temp < config.get("temp_critical_low", 35.0):
            alerts.append(_create_alert(patient_id, "temperature", temp, "critical",
                                        f"Temperature {temp}°C critically low"))

    systolic = vitals.get("systolic_bp")
    diastolic = vitals.get("diastolic_bp")
    if systolic is not None and diastolic is not None:
        if systolic > 180 or diastolic > 120:
            alerts.append(_create_alert(patient_id, "blood_pressure",
                                        f"{systolic}/{diastolic}", "critical",
                                        "Hypertensive crisis"))
        elif systolic > 140 or diastolic > 90:
            alerts.append(_create_alert(patient_id, "blood_pressure",
                                        f"{systolic}/{diastolic}", "warning",
                                        "Elevated blood pressure"))
        elif systolic < 90 or diastolic < 60:
            alerts.append(_create_alert(patient_id, "blood_pressure",
                                        f"{systolic}/{diastolic}", "warning",
                                        "Low blood pressure"))

    resp = vitals.get("respiratory_rate")
    if resp is not None:
        if resp > 30 or resp < 8:
            alerts.append(_create_alert(patient_id, "respiratory_rate", resp, "critical",
                                        f"Respiratory rate {resp}/min abnormal"))
        elif resp > 20 or resp < 12:
            alerts.append(_create_alert(patient_id, "respiratory_rate", resp, "warning",
                                        f"Respiratory rate {resp}/min outside normal"))

    glucose = vitals.get("blood_glucose")
    if glucose is not None:
        if glucose < 54:
            alerts.append(_create_alert(patient_id, "blood_glucose", glucose, "critical",
                                        f"Blood glucose {glucose} mg/dL — severe hypoglycemia"))
        elif glucose < 70:
            alerts.append(_create_alert(patient_id, "blood_glucose", glucose, "warning",
                                        f"Blood glucose {glucose} mg/dL — hypoglycemia"))
        elif glucose > 300:
            alerts.append(_create_alert(patient_id, "blood_glucose", glucose, "critical",
                                        f"Blood glucose {glucose} mg/dL — severe hyperglycemia"))
        elif glucose > 180:
            alerts.append(_create_alert(patient_id, "blood_glucose", glucose, "warning",
                                        f"Blood glucose {glucose} mg/dL — hyperglycemia"))

    return alerts


def _create_alert(patient_id, metric, value, severity, message):
    return {
        "patient_id": patient_id,
        "metric": metric,
        "value": value,
        "severity": severity,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
        "acknowledged": False,
    }


def get_default_config():
    return {
        "hr_critical_high": 200,
        "hr_high": 100,
        "hr_low": 60,
        "hr_critical_low": 40,
        "spo2_critical": 90,
        "spo2_warning": 95,
        "temp_critical_high": 40.0,
        "temp_high": 37.5,
        "temp_critical_low": 35.0,
    }


def prioritize_alerts(alerts: list) -> list:
    severity_order = {"critical": 0, "high": 1, "warning": 2, "info": 3}
    return sorted(alerts, key=lambda a: severity_order.get(a.get("severity", "info"), 99))
