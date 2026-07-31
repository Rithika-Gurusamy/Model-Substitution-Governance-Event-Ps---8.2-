import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(String, primary_key=True, default=generate_uuid)
    auth_user_id = Column(String(255), nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="User")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    api_keys = relationship("ApiKey", back_populates="user_profile", cascade="all, delete-orphan")
    agents = relationship("Agent", back_populates="user_profile", cascade="all, delete-orphan")
    events = relationship("GovernanceEvent", back_populates="user_profile", cascade="all, delete-orphan")

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=generate_uuid)
    key_prefix = Column(String(12), nullable=False)
    key_hash = Column(String(64), nullable=False, unique=True, index=True)
    user_profile_id = Column(String, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user_profile = relationship("UserProfile", back_populates="api_keys")

class ModelProfile(Base):
    __tablename__ = "model_profiles"

    id = Column(String, primary_key=True, default=generate_uuid)
    model_name = Column(String, unique=True, index=True, nullable=False)
    context_window = Column(Integer, nullable=False)
    guardrail_level = Column(String, default="Standard")
    bias_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, default=generate_uuid)
    agent_id = Column(String, index=True, nullable=False)
    agent_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    user_profile_id = Column(String, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user_profile = relationship("UserProfile", back_populates="agents")
    approved_models = relationship("ApprovedModel", back_populates="agent", cascade="all, delete-orphan")

class ApprovedModel(Base):
    __tablename__ = "approved_models"

    id = Column(String, primary_key=True, default=generate_uuid)
    agent_db_id = Column(String, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    model_name = Column(String, nullable=False)

    agent = relationship("Agent", back_populates="approved_models")

class GovernanceEvent(Base):
    __tablename__ = "governance_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    requested_model = Column(String, nullable=False, index=True)
    actual_model = Column(String, nullable=False, index=True)
    reason = Column(String, nullable=False, index=True)
    agent_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=False)
    
    risk_level = Column(String, nullable=False, index=True)
    risk_reason = Column(Text, nullable=False)
    context_downgrade_pct = Column(Float, default=0.0)
    
    compliance_flagged = Column(Boolean, default=False, index=True)
    compliance_reason = Column(Text, nullable=True)

    user_profile_id = Column(String, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    user_profile = relationship("UserProfile", back_populates="events")
