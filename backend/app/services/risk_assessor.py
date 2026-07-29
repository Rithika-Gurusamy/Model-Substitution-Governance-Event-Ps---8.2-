from typing import Tuple
from sqlalchemy.orm import Session
from backend.app.repositories.model_repository import ModelRepository

class RiskAssessor:
    def __init__(self, db: Session):
        self.model_repo = ModelRepository(db)

    def evaluate_substitution_risk(self, requested_model: str, actual_model: str) -> Tuple[str, str, float]:
        """
        Evaluates material capability downgrade between requested and actual models.
        Returns: (risk_level, risk_reason, context_downgrade_pct)
        """
        req_profile = self.model_repo.get_by_name(requested_model)
        act_profile = self.model_repo.get_by_name(actual_model)

        req_cw = req_profile.context_window if req_profile else 128000
        act_cw = act_profile.context_window if act_profile else 128000

        # Calculate context window downgrade percentage
        if req_cw > 0:
            downgrade_pct = max(0.0, float(req_cw - act_cw) / float(req_cw) * 100.0)
        else:
            downgrade_pct = 0.0

        reasons = []
        risk_level = "Low"

        if downgrade_pct > 0:
            reasons.append(f"Context window capacity reduced by {downgrade_pct:.1f}% ({req_cw:,} → {act_cw:,} tokens).")
        else:
            reasons.append(f"Context window capacity maintained or increased ({req_cw:,} → {act_cw:,} tokens).")

        # Risk Classification Rules based on context window drop
        if downgrade_pct >= 75.0:
            risk_level = "Critical"
            reasons.append("CRITICAL: Severe capability downgrade (>75% drop in context window capacity). Risk of prompt truncation or data loss.")
        elif downgrade_pct >= 50.0:
            risk_level = "High"
            reasons.append("HIGH RISK: Material capability downgrade (>50% drop in context window capacity).")
        elif downgrade_pct >= 25.0:
            risk_level = "Medium"
            reasons.append("MEDIUM RISK: Moderate context window reduction.")
        else:
            risk_level = "Low"
            reasons.append("LOW RISK: Substitution within acceptable capability bounds.")

        full_reason = " ".join(reasons)
        return risk_level, full_reason, round(downgrade_pct, 2)
