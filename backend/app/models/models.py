import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON
from ..database import Base

def generate_uuid():
    return str(uuid.uuid4())

class GovernanceEvent(Base):
    __tablename__ = "governance_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    requested_model = Column(String, nullable=False, index=True)
    actual_model = Column(String, nullable=False, index=True)
    reason = Column(String, nullable=False, index=True) # cost, availability, policy
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    agent_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=False, index=True)
    
    # Risk assessment fields
    risk_level = Column(String, nullable=False, default="Low") # Low, Medium, High, Critical
    risk_reason = Column(Text, nullable=True)
    context_downgrade_pct = Column(Float, default=0.0)
    guardrail_downgrade = Column(Boolean, default=False)
    bias_delta = Column(Float, default=0.0)

    # Compliance flag fields
    compliance_flagged = Column(Boolean, default=False, index=True)
    compliance_reason = Column(Text, nullable=True)
    
    extra_metadata = Column(JSON, nullable=True)

class ModelProfile(Base):
    __tablename__ = "model_profiles"

    model_name = Column(String, primary_key=True, index=True)
    context_window = Column(Integer, nullable=False)
    guardrail_level = Column(String, nullable=False) # High, Medium, Low
    bias_score = Column(Float, nullable=False) # e.g. 1.0 (very low bias) to 10.0 (high bias)
    description = Column(Text, nullable=True)

class Agent(Base):
    __tablename__ = "agents"

    agent_id = Column(String, primary_key=True, index=True)
    agent_name = Column(String, nullable=False)
    approved_models = Column(JSON, nullable=False, default=list) # JSON list of model names
