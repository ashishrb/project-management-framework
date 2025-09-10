"""
API dependencies for GenAI Metrics Dashboard
"""
from typing import Generator, Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database import SessionLocal
from app.config import settings

# Security
security = HTTPBearer(auto_error=False)

def get_db() -> Generator:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Get current authenticated user (placeholder for now)"""
    # TODO: Implement proper JWT token validation
    # For now, return a mock user
    return {
        "user_id": 1,
        "username": "admin",
        "role": "admin",
        "email": "admin@example.com"
    }

def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    """Get current admin user"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def get_current_manager_user(current_user: dict = Depends(get_current_user)):
    """Get current manager user"""
    if current_user.get("role") not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
