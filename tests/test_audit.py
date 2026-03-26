"""Tests for audit service."""
import pytest
from src.services.audit_service import log_event, get_audit_log


def test_log_event_does_not_raise():
    """log_event should not raise even in v1 (no-op)."""
    log_event(action="test", user="test_user", resource="test_resource")


def test_get_audit_log_returns_list():
    """get_audit_log should return an empty list in v1."""
    result = get_audit_log()
    assert isinstance(result, list)
    assert len(result) == 0
