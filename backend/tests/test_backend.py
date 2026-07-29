import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.database import Base, engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_record_cost_substitution_event():
    payload = {
        "requested_model": "gpt-4",
        "actual_model": "gpt-4o-mini",
        "reason": "cost",
        "agent_id": "Finance-Bot",
        "session_id": "test-session-1"
    }
    res = client.post("/events", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["requested_model"] == "gpt-4"
    assert data["actual_model"] == "gpt-4o-mini"
    assert data["reason"] == "cost"
    # Material context downgrade (128k -> 32k is 75% drop)
    assert data["risk_level"] in ["High", "Critical"]
    assert data["context_downgrade_pct"] >= 50.0

def test_record_unapproved_model_compliance_flag():
    payload = {
        "requested_model": "gpt-4",
        "actual_model": "llama-3-70b",
        "reason": "policy",
        "agent_id": "HR-Policy-Bot",
        "session_id": "test-session-2"
    }
    res = client.post("/events", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["compliance_flagged"] is True
    assert "Compliance Violation" in data["compliance_reason"]

def test_query_events_filter():
    client.post("/events", json={
        "requested_model": "claude-3-5-sonnet",
        "actual_model": "gemini-1-5-flash",
        "reason": "availability",
        "agent_id": "Support-Agent",
        "session_id": "test-session-3"
    })
    
    res = client.get("/events?reason=availability")
    assert res.status_code == 200
    events = res.json()
    assert len(events) >= 1
    assert all(e["reason"] == "availability" for e in events)

def test_retroactive_compliance_audit():
    res = client.get("/compliance/audit")
    assert res.status_code == 200
    data = res.json()
    assert "total_events" in data
    assert "unapproved_substitutions" in data
    assert "compliance_violation_rate" in data
