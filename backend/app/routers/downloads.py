import io
import zipfile
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(tags=["Downloads"])

@router.get("/download/sdk", summary="Download Governance Interceptor SDK package")
def download_sdk():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("governance-interceptor/setup.py", """from setuptools import setup, find_packages

setup(
    name="governance-interceptor",
    version="1.0.0",
    description="LLM Gateway Interceptor SDK for Model Substitution Governance",
    author="Model Substitution Governance Team",
    packages=find_packages(),
    python_requires=">=3.8",
)
""")
        z.writestr("governance-interceptor/governance_interceptor/__init__.py", """from .interceptor import GovernanceInterceptor, intercept_gateway_decision

__all__ = ["GovernanceInterceptor", "intercept_gateway_decision"]
""")
        z.writestr("governance-interceptor/governance_interceptor/interceptor.py", """import requests
from typing import Optional, Dict, Any

class GovernanceInterceptor:
    def __init__(self, tracker_url: str = "https://model-substitution-governance-event.onrender.com", api_key: Optional[str] = None):
        self.tracker_url = tracker_url.rstrip("/")
        self.api_key = api_key
        self.events_endpoint = f"{self.tracker_url}/api/v1/events"

    def intercept(self, requested_model: str, actual_model: str, reason: str, agent_id: str, session_id: str) -> Optional[Dict[str, Any]]:
        if requested_model == actual_model:
            return None
        payload = {
            "requested_model": requested_model,
            "actual_model": actual_model,
            "reason": reason,
            "agent_id": agent_id,
            "session_id": session_id
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        try:
            res = requests.post(self.events_endpoint, json=payload, headers=headers, timeout=3.5)
            if res.status_code in (200, 201):
                return res.json()
        except Exception as e:
            print(f"[GovernanceInterceptor Warning] Failed to log event: {e}")
        return None
""")
        z.writestr("governance-interceptor/README.md", """# Governance Interceptor SDK

Lightweight Python SDK for LLM Gateways to intercept and record model substitution events.

## Installation
```bash
pip install governance-interceptor
```
""")
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=governance-interceptor.zip"}
    )

@router.get("/download/sample-gateway", summary="Download Runnable Sample LLM Gateway")
def download_sample_gateway():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("sample-gateway/gateway_sim.py", """import requests

TRACKER_URL = "https://model-substitution-governance-event.onrender.com/api/v1/events"

def simulate_substitution(requested_model, actual_model, reason, agent_id, session_id):
    if requested_model == actual_model:
        return
    payload = {
        "requested_model": requested_model,
        "actual_model": actual_model,
        "reason": reason,
        "agent_id": agent_id,
        "session_id": session_id
    }
    res = requests.post(TRACKER_URL, json=payload)
    print(f"Logged substitution {requested_model} -> {actual_model} ({reason}): {res.status_code}")

if __name__ == "__main__":
    print("Running Sample Gateway Simulation...")
    simulate_substitution("GPT-5", "GPT-4o Mini", "cost", "HR-Agent", "sess-live-101")
""")
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=sample-gateway.zip"}
    )
