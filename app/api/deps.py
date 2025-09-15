from typing import Optional, List
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.main_tables import Project
import json
import base64

def decode_user_data(encoded_data):
    """Simple base64 decoding for demo"""
    try:
        return json.loads(base64.b64decode(encoded_data.encode()).decode())
    except:
        return None

# Simple cookie-based auth for demo
def get_current_user(request: Request):
    """Get current user from cookie - simplified for demo"""
    try:
        user_cookie = request.cookies.get("user_session")
        if user_cookie:
            user_data = decode_user_data(user_cookie)
            if user_data:
                return {
                    "user_id": user_data.get("id"),
                    "username": user_data.get("username"),
                    "role": user_data.get("role", "guest"),
                    "email": user_data.get("email")
                }
        
        # Return guest user for unauthenticated access
        return {
            "user_id": None,
            "username": "guest",
            "role": "guest",
            "email": None
        }
    except Exception as e:
        # Return guest user on any error
        return {
            "user_id": None,
            "username": "guest", 
            "role": "guest",
            "email": None
        }

def get_current_admin_user(request: Request):
    """Get current admin user - simplified for demo"""
    user = get_current_user(request)
    if user.get("role") == "admin":
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

def get_demo_project_ids(db: Session, limit: int = 10) -> List[int]:
    """Get demo project IDs for demo mode"""
    try:
        projects = db.query(Project).filter(Project.is_active == True).limit(limit).all()
        return [p.id for p in projects]
    except Exception:
        return []