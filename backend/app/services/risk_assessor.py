from typing import Tuple
from sqlalchemy.orm import Session
from backend.app.repositories.model_repository import ModelRepository

class RiskAssessor:
    def __init__(self, db: Session):
        self.model_repo = ModelRepository(db)

    def evaluate_substitution_risk(self, requested_model: str, actual_model: str) -> Tuple[str, str, float]:
        """
        Evaluates capability risk exclusively based on Context Window Capacity downgrade.
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

        downgrade_pct_rounded = round(downgrade_pct, 1)

        # Risk Classification Logic strictly based on Context Window Capacity Drop
        if downgrade_pct == 0.0:
            risk_level = "Low"
            risk_reason = f"LOW RISK: Context window capacity maintained or increased ({req_cw:,} → {act_cw:,} tokens)."
        elif downgrade_pct < 25.0:
            risk_level = "Low"
            risk_reason = f"LOW RISK: Minor context window reduction of {downgrade_pct_rounded}% ({req_cw:,} → {act_cw:,} tokens)."
        elif downgrade_pct < 50.0:
            risk_level = "Medium"
            risk_reason = f"MEDIUM RISK: Moderate context window reduction of {downgrade_pct_rounded}% ({req_cw:,} → {act_cw:,} tokens)."
        elif downgrade_pct < 75.0:
            risk_level = "High"
            risk_reason = f"HIGH RISK: Material context window reduction of {downgrade_pct_rounded}% ({req_cw:,} → {act_cw:,} tokens)."
        else:
            risk_level = "Critical"
            risk_reason = f"CRITICAL RISK: Severe material capability downgrade ({downgrade_pct_rounded}% drop in context capacity: {req_cw:,} → {act_cw:,} tokens). Risk of prompt truncation or severe context loss."

        return risk_level, risk_reason, round(downgrade_pct, 2)
