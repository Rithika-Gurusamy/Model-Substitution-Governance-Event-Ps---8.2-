import urllib.request
import urllib.parse
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Callable

logger = logging.getLogger("governance_interceptor")

class GovernanceInterceptor:
    """
    Lightweight Interceptor installed inside customer LLM Gateways.
    
    Observes model routing decisions and records every substitution event 
    (requested_model != actual_model) to the Governance Tracker API.
    """
    def __init__(
        self,
        tracker_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: float = 5.0,
        fail_silently: bool = True
    ):
        self.tracker_url = tracker_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.fail_silently = fail_silently

    def intercept_substitution(
        self,
        requested_model: str,
        actual_model: str,
        reason: str,
        agent_id: str,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Detects model substitution and records it to the tracker.
        
        :param requested_model: Model requested by client (e.g. 'gpt-4')
        :param actual_model: Model selected by gateway (e.g. 'gpt-4o-mini')
        :param reason: Reason for substitution ('cost', 'availability', 'policy')
        :param agent_id: ID of the invoking agent (e.g. 'HR-Agent')
        :param session_id: Session ID of the request
        :param metadata: Extra context metadata
        :return: Result dict with status and event data
        """
        # If model requested matches actual model, no substitution occurred.
        if requested_model == actual_model:
            return {
                "substituted": False,
                "recorded": False,
                "reason": "Model requested matches actual model."
            }

        payload = {
            "requested_model": requested_model,
            "actual_model": actual_model,
            "reason": reason.lower(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": agent_id,
            "session_id": session_id,
            "metadata": metadata or {}
        }

        return self._send_event(payload)

    def _send_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        endpoint = f"{self.tracker_url}/events"
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                resp_data = json.loads(resp.read().decode('utf-8'))
                return {
                    "substituted": True,
                    "recorded": True,
                    "event": resp_data
                }
        except Exception as e:
            msg = f"Failed to record substitution event to tracker: {e}"
            logger.error(msg)
            if not self.fail_silently:
                raise RuntimeError(msg) from e
            return {
                "substituted": True,
                "recorded": False,
                "error": str(e),
                "payload": payload
            }

    def wrap_gateway_router(self, route_fn: Callable) -> Callable:
        """
        Decorator for gateway routing functions.
        Expects route_fn to return a tuple or dict containing (requested_model, actual_model, reason, agent_id, session_id).
        """
        def wrapper(*args, **kwargs):
            result = route_fn(*args, **kwargs)
            if isinstance(result, dict):
                req_model = result.get("requested_model")
                act_model = result.get("actual_model")
                reason = result.get("reason", "unknown")
                agent_id = result.get("agent_id", "default_agent")
                session_id = result.get("session_id", "default_session")
                if req_model and act_model:
                    self.intercept_substitution(req_model, act_model, reason, agent_id, session_id)
            return result
        return wrapper
