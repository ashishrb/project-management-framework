# API v1 package
from fastapi import APIRouter
from app.api.v1.endpoints import auth

api_router = APIRouter()

# Include auth router
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
