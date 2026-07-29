from typing import Tuple, Optional, List
from sqlalchemy.orm import Session
from backend.app.repositories.agent_repository import AgentRepository
from backend.app.repositories.event_repository import EventRepository
from backend.app.schemas.schemas import ComplianceAuditResponse, GovernanceEventResponse

class ComplianceEngine:
    def __init__(self, db: Session):
        self.agent_repo = AgentRepository(db)
        self.event_repo = EventRepository(db)

    def evaluate_compliance(self, agent_id: str, actual_model: str) -> Tuple[bool, Optional[str]]:
        """
        Evaluates if actual_model complies with the agent's approved model whitelist.
        Returns: (compliance_flagged, compliance_reason)
        """
        approved_models = self.agent_repo.get_approved_models(agent_id)

        if not approved_models:
            # If agent has no explicit whitelist configured yet, pass with warning
            return False, None

        # Normalize names for case-insensitive check
        normalized_approved = [m.lower().strip() for m in approved_models]
        if actual_model.lower().strip() not in normalized_approved:
            reason = f"COMPLIANCE VIOLATION: Substituted model '{actual_model}' is not in approved list for agent '{agent_id}' ({', '.join(approved_models)})."
            return True, reason

        return False, None

    def generate_retroactive_audit(self, limit: int = 500) -> ComplianceAuditResponse:
        """
        Generates retroactive compliance audit across historical governance event logs.
        """
        all_events = self.event_repo.filter_events(limit=limit)
        total_events = len(all_events)

        if total_events == 0:
            return ComplianceAuditResponse(
                total_events_analyzed=0,
                total_unapproved_requests=0,
                compliance_flag_rate_pct=0.0,
                high_risk_substitutions=0,
                high_risk_exposure_pct=0.0,
                unapproved_events=[]
            )

        unapproved = [e for e in all_events if e.compliance_flagged]
        high_risk = [e for e in all_events if e.risk_level in ["High", "Critical"]]

        flag_rate = round((len(unapproved) / total_events) * 100.0, 2)
        high_risk_pct = round((len(high_risk) / total_events) * 100.0, 2)

        unapproved_schemas = [GovernanceEventResponse.model_validate(e) for e in unapproved]

        return ComplianceAuditResponse(
            total_events_analyzed=total_events,
            total_unapproved_requests=len(unapproved),
            compliance_flag_rate_pct=flag_rate,
            high_risk_substitutions=len(high_risk),
            high_risk_exposure_pct=high_risk_pct,
            unapproved_events=unapproved_schemas
        )
