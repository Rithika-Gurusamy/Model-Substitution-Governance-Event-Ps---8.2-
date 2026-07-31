from typing import Optional, Tuple, Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.repositories.agent_repository import AgentRepository
from backend.app.repositories.event_repository import EventRepository

class ComplianceEngine:
    def __init__(self, db: Session):
        self.db = db
        self.agent_repo = AgentRepository(db)
        self.event_repo = EventRepository(db)

    def evaluate_compliance(self, agent_id: str, actual_model: str, user_profile_id: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        approved_models = self.agent_repo.get_approved_models_for_agent(agent_id, user_profile_id)
        
        if not approved_models:
            return False, None

        if actual_model in approved_models:
            return False, None
        else:
            approved_str = ", ".join(approved_models)
            reason = f"COMPLIANCE VIOLATION: Substituted model '{actual_model}' is not in approved list for agent '{agent_id}' ({approved_str})."
            return True, reason

    def run_retroactive_audit(self, user_profile_id: Optional[str] = None) -> Dict[str, Any]:
        events = self.event_repo.filter_events(limit=1000, user_profile_id=user_profile_id)
        total_events = len(events)

        if total_events == 0:
            return {
                "total_events_analyzed": 0,
                "total_unapproved_requests": 0,
                "compliance_flag_rate_pct": 0.0,
                "high_risk_substitutions": 0,
                "high_risk_exposure_pct": 0.0,
                "unapproved_events": []
            }

        unapproved_events: List[Dict[str, Any]] = []
        high_risk_count = 0

        for ev in events:
            if ev.compliance_flagged:
                unapproved_events.append({
                    "id": ev.id,
                    "agent_id": ev.agent_id,
                    "requested_model": ev.requested_model,
                    "actual_model": ev.actual_model,
                    "reason": ev.reason,
                    "compliance_reason": ev.compliance_reason or "Unapproved model usage",
                    "timestamp": ev.timestamp
                })

            if ev.risk_level in ["High", "Critical"]:
                high_risk_count += 1

        unapproved_count = len(unapproved_events)
        compliance_flag_rate = round((unapproved_count / total_events) * 100, 2)
        high_risk_exposure_rate = round((high_risk_count / total_events) * 100, 2)

        return {
            "total_events_analyzed": total_events,
            "total_unapproved_requests": unapproved_count,
            "compliance_flag_rate_pct": compliance_flag_rate,
            "high_risk_substitutions": high_risk_count,
            "high_risk_exposure_pct": high_risk_exposure_rate,
            "unapproved_events": unapproved_events
        }
