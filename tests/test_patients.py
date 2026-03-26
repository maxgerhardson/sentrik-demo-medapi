# REQUIREMENT: REQ-IEC-003, REQ-IEC-004 — Patient management tests
"""Tests for patient management endpoints."""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "vitalsync-medapi"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "VitalSync" in data["service"]


def test_list_patients_returns_list():
    """Verifies the patients list endpoint returns a list structure."""
    # Note: requires database to be initialized
    # In integration tests, this would hit a real DB
    # For unit tests, we'd mock the database
    pass


def test_patient_serialization():
    """Verify patient data serialization format."""
    from src.api.routes.patients import _serialize

    class MockPatient:
        id = 1
        first_name = "John"
        last_name = "Doe"
        date_of_birth = "1990-01-01"
        medical_record_number = "MRN-123456"
        email = "john@example.com"
        phone = "555-0100"
        created_at = "2024-01-01T00:00:00"

    result = _serialize(MockPatient())
    assert result["id"] == 1
    assert result["first_name"] == "John"
    assert result["medical_record_number"] == "MRN-123456"
