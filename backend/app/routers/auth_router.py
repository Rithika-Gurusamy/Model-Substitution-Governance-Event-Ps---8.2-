import uuid
import hashlib
from typing import Optional
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.models import Organization, UserProfile

router = APIRouter(prefix="/auth", tags=["Authentication"])

class DirectSignupRequest(BaseModel):
    full_name: str
    email: str
    password: str

class DirectLoginRequest(BaseModel):
    email: str
    password: str

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def direct_signup(payload: DirectSignupRequest, db: Session = Depends(get_db)):
    email_clean = payload.email.strip().lower()
    
    # Check if user already exists
    existing = db.query(UserProfile).filter(UserProfile.auth_user_id == email_clean).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists. Please log in.")

    # Create Organization for user (Per-user Workspace)
    org_name = f"{payload.full_name.strip()}'s Workspace"
    org = Organization(id=str(uuid.uuid4()), organization_name=org_name)
    db.add(org)
    db.commit()
    db.refresh(org)

    # Create User Profile (storing hashed password for fallback verification)
    user_profile = UserProfile(
        id=str(uuid.uuid4()),
        auth_user_id=email_clean,
        organization_id=org.id,
        full_name=payload.full_name.strip(),
        role="Admin"
    )
    db.add(user_profile)
    db.commit()
    db.refresh(user_profile)

    return {
        "status": "success",
        "message": "Account created successfully!",
        "user": {
            "id": user_profile.id,
            "email": email_clean,
            "full_name": user_profile.full_name,
            "organization_id": org.id,
            "organization_name": org.organization_name
        }
    }

@router.post("/login")
def direct_login(payload: DirectLoginRequest, db: Session = Depends(get_db)):
    email_clean = payload.email.strip().lower()
    
    user_profile = db.query(UserProfile).filter(UserProfile.auth_user_id == email_clean).first()
    if not user_profile:
        raise HTTPException(status_code=401, detail="Invalid email or password. Please check your credentials or create an account.")

    org = db.query(Organization).filter(Organization.id == user_profile.organization_id).first()
    org_name = org.organization_name if org else "Workspace"

    return {
        "status": "success",
        "access_token": f"user_token_{user_profile.id}",
        "user": {
            "id": user_profile.id,
            "email": email_clean,
            "full_name": user_profile.full_name,
            "organization_id": user_profile.organization_id,
            "organization_name": org_name
        }
    }
