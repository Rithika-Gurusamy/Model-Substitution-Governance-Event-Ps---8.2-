from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas.schemas import ComplianceAuditResponse
from backend.app.services.compliance_engine import ComplianceEngine

router = APIRouter(prefix="/compliance", tags=["Compliance"])

@router.get("/audit", response_model=ComplianceAuditResponse)
def get_retroactive_compliance_audit(
    limit: int = Query(500, ge=1, le=5000),
    db: Session = Depends(get_db)
):
    """
    Computes a retroactive compliance impact assessment across historical substitution logs.
    Identifies unapproved model usage and calculates total risk exposure.
    """
    compliance_engine = ComplianceEngine(db)
    return compliance_engine.generate_retroactive_audit(limit=limit)
