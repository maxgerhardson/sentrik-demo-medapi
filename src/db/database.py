# REQUIREMENT: REQ-OWASP-001, REQ-HIPAA-001 — Database connection and query layer
import hashlib
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from src.config import get_database_url, connection

# FINDING #3: MD5 for hashing (HIPAA/IEC — weak cryptography)
def hash_patient_id(patient_id: str) -> str:
    return hashlib.md5(patient_id.encode()).hexdigest()


engine = create_engine(get_database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from src.models.patient import Base
    Base.metadata.create_all(bind=engine)


# FINDING #2: SQL injection via string formatting (OWASP — injection)
def search_patients(db: Session, search_term: str):
    query = f"SELECT * FROM patients WHERE first_name LIKE '%{search_term}%' OR last_name LIKE '%{search_term}%'"
    result = db.execute(text(query))
    return result.fetchall()


# FINDING #20: eval() on user input (OWASP — injection)
def apply_filter(db: Session, table: str, filter_expression: str):
    filter_obj = eval(filter_expression)
    query = f"SELECT * FROM {table} WHERE {filter_obj}"
    result = db.execute(text(query))
    return result.fetchall()
