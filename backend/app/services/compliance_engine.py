from typing import Tuple, List, Dict, Any
from sqlalchemy.orm import Session
from ..models.models import Agent, GovernanceEvent

DEFAULT_AGENT_POLICIES = {
    "Finance-Bot": ["gpt-4", "gpt-4o", "claude-3-5-sonnet"],
    "Support-Agent": ["claude-3-5-sonnet", "claude-3-haiku", "gpt-4o-mini", "gemini-1-5-flash"],
    "HR-Policy-Bot": ["gpt-4", "gpt-4o"],
    "Code-Assistant": ["gpt-4o", "claude-3-5-sonnet", "gemini-1-5-pro"]
}

class ComplianceEngine:
    """
    Checks substitutions against Agent Approved Model lists.
    Also provides retroactive compliance exposure audits.
    """
    @classmethod
    def check_compliance(cls, db: Session, agent_id: str, actual_model: str) -> Tuple[bool, str]:
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if agent:
            approved_list = agent.approved_models or []
        else:
            approved_list = DEFAULT_AGENT_POLICIES.get(agent_id, ["gpt-4", "gpt-4o", "claude-3-5-sonnet"])

        # Check if actual model (or its prefix/variant) is approved
        actual_norm = actual_model.lower().strip()
        is_approved = any(actual_norm == app.lower().strip() for app in approved_list)

        if not is_approved:
            reason = f"Compliance Violation: Substituted model '{actual_model}' is outside agent '{agent_id}' approved list ({approved_list})."
            return True, reason
        
        return False, "Compliant: Substituted model is on approved model list."

    @classmethod
    def perform_retroactive_audit(cls, db: Session, agent_id: str = None, start_time: str = None, end_time: str = None) -> Dict[str, Any]:
        query = db.query(GovernanceEvent)

        if agent_id:
            query = query.filter(GovernanceEvent.agent_id == agent_id)

        events = query.all()
        total_events = len(events)
        if total_events == 0:
            return {
                "total_events": 0,
                "unapproved_substitutions": 0,
                "compliance_violation_rate": 0.0,
                "high_risk_substitutions": 0,
                "critical_risk_substitutions": 0,
                "affected_agents": [],
                "substitution_reasons_breakdown": {},
                "risk_level_breakdown": {}
            }

        unapproved = sum(1 for e in events if e.compliance_flagged)
        high_risk = sum(1 for e in events if e.risk_level == "High")
        critical_risk = sum(1 for e in events if e.risk_level == "Critical")
        affected_agents = list(set(e.agent_id for e in events if e.compliance_flagged))

        reasons_count = {}
        risk_count = {}
        for e in events:
            reasons_count[e.reason] = reasons_count.get(e.reason, 0) + 1
            risk_count[e.risk_level] = risk_count.get(e.risk_level, 0) + 1

        return {
            "total_events": total_events,
            "unapproved_substitutions": unapproved,
            "compliance_violation_rate": round((unapproved / total_events) * 100.0, 1),
            "high_risk_substitutions": high_risk,
            "critical_risk_substitutions": critical_risk,
            "affected_agents": affected_agents,
            "substitution_reasons_breakdown": reasons_count,
            "risk_level_breakdown": risk_count
        }
