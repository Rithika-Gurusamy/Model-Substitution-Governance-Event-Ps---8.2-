import jwt
import hashlib
import uuid
from typing import Optional, Tuple
from fastapi import Depends, HTTPException, Security, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.models.models import UserProfile, ApiKey

security = HTTPBearer(auto_error=False)

DEFAULT_DEMO_USER_PROFILE_ID = "u0000000-0000-0000-0000-000000000001"

def generate_api_key_for_user(user_profile_id: str, db: Session) -> str:
    """
    Generates a secure API key for a user profile, hashes it for storage,
    and returns the unhashed raw key string (e.g. 'usr_live_...').
    """
    raw_secret = uuid.uuid4().hex + uuid.uuid4().hex
    raw_key = f"usr_live_{raw_secret}"
    key_prefix = raw_key[:12]
    key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    api_key_obj = ApiKey(
        key_prefix=key_prefix,
        key_hash=key_hash,
        user_profile_id=user_profile_id
    )
    db.add(api_key_obj)
    db.commit()
    db.refresh(api_key_obj)
    return raw_key

def get_current_user_and_org(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    db: Session = Depends(get_db)
) -> Tuple[Optional[UserProfile], str]:
    """
    3-Tier Auth Resolution:
    1. X-API-Key header (Machine / SDK access)
    2. Bearer Token (Human / Dashboard JWT or Direct Auth Session)
    3. Guest Fallback (Demo Mode)
    Returns (UserProfile, user_profile_id)
    """
    # 1. Check X-API-Key Header (SDK calls)
    api_key_header = request.headers.get("X-API-Key")
    if api_key_header:
        key_clean = api_key_header.strip()
        if key_clean and key_clean.lower() != "null":
            key_hash = hashlib.sha256(key_clean.encode("utf-8")).hexdigest()
            key_record = db.query(ApiKey).filter(ApiKey.key_hash == key_hash).first()
            if key_record:
                user_profile = db.query(UserProfile).filter(UserProfile.id == key_record.user_profile_id).first()
                if user_profile:
                    return user_profile, user_profile.id
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API Key. Please copy your active API Key from the dashboard integration tab."
            )

    # 2. Check Bearer Token Header (Dashboard Browser session)
    if credentials and credentials.credentials:
        token = credentials.credentials.strip()

        # Direct Auth Token Fallback (user_token_<id>)
        if token.startswith("user_token_"):
            profile_id = token.replace("user_token_", "")
            user_profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
            if user_profile:
                return user_profile, user_profile.id

        # Supabase JWT Auth Token
        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False}
            )
            auth_user_id = payload.get("sub")
            email = payload.get("email", "User")
            full_name = payload.get("user_metadata", {}).get("full_name") or email.split("@")[0]

            if auth_user_id:
                user_profile = db.query(UserProfile).filter(UserProfile.auth_user_id == auth_user_id).first()
                if not user_profile:
                    user_profile = UserProfile(
                        id=str(uuid.uuid4()),
                        auth_user_id=auth_user_id,
                        full_name=full_name,
                        role="User"
                    )
                    db.add(user_profile)
                    db.commit()
                    db.refresh(user_profile)
                    # Auto-generate API key for new Supabase user
                    generate_api_key_for_user(user_profile.id, db)

                return user_profile, user_profile.id
        except Exception:
            pass

    # 3. Default Demo Guest Fallback
    return None, DEFAULT_DEMO_USER_PROFILE_ID
