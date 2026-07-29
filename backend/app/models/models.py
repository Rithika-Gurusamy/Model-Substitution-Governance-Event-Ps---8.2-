import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class ModelProfile(Base):
    __tablename__ = "model_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    model_name = Column(String(100), unique=True, nullable=False, index=True)
    context_window = Column(Integer, nullable=False)
    guardrail_level = Column(String(50), nullable=True, default="Medium")
    bias_score = Column(Float, nullable=True, default=5.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    agent_id = Column(String(100), unique=True, nullable=False, index=True)
    agent_name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    approved_models = relationship("ApprovedModel", back_populates="agent", cascade="all, delete-orphan")
    events = relationship("GovernanceEvent", back_populates="agent")

class ApprovedModel(Base):
    __tablename__ = "approved_models"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    agent_db_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    model_name = Column(String(100), nullable=False)

    agent = relationship("Agent", back_populates="approved_models")

class GovernanceEvent(Base):
    __tablename__ = "governance_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    requested_model = Column(String(100), nullable=False, index=True)
    actual_model = Column(String(100), nullable=False, index=True)
    reason = Column(String(50), nullable=False, index=True)  # cost, availability, policy
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    agent_id = Column(String(100), ForeignKey("agents.agent_id"), nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True)

    # Risk Assessor Output
    risk_level = Column(String(20), nullable=False, default="Low", index=True) # Low, Medium, High, Critical
    risk_reason = Column(Text, nullable=False)
    context_downgrade_pct = Column(Float, nullable=False, default=0.0)

    # Compliance Flag Engine Output
    compliance_flagged = Column(Boolean, nullable=False, default=False, index=True)
    compliance_reason = Column(Text, nullable=True)

    agent = relationship("Agent", back_populates="events")
