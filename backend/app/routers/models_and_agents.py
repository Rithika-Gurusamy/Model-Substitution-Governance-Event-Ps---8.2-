from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.models import ModelProfile, Agent
from ..schemas.schemas import ModelProfileBase, ModelProfileResponse, AgentBase, AgentResponse
from ..services.risk_assessor import DEFAULT_MODEL_PROFILES
from ..services.compliance_engine import DEFAULT_AGENT_POLICIES

router = APIRouter(tags=["Model Profiles & Agent Policies"])

@router.get("/models", response_model=List[ModelProfileResponse])
def list_models(db: Session = Depends(get_db)):
    models = db.query(ModelProfile).all()
    if not models:
        # Return seeded profiles if empty
        return [
            ModelProfileResponse(
                model_name=k,
                context_window=v["context_window"],
                guardrail_level=v["guardrail_level"],
                bias_score=v["bias_score"],
                description=f"Standard benchmark profile for {k}"
            )
            for k, v in DEFAULT_MODEL_PROFILES.items()
        ]
    return models

@router.post("/models", response_model=ModelProfileResponse)
def upsert_model(payload: ModelProfileBase, db: Session = Depends(get_db)):
    profile = db.query(ModelProfile).filter(ModelProfile.model_name == payload.model_name.lower()).first()
    if not profile:
        profile = ModelProfile(model_name=payload.model_name.lower())
    
    profile.context_window = payload.context_window
    profile.guardrail_level = payload.guardrail_level
    profile.bias_score = payload.bias_score
    profile.description = payload.description

    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

@router.get("/agents", response_model=List[AgentResponse])
def list_agents(db: Session = Depends(get_db)):
    agents = db.query(Agent).all()
    if not agents:
        return [
            AgentResponse(
                agent_id=k,
                agent_name=f"{k} Policy",
                approved_models=v
            )
            for k, v in DEFAULT_AGENT_POLICIES.items()
        ]
    return agents

@router.post("/agents", response_model=AgentResponse)
def upsert_agent(payload: AgentBase, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.agent_id == payload.agent_id).first()
    if not agent:
        agent = Agent(agent_id=payload.agent_id)
    
    agent.agent_name = payload.agent_name
    agent.approved_models = payload.approved_models

    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent
