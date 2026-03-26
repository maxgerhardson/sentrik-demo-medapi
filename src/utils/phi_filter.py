# REQUIREMENT: REQ-HIPAA-005 — PHI data masking for minimum necessary standard
"""PHI data masking for logs — placeholder.

The v2 fix will wire this into logging configuration so that
PHI is never exposed in log output (HIPAA minimum necessary).
"""
import re


def mask_phi(text: str) -> str:
    """Mask common PHI patterns in text."""
    # Mask SSN-like patterns
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '***-**-****', text)
    # Mask email addresses
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                  '***@***.***', text)
    # Mask phone numbers
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '***-***-****', text)
    # Mask MRN
    text = re.sub(r'MRN-\d+', 'MRN-****', text)
    return text


def redact_patient_fields(data: dict, allowed_fields: set = None) -> dict:
    """Redact PHI fields from a patient record for logging."""
    sensitive_fields = {
        "first_name", "last_name", "date_of_birth", "email", "phone",
        "address", "medical_record_number", "insurance_id", "emergency_contact",
    }
    allowed = allowed_fields or {"id", "created_at"}

    result = {}
    for key, value in data.items():
        if key in sensitive_fields and key not in allowed:
            result[key] = "[REDACTED]"
        else:
            result[key] = value
    return result
