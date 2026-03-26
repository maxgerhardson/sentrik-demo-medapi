# REQUIREMENT: REQ-IEC-003, REQ-HIPAA-001 — Encryption service tests
"""Tests for encryption service."""
import pytest
from src.services.encryption_service import encrypt_phi, decrypt_phi


def test_encrypt_decrypt_roundtrip():
    """Encryption and decryption should be inverse operations."""
    plaintext = "John Doe"
    encrypted = encrypt_phi(plaintext)
    decrypted = decrypt_phi(encrypted)
    assert decrypted == plaintext


def test_encrypt_returns_string():
    """Encrypted output should be a string."""
    result = encrypt_phi("test data")
    assert isinstance(result, str)


# NOTE: In v1, encryption is a no-op (returns plaintext).
# These tests will need updating when real encryption is implemented.
def test_encrypt_phi_placeholder():
    """v1: encryption is a no-op — returns input unchanged."""
    assert encrypt_phi("sensitive") == "sensitive"
