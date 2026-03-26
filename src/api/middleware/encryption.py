# REQUIREMENT: REQ-HIPAA-002 — Response encryption middleware
"""Encryption middleware — placeholder.

This would enforce that responses containing PHI are properly
handled. Currently a no-op.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class EncryptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # TODO: Add response headers for encryption requirements
        return response
