from sqlalchemy.orm import Session
from src.db.database import get_db


def get_database():
    return get_db()
