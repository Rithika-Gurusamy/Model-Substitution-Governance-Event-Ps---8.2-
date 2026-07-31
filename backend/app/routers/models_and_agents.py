from typing import List, Optional, Tuple
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.auth import get_current_user_and_org
from backend.app.models.models import UserProfile
from backend.app.schemas.schemas import ModelProfileResponse, AgentResponse, UserProfileResponse
from backend.app.repositories.model_repository import ModelRepository
from backend.app.repositories.agent_repository import AgentRepository

router = APIRouter(tags=["Models & Agents & Auth Profile"])

@router.get("/models", response_model=List[ModelProfileResponse])
def list_model_profiles(db: Session = Depends(get_db)):
    """
    GLOBAL reference directory: Returns all model capability profiles.
    Shared across all users.
    """
    model_repo = ModelRepository(db)
    return model_repo.list_all()

@router.get("/agents", response_model=List[AgentResponse])
def list_agents(
    auth_data: Tuple[Optional[UserProfile], str] = Depends(get_current_user_and_org),
    db: Session = Depends(get_db)
):
    """
    Returns registered agents and approved whitelists scoped to user.
    """
    _, user_profile_id = auth_data
    agent_repo = AgentRepository(db)
    agents = agent_repo.get_all(user_profile_id=user_profile_id)

    response = []
    for a in agents:
        response.append({
            "id": a.id,
            "agent_id": a.agent_id,
            "agent_name": a.agent_name,
            "description": a.description,
            "organization_id": a.user_profile_id,
            "approved_models": [m.model_name for m in a.approved_models]
        })
    return response

@router.get("/auth/me", response_model=UserProfileResponse)
def get_current_user_profile(
    auth_data: Tuple[Optional[UserProfile], str] = Depends(get_current_user_and_org),
    db: Session = Depends(get_db)
):
    """
    Returns authenticated user profile details.
    """
    user_profile, user_profile_id = auth_data

    if user_profile:
        return {
            "id": user_profile.id,
            "auth_user_id": user_profile.auth_user_id,
            "organization_id": user_profile.id,
            "full_name": user_profile.full_name,
            "role": user_profile.role,
            "organization_name": f"{user_profile.full_name}'s Account",
            "created_at": user_profile.created_at
        }
    else:
        # Default unauthenticated public demo profile
        return {
            "id": user_profile_id,
            "auth_user_id": "demo-auth-id",
            "organization_id": user_profile_id,
            "full_name": "Demo Visitor",
            "role": "Demo Visitor",
            "organization_name": "Demo Visitor's Account",
            "created_at": "2026-07-30T00:00:00Z"
        }
