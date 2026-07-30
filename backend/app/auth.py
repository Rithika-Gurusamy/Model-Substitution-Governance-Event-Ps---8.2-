import jwt
from typing import Optional, Tuple
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.models.models import Organization, UserProfile

security = HTTPBearer(auto_error=False)

DEFAULT_DEMO_ORG_ID = "a0000000-0000-0000-0000-000000000001"

def get_current_user_and_org(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    db: Session = Depends(get_db)
) -> Tuple[Optional[UserProfile], str]:
    """
    Decodes Supabase JWT token and resolves authenticated user profile & organization_id.
    If no bearer token is present (e.g., gateway simulator or unauthenticated demo requests),
    defaults to Hackathon Demo Org ('a0000000-0000-0000-0000-000000000001').
    """
    if not credentials or not credentials.credentials:
        return None, DEFAULT_DEMO_ORG_ID

    token = credentials.credentials
    try:
        # Decode Supabase JWT
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        auth_user_id = payload.get("sub")
        email = payload.get("email", "User")
        full_name = payload.get("user_metadata", {}).get("full_name") or email.split("@")[0]

        if not auth_user_id:
            return None, DEFAULT_DEMO_ORG_ID

        # Lookup user profile
        user_profile = db.query(UserProfile).filter(UserProfile.auth_user_id == auth_user_id).first()
        if not user_profile:
            # Create user organization & profile on first login automatically
            org_name = f"{full_name}'s Organization"
            new_org = Organization(organization_name=org_name)
            db.add(new_org)
            db.commit()
            db.refresh(new_org)

            user_profile = UserProfile(
                auth_user_id=auth_user_id,
                organization_id=new_org.id,
                full_name=full_name,
                role="Compliance Officer"
            )
            db.add(user_profile)
            db.commit()
            db.refresh(user_profile)

        return user_profile, user_profile.organization_id

    except Exception as e:
        # Token validation error or expired -> fallback to default demo org for public demo resiliency
        return None, DEFAULT_DEMO_ORG_ID
