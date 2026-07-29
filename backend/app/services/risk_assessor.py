from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from ..models.models import ModelProfile

# Default fallback profiles if model is not yet in database
DEFAULT_MODEL_PROFILES = {
    "gpt-4": {"context_window": 128000, "guardrail_level": "High", "bias_score": 2.0},
    "gpt-4o": {"context_window": 128000, "guardrail_level": "High", "bias_score": 2.2},
    "gpt-4o-mini": {"context_window": 32000, "guardrail_level": "Medium", "bias_score": 4.5},
    "gpt-3.5-turbo": {"context_window": 16000, "guardrail_level": "Medium", "bias_score": 5.0},
    "claude-3-5-sonnet": {"context_window": 200000, "guardrail_level": "High", "bias_score": 1.8},
    "claude-3-haiku": {"context_window": 48000, "guardrail_level": "Medium", "bias_score": 4.0},
    "gemini-1-5-pro": {"context_window": 1000000, "guardrail_level": "High", "bias_score": 2.5},
    "gemini-1-5-flash": {"context_window": 1000000, "guardrail_level": "Medium", "bias_score": 3.8},
    "llama-3-70b": {"context_window": 8000, "guardrail_level": "Low", "bias_score": 6.0},
    "mistral-7b": {"context_window": 8000, "guardrail_level": "Low", "bias_score": 6.5},
}

GUARDRAIL_RANKS = {"High": 3, "Medium": 2, "Low": 1}

class RiskAssessor:
    """
    Evaluates substitution risk based on model capability profiles:
    - Context Window material downgrade
    - Guardrail level drops
    - Bias score increases
    """
    @staticmethod
    def _get_profile(db: Session, model_name: str) -> Dict[str, Any]:
        normalized_name = model_name.lower().strip()
        db_profile = db.query(ModelProfile).filter(ModelProfile.model_name == normalized_name).first()
        if db_profile:
            return {
                "context_window": db_profile.context_window,
                "guardrail_level": db_profile.guardrail_level,
                "bias_score": db_profile.bias_score
            }
        
        # Check defaults if not found in DB
        if normalized_name in DEFAULT_MODEL_PROFILES:
            return DEFAULT_MODEL_PROFILES[normalized_name]
        
        for k, v in DEFAULT_MODEL_PROFILES.items():
            if k == normalized_name:
                return v
        
        # Fallback generic profile
        return {"context_window": 32000, "guardrail_level": "Medium", "bias_score": 5.0}

    @classmethod
    def evaluate(cls, db: Session, requested_model: str, actual_model: str) -> Tuple[str, str, float, bool, float]:
        req = cls._get_profile(db, requested_model)
        act = cls._get_profile(db, actual_model)

        req_ctx = req["context_window"]
        act_ctx = act["context_window"]

        req_g = req["guardrail_level"]
        act_g = act["guardrail_level"]

        req_b = req["bias_score"]
        act_b = act["bias_score"]

        # Calculate context downgrade percentage
        context_downgrade_pct = 0.0
        if req_ctx > act_ctx:
            context_downgrade_pct = ((req_ctx - act_ctx) / req_ctx) * 100.0

        # Calculate guardrail downgrade
        guardrail_downgrade = GUARDRAIL_RANKS.get(act_g, 2) < GUARDRAIL_RANKS.get(req_g, 2)

        # Calculate bias delta (higher bias = worse)
        bias_delta = round(act_b - req_b, 2)

        # Determine risk factors & explanation
        risk_factors = []
        if context_downgrade_pct >= 50.0:
            risk_factors.append(f"Material context window downgrade of {context_downgrade_pct:.1f}% ({req_ctx:,} -> {act_ctx:,} tokens)")
        elif context_downgrade_pct > 20.0:
            risk_factors.append(f"Minor context window decrease of {context_downgrade_pct:.1f}%")

        if guardrail_downgrade:
            risk_factors.append(f"Guardrail level downgraded from {req_g} to {act_g}")

        if bias_delta > 1.5:
            risk_factors.append(f"Increased bias benchmark risk (+{bias_delta} score delta)")

        # Assign overall risk level
        if context_downgrade_pct >= 75.0 and guardrail_downgrade:
            risk_level = "Critical"
        elif context_downgrade_pct >= 50.0 or guardrail_downgrade:
            risk_level = "High"
        elif context_downgrade_pct > 20.0 or bias_delta > 1.0:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        risk_reason = " | ".join(risk_factors) if risk_factors else "Substitution maintains comparable capability metrics."

        return risk_level, risk_reason, round(context_downgrade_pct, 1), guardrail_downgrade, bias_delta
