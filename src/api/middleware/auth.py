# REQUIREMENT: REQ-HIPAA-003, REQ-OWASP-002 — JWT authentication middleware
"""Authentication middleware — minimal placeholder.

FINDING #4 context: Authentication exists but is NOT enforced on
most endpoints. The v2 fix will add proper JWT auth to all PHI endpoints.
"""
from fastapi import Request, HTTPException


# FINDING #18: No HTTPS enforcement (OWASP — security misconfiguration)
# No middleware to redirect HTTP -> HTTPS or check X-Forwarded-Proto


async def verify_token(request: Request):
    """Placeholder token verification — does not actually validate."""
    token = request.headers.get("Authorization")
    if not token:
        # In v1, we just warn but don't block — this is intentionally weak
        pass
    return {"user_id": "anonymous", "role": "viewer"}
