from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.models.models import GovernanceEvent

class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        requested_model: str,
        actual_model: str,
        reason: str,
        agent_id: str,
        session_id: str,
        risk_level: str,
        risk_reason: str,
        context_downgrade_pct: float,
        compliance_flagged: bool,
        compliance_reason: Optional[str] = None,
        user_profile_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> GovernanceEvent:
        event = GovernanceEvent(
            requested_model=requested_model,
            actual_model=actual_model,
            reason=reason,
            agent_id=agent_id,
            session_id=session_id,
            risk_level=risk_level,
            risk_reason=risk_reason,
            context_downgrade_pct=context_downgrade_pct,
            compliance_flagged=compliance_flagged,
            compliance_reason=compliance_reason,
            user_profile_id=user_profile_id,
        )
        if timestamp:
            event.timestamp = timestamp

        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_by_id(self, event_id: str) -> Optional[GovernanceEvent]:
        return self.db.query(GovernanceEvent).filter(GovernanceEvent.id == event_id).first()

    def filter_events(
        self,
        agent_id: Optional[str] = None,
        reason: Optional[str] = None,
        risk_level: Optional[str] = None,
        compliance_flagged: Optional[bool] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        user_profile_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[GovernanceEvent]:
        query = self.db.query(GovernanceEvent)

        if user_profile_id:
            query = query.filter(GovernanceEvent.user_profile_id == user_profile_id)
        if agent_id:
            query = query.filter(GovernanceEvent.agent_id == agent_id)
        if reason:
            query = query.filter(GovernanceEvent.reason == reason)
        if risk_level:
            query = query.filter(GovernanceEvent.risk_level == risk_level)
        if compliance_flagged is not None:
            query = query.filter(GovernanceEvent.compliance_flagged == compliance_flagged)
        if start_time:
            query = query.filter(GovernanceEvent.timestamp >= start_time)
        if end_time:
            query = query.filter(GovernanceEvent.timestamp <= end_time)

        return query.order_by(desc(GovernanceEvent.timestamp)).offset(offset).limit(limit).all()
