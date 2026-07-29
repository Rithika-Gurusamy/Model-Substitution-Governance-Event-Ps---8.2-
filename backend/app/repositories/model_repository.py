from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.models.models import ModelProfile

class ModelRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_name(self, model_name: str) -> Optional[ModelProfile]:
        # Case insensitive exact or fallback search
        profile = self.db.query(ModelProfile).filter(ModelProfile.model_name == model_name).first()
        if not profile:
            # Case-insensitive fallback
            profile = self.db.query(ModelProfile).filter(ModelProfile.model_name.ilike(model_name)).first()
        return profile

    def list_all(self) -> List[ModelProfile]:
        return self.db.query(ModelProfile).order_by(ModelProfile.model_name).all()

    def create(self, model_name: str, context_window: int, guardrail_level: str = "Medium", bias_score: float = 5.0) -> ModelProfile:
        profile = ModelProfile(
            model_name=model_name,
            context_window=context_window,
            guardrail_level=guardrail_level,
            bias_score=bias_score
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile
