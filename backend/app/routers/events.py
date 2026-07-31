from typing import Optional, List, Tuple
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.auth import get_current_user_and_org
from backend.app.models.models import UserProfile
from backend.app.schemas.schemas import SubstitutionEventCreate, GovernanceEventResponse
from backend.app.repositories.event_repository import EventRepository
from backend.app.services.risk_assessor import RiskAssessor
from backend.app.services.compliance_engine import ComplianceEngine

router = APIRouter(prefix="/events", tags=["Governance Events"])

@router.post("", response_model=GovernanceEventResponse, status_code=status.HTTP_201_CREATED)
def record_substitution_event(
    payload: SubstitutionEventCreate,
    auth_data: Tuple[Optional[UserProfile], str] = Depends(get_current_user_and_org),
    db: Session = Depends(get_db)
):
    _, user_profile_id = auth_data
    risk_assessor = RiskAssessor(db)
    compliance_engine = ComplianceEngine(db)
    event_repo = EventRepository(db)

    # 1. Evaluate Capability Risk
    risk_level, risk_reason, downgrade_pct = risk_assessor.evaluate_substitution_risk(
        payload.requested_model,
        payload.actual_model
    )

    # 2. Evaluate Agent Compliance Whitelist for User Profile
    compliance_flagged, compliance_reason = compliance_engine.evaluate_compliance(
        payload.agent_id,
        payload.actual_model,
        user_profile_id=user_profile_id
    )

    # 3. Persist Governance Event Record under User Profile
    event = event_repo.create(
        requested_model=payload.requested_model,
        actual_model=payload.actual_model,
        reason=payload.reason,
        agent_id=payload.agent_id,
        session_id=payload.session_id,
        risk_level=risk_level,
        risk_reason=risk_reason,
        context_downgrade_pct=downgrade_pct,
        compliance_flagged=compliance_flagged,
        compliance_reason=compliance_reason,
        user_profile_id=user_profile_id,
        timestamp=payload.timestamp
    )

    return event

@router.get("", response_model=List[GovernanceEventResponse])
def query_events(
    agent_id: Optional[str] = Query(None, description="Filter by Agent ID"),
    reason: Optional[str] = Query(None, description="Filter by substitution reason (cost, availability, policy)"),
    risk_level: Optional[str] = Query(None, description="Filter by Risk Level (Low, Medium, High, Critical)"),
    compliance_flagged: Optional[bool] = Query(None, description="Filter by Compliance Flag"),
    start_time: Optional[datetime] = Query(None, description="ISO Start Timestamp"),
    end_time: Optional[datetime] = Query(None, description="ISO End Timestamp"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    auth_data: Tuple[Optional[UserProfile], str] = Depends(get_current_user_and_org),
    db: Session = Depends(get_db)
):
    _, user_profile_id = auth_data
    event_repo = EventRepository(db)
    return event_repo.filter_events(
        agent_id=agent_id,
        reason=reason,
        risk_level=risk_level,
        compliance_flagged=compliance_flagged,
        start_time=start_time,
        end_time=end_time,
        user_profile_id=user_profile_id,
        limit=limit,
        offset=offset
    )

@router.get("/{id}", response_model=GovernanceEventResponse)
def get_event_by_id(id: str, db: Session = Depends(get_db)):
    event_repo = EventRepository(db)
    event = event_repo.get_by_id(id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Governance event '{id}' not found.")
    return event
