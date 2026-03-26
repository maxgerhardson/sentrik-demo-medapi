# REQUIREMENT: REQ-HIPAA-004, REQ-SOC2-001 — Request audit logging middleware
"""Audit logging middleware — placeholder.

FINDING #11 context: Middleware exists but does nothing.
The v2 fix will implement request/response audit logging.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # FINDING #11: No audit logging happening
        # This middleware is a no-op — it should log all PHI access
        response = await call_next(request)
        return response
