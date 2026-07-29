from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.models.models import Agent, ApprovedModel

class AgentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_agent_id(self, agent_id: str) -> Optional[Agent]:
        return self.db.query(Agent).filter(Agent.agent_id == agent_id).first()

    def list_all(self) -> List[Agent]:
        return self.db.query(Agent).order_by(Agent.agent_id).all()

    def get_approved_models(self, agent_id: str) -> List[str]:
        agent = self.get_by_agent_id(agent_id)
        if not agent:
            return []
        return [am.model_name for am in agent.approved_models]

    def create(self, agent_id: str, agent_name: str, description: Optional[str] = None, approved_models: List[str] = None) -> Agent:
        agent = Agent(
            agent_id=agent_id,
            agent_name=agent_name,
            description=description
        )
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)

        if approved_models:
            for m_name in approved_models:
                self.db.add(ApprovedModel(agent_db_id=agent.id, model_name=m_name))
            self.db.commit()
            self.db.refresh(agent)

        return agent
