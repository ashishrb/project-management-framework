"""
API dependencies for GenAI Metrics Dashboard
"""
from typing import Generator, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.database import SessionLocal
from app.config import settings
from app.models.main_tables import Project
from app.config import settings

# Auth constants
ACCESS_TOKEN_COOKIE = "access_token"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY

# Security
security = HTTPBearer(auto_error=False)

def get_db() -> Generator:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Resolve current user from Bearer token or httpOnly cookie; fall back to guest."""
    token: Optional[str] = None
    if credentials and credentials.scheme.lower() == "bearer":
        token = credentials.credentials
    if not token:
        token = request.cookies.get(ACCESS_TOKEN_COOKIE)

    if token:
        data = _decode_token(token)
        if data:
            # minimal normalized user dict
            return {
                "user_id": data.get("sub"),
                "email": data.get("email"),
                "username": data.get("name") or data.get("email"),
                "role": data.get("role", "guest").lower(),
                "exp": data.get("exp")
            }

    # guest user for unauthenticated access to public pages
    return {
        "user_id": None,
        "username": "guest",
        "role": "guest",
        "email": None
    }

def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    """Get current admin user"""
    if (current_user.get("role") or "").lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def get_current_manager_user(current_user: dict = Depends(get_current_user)):
    """Get current manager user"""
    role = (current_user.get("role") or "").lower()
    if role not in ["admin", "manager", "owner", "portfolio"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def require_roles(*allowed_roles: str):
    def _dep(current_user: dict = Depends(get_current_user)):
        role = (current_user.get("role") or "").lower()
        if role not in [r.lower() for r in allowed_roles]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return current_user
    return _dep


# Demo-mode helpers
def get_demo_project_ids(db: Session, limit: int = 10):
    """Return curated project IDs for demo mode (most recently updated)."""
    ids = [pid for (pid,) in db.query(Project.id).order_by(Project.updated_at.desc().nullslast()).limit(limit).all()]
    return ids
