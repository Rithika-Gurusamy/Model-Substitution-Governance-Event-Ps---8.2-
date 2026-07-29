from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from ..database import get_db
from ..models.models import GovernanceEvent
from ..schemas.schemas import EventCreate, EventResponse
from ..services.risk_assessor import RiskAssessor
from ..services.compliance_engine import ComplianceEngine

router = APIRouter(prefix="/events", tags=["Governance Events"])

@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def record_event(payload: EventCreate, db: Session = Depends(get_db)):
    """
    Ingests model substitution event from interceptor, assesses capability risk,
    checks agent compliance whitelist, and records governance log.
    """
    # 1. Risk Assessment
    risk_level, risk_reason, ctx_drop, g_drop, bias_delta = RiskAssessor.evaluate(
        db, payload.requested_model, payload.actual_model
    )

    # 2. Compliance Flag Check
    compliance_flagged, compliance_reason = ComplianceEngine.check_compliance(
        db, payload.agent_id, payload.actual_model
    )

    # If unapproved model, upgrade risk to Critical if it wasn't already High
    if compliance_flagged and risk_level == "Low":
        risk_level = "Medium"

    # 3. Create DB Record
    event = GovernanceEvent(
        requested_model=payload.requested_model,
        actual_model=payload.actual_model,
        reason=payload.reason.lower(),
        timestamp=payload.timestamp or datetime.now(timezone.utc),
        agent_id=payload.agent_id,
        session_id=payload.session_id,
        risk_level=risk_level,
        risk_reason=risk_reason,
        context_downgrade_pct=ctx_drop,
        guardrail_downgrade=g_drop,
        bias_delta=bias_delta,
        compliance_flagged=compliance_flagged,
        compliance_reason=compliance_reason,
        extra_metadata=payload.metadata
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event

@router.get("", response_model=List[EventResponse])
def query_events(
    agent_id: Optional[str] = Query(None, description="Filter by Agent ID"),
    reason: Optional[str] = Query(None, description="Filter by reason (cost, availability, policy)"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level (Low, Medium, High, Critical)"),
    compliance_flagged: Optional[bool] = Query(None, description="Filter by compliance flag"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Query governance event log by agent, substitution reason, risk level, and compliance status.
    """
    query = db.query(GovernanceEvent)

    if agent_id:
        query = query.filter(GovernanceEvent.agent_id == agent_id)
    if reason:
        query = query.filter(GovernanceEvent.reason == reason.lower())
    if risk_level:
        query = query.filter(GovernanceEvent.risk_level == risk_level)
    if compliance_flagged is not None:
        query = query.filter(GovernanceEvent.compliance_flagged == compliance_flagged)

    events = query.order_by(GovernanceEvent.timestamp.desc()).offset(offset).limit(limit).all()
    return events

@router.get("/{event_id}", response_model=EventResponse)
def get_event_detail(event_id: str, db: Session = Depends(get_db)):
    """
    Retrieve single governance event by ID.
    """
    event = db.query(GovernanceEvent).filter(GovernanceEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Governance event not found.")
    return event
