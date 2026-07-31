from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.models.models import Agent, ApprovedModel

class AgentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_agent_id(self, agent_id: str, user_profile_id: Optional[str] = None) -> Optional[Agent]:
        query = self.db.query(Agent).filter(Agent.agent_id == agent_id)
        if user_profile_id:
            query = query.filter(Agent.user_profile_id == user_profile_id)
        return query.first()

    def get_all(self, user_profile_id: Optional[str] = None) -> List[Agent]:
        query = self.db.query(Agent)
        if user_profile_id:
            query = query.filter(Agent.user_profile_id == user_profile_id)
        return query.all()

    def get_approved_models_for_agent(self, agent_id: str, user_profile_id: Optional[str] = None) -> List[str]:
        agent = self.get_by_agent_id(agent_id, user_profile_id)
        if not agent:
            return []
        return [m.model_name for m in agent.approved_models]
