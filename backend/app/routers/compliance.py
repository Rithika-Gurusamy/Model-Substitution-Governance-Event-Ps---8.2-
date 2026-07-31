from typing import Optional, Tuple
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.auth import get_current_user_and_org
from backend.app.models.models import UserProfile
from backend.app.schemas.schemas import ComplianceAuditResponse
from backend.app.services.compliance_engine import ComplianceEngine

router = APIRouter(prefix="/compliance", tags=["Compliance"])

@router.get("/audit", response_model=ComplianceAuditResponse)
def get_retroactive_compliance_audit(
    auth_data: Tuple[Optional[UserProfile], str] = Depends(get_current_user_and_org),
    db: Session = Depends(get_db)
):
    _, user_profile_id = auth_data
    engine = ComplianceEngine(db)
    report = engine.run_retroactive_audit(user_profile_id=user_profile_id)
    return report
