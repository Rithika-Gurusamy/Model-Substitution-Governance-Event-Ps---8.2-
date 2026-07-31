import os
import requests
import logging
from typing import Optional, Dict, Any, Tuple, Callable
from datetime import datetime, timezone

logger = logging.getLogger("GovernanceInterceptor")

class GovernanceInterceptor:
    def __init__(self, tracker_url: Optional[str] = None, api_key: Optional[str] = None):
        target_url = tracker_url or os.getenv("TRACKER_URL") or "https://model-substitution-governance-event.onrender.com"
        self.tracker_url = target_url.rstrip("/")
        self.events_endpoint = f"{self.tracker_url}/api/v1/events"
        self.api_key = api_key or os.getenv("API_KEY") or os.getenv("GOVERNANCE_API_KEY")

    def intercept(
        self,
        requested_model: str,
        actual_model: str,
        reason: str,
        agent_id: str,
        session_id: str,
        timestamp: Optional[datetime] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Intercepts LLM gateway routing decisions.
        If requested_model == actual_model, no substitution occurred.
        If requested_model != actual_model, captures and sends Governance Event to Cloud Tracker.
        """
        if requested_model.strip().lower() == actual_model.strip().lower():
            logger.debug(f"No substitution detected ({requested_model} used as requested).")
            return False, None

        logger.info(f"🚨 Model substitution detected! Requested: '{requested_model}' → Actual: '{actual_model}' (Reason: {reason})")

        payload = {
            "requested_model": requested_model,
            "actual_model": actual_model,
            "reason": reason,
            "agent_id": agent_id,
            "session_id": session_id,
            "timestamp": (timestamp or datetime.now(timezone.utc)).isoformat()
        }

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            response = requests.post(self.events_endpoint, json=payload, headers=headers, timeout=5.0)
            if response.status_code in [200, 201]:
                event_data = response.json()
                logger.info(f"✅ Governance event recorded (ID: {event_data.get('id')}, Risk: {event_data.get('risk_level')}, Flagged: {event_data.get('compliance_flagged')})")
                return True, event_data
            else:
                logger.error(f"Failed to record governance event: HTTP {response.status_code} - {response.text}")
                return True, None
        except Exception as e:
            logger.error(f"Error connecting to Governance Tracker endpoint '{self.events_endpoint}': {e}")
            return True, None

    def intercept_substitution(
        self,
        requested_model: str,
        actual_model: str,
        reason: str,
        agent_id: str,
        session_id: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Backward compatibility alias for intercept()."""
        return self.intercept(
            requested_model=requested_model,
            actual_model=actual_model,
            reason=reason,
            agent_id=agent_id,
            session_id=session_id,
            timestamp=timestamp
        )

def intercept_gateway_decision(
    requested_model: str,
    actual_model: str,
    reason: str,
    agent_id: str,
    session_id: str,
    tracker_url: Optional[str] = None,
    api_key: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Helper wrapper function for single-line gateway integration."""
    interceptor = GovernanceInterceptor(tracker_url=tracker_url, api_key=api_key)
    _, event = interceptor.intercept(
        requested_model=requested_model,
        actual_model=actual_model,
        reason=reason,
        agent_id=agent_id,
        session_id=session_id
    )
    return event
