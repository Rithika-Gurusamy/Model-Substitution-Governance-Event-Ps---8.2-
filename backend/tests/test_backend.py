import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import engine, Base, SessionLocal
from backend.app.seed_data import seed_database

# Ensure clean database tables for pytest
Base.metadata.drop_all(bind=engine)
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

def test_api_key_auth_and_user_isolation():
    # 1. Sign up user
    signup_res = client.post("/api/v1/auth/signup", json={
        "full_name": "Test User",
        "email": "testuser@example.com",
        "password": "Password123!"
    })
    assert signup_res.status_code == 201
    signup_data = signup_res.json()
    api_key = signup_data["api_key"]
    assert api_key.startswith("usr_live_")

    # 2. Record event using X-API-Key header
    payload = {
        "requested_model": "GPT-5",
        "actual_model": "GPT-4o Mini",
        "reason": "cost",
        "agent_id": "Doc-Agent",
        "session_id": "isolated-session-100"
    }
    event_res = client.post("/api/v1/events", json=payload, headers={"X-API-Key": api_key})
    assert event_res.status_code == 201

    # 3. Query events using user token -> user sees their isolated event
    token = signup_data["access_token"]
    user_events_res = client.get("/api/v1/events", headers={"Authorization": f"Bearer {token}"})
    assert user_events_res.status_code == 200
    user_events = user_events_res.json()
    assert len(user_events) == 1
    assert user_events[0]["session_id"] == "isolated-session-100"
