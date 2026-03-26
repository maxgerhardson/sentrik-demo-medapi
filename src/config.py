"""Application configuration."""
import os
from os import *  # FINDING #6: Star import (AST — star import)

# FINDING #1: Hardcoded database password (Secrets scan + regex)
DB_PASSWORD = "admin123"
DATABASE_URL = f"postgresql://vitalsync:{DB_PASSWORD}@localhost:5432/vitalsync"

# FINDING #12: Planted API key in comment (Secrets scan)
# API_KEY = "sk_test_DEMO_4eC39HqLyjWDarjtT1zdp7dc_FAKE"

# FINDING #17: Global mutable state (AST — global variable)
connection = None
request_count = 0


def get_database_url():
    return os.environ.get("DATABASE_URL", DATABASE_URL)


def get_jwt_secret():
    # Hardcoded fallback — should use env var only
    return os.environ.get("JWT_SECRET_KEY", "super-secret-jwt-key-do-not-share")


def get_encryption_key():
    return os.environ.get("ENCRYPTION_KEY", "")


def is_debug():
    return os.environ.get("DEBUG", "true").lower() == "true"
