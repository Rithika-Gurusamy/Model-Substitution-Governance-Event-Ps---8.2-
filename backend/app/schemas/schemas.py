from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# Organization & Profile Schemas
class OrganizationResponse(BaseModel):
    id: str
    organization_name: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserProfileResponse(BaseModel):
    id: str
    auth_user_id: str
    organization_id: str
    full_name: str
    role: str
    organization_name: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Event Schemas
class SubstitutionEventCreate(BaseModel):
    requested_model: str = Field(..., example="GPT-5")
    actual_model: str = Field(..., example="GPT-4o Mini")
    reason: str = Field(..., example="cost", description="cost, availability, or policy")
    agent_id: str = Field(..., example="HR-Agent")
    session_id: str = Field(..., example="sess-9912")
    timestamp: Optional[datetime] = None

class GovernanceEventResponse(BaseModel):
    id: str
    requested_model: str
    actual_model: str
    reason: str
    agent_id: str
    session_id: str
    risk_level: str
    risk_reason: str
    context_downgrade_pct: float
    compliance_flagged: bool
    compliance_reason: Optional[str] = None
    organization_id: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

# Model Schemas
class ModelProfileResponse(BaseModel):
    id: str
    model_name: str
    context_window: int
    guardrail_level: str
    bias_score: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Agent Schemas
class AgentResponse(BaseModel):
    id: str
    agent_id: str
    agent_name: str
    description: Optional[str] = None
    organization_id: Optional[str] = None
    approved_models: List[str]

    model_config = ConfigDict(from_attributes=True)

# Compliance Audit Schemas
class UnapprovedEventSummary(BaseModel):
    id: str
    agent_id: str
    requested_model: str
    actual_model: str
    reason: str
    compliance_reason: str
    timestamp: datetime

class ComplianceAuditResponse(BaseModel):
    total_events_analyzed: int
    total_unapproved_requests: int
    compliance_flag_rate_pct: float
    high_risk_substitutions: int
    high_risk_exposure_pct: float
    unapproved_events: List[UnapprovedEventSummary]
