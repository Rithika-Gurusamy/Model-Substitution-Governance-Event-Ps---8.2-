import uuid
import hashlib
from typing import Optional, Tuple
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.models import UserProfile, ApiKey
from backend.app.auth import get_current_user_and_org, generate_api_key_for_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

class DirectSignupRequest(BaseModel):
    full_name: str
    email: str
    password: str

class DirectLoginRequest(BaseModel):
    email: str
    password: str

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def direct_signup(payload: DirectSignupRequest, db: Session = Depends(get_db)):
    email_clean = payload.email.strip().lower()
    
    # Check if user already exists
    existing = db.query(UserProfile).filter(UserProfile.auth_user_id == email_clean).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists. Please log in.")

    # Create User Profile
    user_profile = UserProfile(
        id=str(uuid.uuid4()),
        auth_user_id=email_clean,
        full_name=payload.full_name.strip(),
        role="User"
    )
    db.add(user_profile)
    db.commit()
    db.refresh(user_profile)

    # Auto-generate Developer API Key for SDK integration
    raw_api_key = generate_api_key_for_user(user_profile.id, db)

    return {
        "status": "success",
        "message": "Account created successfully!",
        "access_token": f"user_token_{user_profile.id}",
        "api_key": raw_api_key,
        "user": {
            "id": user_profile.id,
            "email": email_clean,
            "full_name": user_profile.full_name,
            "role": user_profile.role
        }
    }

@router.post("/login")
def direct_login(payload: DirectLoginRequest, db: Session = Depends(get_db)):
    email_clean = payload.email.strip().lower()

    user_profile = db.query(UserProfile).filter(UserProfile.auth_user_id == email_clean).first()
    if not user_profile:
        raise HTTPException(status_code=401, detail="Invalid email or password. Please check your credentials or create an account.")

    # Retrieve existing API key or generate one if user doesn't have one
    key_obj = db.query(ApiKey).filter(ApiKey.user_profile_id == user_profile.id).order_by(ApiKey.created_at.desc()).first()
    if not key_obj:
        raw_api_key = generate_api_key_for_user(user_profile.id, db)
        key_prefix = raw_api_key[:12]
    else:
        raw_api_key = None
        key_prefix = key_obj.key_prefix

    return {
        "status": "success",
        "access_token": f"user_token_{user_profile.id}",
        "api_key": raw_api_key,
        "key_prefix": key_prefix,
        "user": {
            "id": user_profile.id,
            "email": email_clean,
            "full_name": user_profile.full_name,
            "role": user_profile.role
        }
    }

@router.get("/me")
def get_me(
    auth_data: Tuple[Optional[UserProfile], str] = Depends(get_current_user_and_org),
    db: Session = Depends(get_db)
):
    user_profile, user_profile_id = auth_data
    if not user_profile:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "id": user_profile.id,
        "email": user_profile.auth_user_id,
        "full_name": user_profile.full_name,
        "role": user_profile.role
    }

@router.get("/api-key")
def get_user_api_key(
    auth_data: Tuple[Optional[UserProfile], str] = Depends(get_current_user_and_org),
    db: Session = Depends(get_db)
):
    user_profile, user_profile_id = auth_data
    key_obj = db.query(ApiKey).filter(ApiKey.user_profile_id == user_profile_id).order_by(ApiKey.created_at.desc()).first()
    if not key_obj:
        raw_key = generate_api_key_for_user(user_profile_id, db)
        return {
            "key_prefix": raw_key[:12],
            "api_key": raw_key,
            "created_at": None
        }
    return {
        "key_prefix": key_obj.key_prefix,
        "api_key": None, # Unhashed raw secret only shown when newly created or regenerated
        "created_at": key_obj.created_at
    }

@router.post("/api-key/regenerate")
def regenerate_api_key(
    auth_data: Tuple[Optional[UserProfile], str] = Depends(get_current_user_and_org),
    db: Session = Depends(get_db)
):
    user_profile, user_profile_id = auth_data
    # Delete old API keys for this user profile
    db.query(ApiKey).filter(ApiKey.user_profile_id == user_profile_id).delete()
    db.commit()

    # Generate new key
    raw_api_key = generate_api_key_for_user(user_profile_id, db)
    return {
        "status": "success",
        "message": "New API Key generated successfully! Update your SDK configuration.",
        "api_key": raw_api_key,
        "key_prefix": raw_api_key[:12]
    }
