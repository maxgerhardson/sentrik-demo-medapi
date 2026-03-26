"""Requirement traceability utilities.

Provides request-level traceability headers linking API calls
to regulatory requirements.
"""


def get_traceability_headers(endpoint: str) -> dict:
    """Return traceability headers for a given endpoint."""
    mapping = {
        "/api/patients": ["REQ-HIPAA-001", "REQ-HIPAA-003"],
        "/api/vitals": ["REQ-HIPAA-001", "REQ-IEC-006"],
        "/api/devices": ["REQ-IEC-005"],
        "/api/alerts": ["REQ-IEC-006"],
        "/api/reports": ["REQ-SOC2-001"],
    }

    reqs = []
    for prefix, req_ids in mapping.items():
        if endpoint.startswith(prefix):
            reqs.extend(req_ids)

    return {
        "X-Requirement-IDs": ",".join(reqs) if reqs else "none",
        "X-Compliance-Version": "1.0",
    }
