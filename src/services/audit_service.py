# REQUIREMENT: REQ-HIPAA-004, REQ-SOC2-001 — Audit logging with HMAC integrity
"""Audit service — placeholder.

FINDING #11 context: This service exists but is NOT wired into any
middleware or endpoint. No audit logging is actually happening.
The v2 fix will implement proper HMAC-signed audit logging.
"""
# Intentionally empty — audit service exists but isn't used
# to demonstrate the SOC2/HIPAA finding about missing audit trail.


def log_event(action: str, user: str = None, resource: str = None,
              details: dict = None):
    # TODO: Implement proper audit logging with HMAC integrity
    pass


def get_audit_log(start: str = None, end: str = None):
    # TODO: Implement audit log retrieval
    return []
