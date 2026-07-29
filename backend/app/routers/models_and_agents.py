from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas.schemas import ModelProfileResponse, AgentResponse, AgentCreate
from backend.app.repositories.model_repository import ModelRepository
from backend.app.repositories.agent_repository import AgentRepository

router = APIRouter(tags=["Model Profiles & Agent Policies"])

@router.get("/models", response_model=List[ModelProfileResponse])
def list_model_profiles(db: Session = Depends(get_db)):
    """
    List all supported model capability profiles and context windows.
    """
    model_repo = ModelRepository(db)
    return model_repo.list_all()

@router.get("/agents", response_model=List[AgentResponse])
def list_agents(db: Session = Depends(get_db)):
    """
    List all registered agent compliance policies and approved model whitelists.
    """
    agent_repo = AgentRepository(db)
    agents = agent_repo.list_all()
    results = []
    for a in agents:
        approved = [am.model_name for am in a.approved_models]
        results.append(AgentResponse(
            id=a.id,
            agent_id=a.agent_id,
            agent_name=a.agent_name,
            description=a.description,
            approved_models=approved,
            created_at=a.created_at
        ))
    return results

@router.post("/agents", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_agent_policy(payload: AgentCreate, db: Session = Depends(get_db)):
    """
    Create a new agent governance policy or update approved model whitelist.
    """
    agent_repo = AgentRepository(db)
    existing = agent_repo.get_by_agent_id(payload.agent_id)
    if existing:
        raise HTTPException(status_code=400, detail=f"Agent '{payload.agent_id}' already exists.")

    agent = agent_repo.create(
        agent_id=payload.agent_id,
        agent_name=payload.agent_name,
        description=payload.description,
        approved_models=payload.approved_models
    )
    approved = [am.model_name for am in agent.approved_models]
    return AgentResponse(
        id=agent.id,
        agent_id=agent.agent_id,
        agent_name=agent.agent_name,
        description=agent.description,
        approved_models=approved,
        created_at=agent.created_at
    )
