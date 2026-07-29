from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

# --- Model Profile Schemas ---
class ModelProfileBase(BaseModel):
    model_name: str
    context_window: int
    guardrail_level: Optional[str] = "Medium"
    bias_score: Optional[float] = 5.0

class ModelProfileCreate(ModelProfileBase):
    pass

class ModelProfileResponse(ModelProfileBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Agent & Policy Schemas ---
class AgentBase(BaseModel):
    agent_id: str
    agent_name: str
    description: Optional[str] = None

class AgentCreate(AgentBase):
    approved_models: List[str] = []

class AgentResponse(AgentBase):
    id: str
    approved_models: List[str] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Governance Event Schemas ---
class SubstitutionEventCreate(BaseModel):
    requested_model: str = Field(..., json_schema_extra={"example": "GPT-5"})
    actual_model: str = Field(..., json_schema_extra={"example": "GPT-4o Mini"})
    reason: str = Field(..., description="cost, availability, or policy", json_schema_extra={"example": "cost"})
    agent_id: str = Field(..., json_schema_extra={"example": "HR-Agent"})
    session_id: str = Field(..., json_schema_extra={"example": "sess-10293"})
    timestamp: Optional[datetime] = None

class GovernanceEventResponse(BaseModel):
    id: str
    requested_model: str
    actual_model: str
    reason: str
    timestamp: datetime
    agent_id: str
    session_id: str
    risk_level: str
    risk_reason: str
    context_downgrade_pct: float
    compliance_flagged: bool
    compliance_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# --- Retroactive Compliance Audit Schemas ---
class ComplianceAuditResponse(BaseModel):
    total_events_analyzed: int
    total_unapproved_requests: int
    compliance_flag_rate_pct: float
    high_risk_substitutions: int
    high_risk_exposure_pct: float
    unapproved_events: List[GovernanceEventResponse]
