from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..schemas.schemas import ComplianceAuditSummary
from ..services.compliance_engine import ComplianceEngine

router = APIRouter(prefix="/compliance", tags=["Compliance & Audit"])

@router.get("/audit", response_model=ComplianceAuditSummary)
def get_compliance_audit(
    agent_id: Optional[str] = Query(None, description="Optional agent ID to narrow audit"),
    db: Session = Depends(get_db)
):
    """
    Bonus Feature: Retroactive compliance impact assessment.
    Computes total non-approved requests, violation rate, high risk exposures, and affected agents.
    """
    summary = ComplianceEngine.perform_retroactive_audit(db, agent_id=agent_id)
    return summary
