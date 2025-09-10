"""
User Management API endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return {
        "id": current_user.get("id", 1),
        "username": current_user.get("username", "admin"),
        "email": current_user.get("email", "admin@example.com"),
        "name": current_user.get("name", "Administrator"),
        "role": current_user.get("role", "admin"),
        "is_active": current_user.get("is_active", True)
    }
