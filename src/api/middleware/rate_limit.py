# REQUIREMENT: REQ-OWASP-006 — Rate limiting middleware
"""Rate limiting middleware — placeholder.

FINDING #14 context: Rate limiting is not implemented.
The v2 fix will add proper per-IP rate limiting.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


# FINDING #14: No rate limiting (OWASP)
class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # No rate limiting implemented — all requests pass through
        response = await call_next(request)
        return response
