import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import engine, Base, SessionLocal
from backend.app.seed_data import seed_database

# Ensure database tables and seed data exist for pytest
Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    seed_database(db)
finally:
    db.close()

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_list_models_seeded():
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 50
    model_names = [m["model_name"] for m in data]
    assert "GPT-5" in model_names
    assert "Claude Opus 4" in model_names
    assert "Gemini 1.5 Pro" in model_names

def test_record_substitution_event():
    payload = {
        "requested_model": "GPT-5",
        "actual_model": "GPT-4o Mini",
        "reason": "cost",
        "agent_id": "HR-Agent",
        "session_id": "test-sess-1"
    }
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["requested_model"] == "GPT-5"
    assert data["actual_model"] == "GPT-4o Mini"
    assert data["risk_level"] in ["High", "Critical"]
    assert data["compliance_flagged"] is True

def test_query_events_filter():
    response = client.get("/api/v1/events?agent_id=HR-Agent")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["agent_id"] == "HR-Agent"

def test_retroactive_compliance_audit():
    response = client.get("/api/v1/compliance/audit")
    assert response.status_code == 200
    data = response.json()
    assert "total_events_analyzed" in data
    assert "total_unapproved_requests" in data
    assert "compliance_flag_rate_pct" in data
