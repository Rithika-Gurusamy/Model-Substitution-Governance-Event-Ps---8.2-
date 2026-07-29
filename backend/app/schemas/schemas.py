from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

# Event Creation Schema
class EventCreate(BaseModel):
    requested_model: str = Field(..., json_schema_extra={"example": "gpt-4"})
    actual_model: str = Field(..., json_schema_extra={"example": "gpt-4o-mini"})
    reason: str = Field(..., json_schema_extra={"example": "cost"}, description="Reason for substitution: cost, availability, or policy")
    timestamp: Optional[datetime] = None
    agent_id: str = Field(..., json_schema_extra={"example": "HR-Agent"})
    session_id: str = Field(..., json_schema_extra={"example": "session-123"})
    metadata: Optional[Dict[str, Any]] = None

# Event Response Schema
class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    requested_model: str
    actual_model: str
    reason: str
    timestamp: datetime
    agent_id: str
    session_id: str
    risk_level: str
    risk_reason: Optional[str] = None
    context_downgrade_pct: float
    guardrail_downgrade: bool
    bias_delta: float
    compliance_flagged: bool
    compliance_reason: Optional[str] = None
    extra_metadata: Optional[Dict[str, Any]] = None

# Model Profile Schema
class ModelProfileBase(BaseModel):
    model_name: str
    context_window: int
    guardrail_level: str
    bias_score: float
    description: Optional[str] = None

class ModelProfileResponse(ModelProfileBase):
    model_config = ConfigDict(from_attributes=True)

# Agent Schema
class AgentBase(BaseModel):
    agent_id: str
    agent_name: str
    approved_models: List[str]

class AgentResponse(AgentBase):
    model_config = ConfigDict(from_attributes=True)

# Compliance Audit Summary Schema
class ComplianceAuditSummary(BaseModel):
    total_events: int
    unapproved_substitutions: int
    compliance_violation_rate: float
    high_risk_substitutions: int
    critical_risk_substitutions: int
    affected_agents: List[str]
    substitution_reasons_breakdown: Dict[str, int]
    risk_level_breakdown: Dict[str, int]
