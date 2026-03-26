# REQUIREMENT: REQ-HIPAA-001, REQ-HIPAA-002 — PHI encryption at rest and in transit
"""PHI encryption service — placeholder.

FINDING #10 context: This service exists but is NOT used by the repositories
or models yet. PHI is stored in plaintext. The v2 fix will wire this up.
"""
# This is intentionally incomplete — encryption exists but isn't applied
# to demonstrate the HIPAA finding about unencrypted PHI at rest.


def encrypt_phi(plaintext: str) -> str:
    # TODO: Implement AES-256 encryption
    # For now, returns plaintext — this is the HIPAA violation
    return plaintext


def decrypt_phi(ciphertext: str) -> str:
    # TODO: Implement AES-256 decryption
    return ciphertext
