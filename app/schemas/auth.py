"""
Authentication schemas
"""
from pydantic import BaseModel
from typing import List, Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    name: str
    email: str
    assigned_projects: List[int]

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
    message: str
