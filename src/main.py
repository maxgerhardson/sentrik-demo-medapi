# REQUIREMENT: REQ-IEC-001, REQ-IEC-002 — Application entry point and configuration
"""VitalSync Medical API — Patient Vitals Ingestion Service.

A FastAPI service that ingests patient vital signs from wearable medical
devices, stores them securely, and exposes an API for clinicians.

Regulated under:
  - IEC 62304 (Medical Device Software Lifecycle)
  - HIPAA Security Rule (PHI Protection)
  - OWASP Top 10 (Application Security)
  - SOC2 Trust Services (Security & Availability)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import patients, vitals, devices, alerts, reports
from src.api.middleware.audit import AuditMiddleware
from src.api.middleware.rate_limit import RateLimitMiddleware
from src.db.database import init_db
from src.config import is_debug

app = FastAPI(
    title="VitalSync Medical API",
    description="Patient vitals ingestion from wearable medical devices",
    version="0.1.0",
    docs_url="/docs" if is_debug() else None,
    redoc_url="/redoc" if is_debug() else None,
)

# Middleware (order matters — outermost first)
app.add_middleware(AuditMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # FINDING: Overly permissive CORS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(patients.router)
app.include_router(vitals.router)
app.include_router(devices.router)
app.include_router(alerts.router)
app.include_router(reports.router)


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "vitalsync-medapi", "version": "0.1.0"}


@app.get("/")
def root():
    return {
        "service": "VitalSync Medical API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
