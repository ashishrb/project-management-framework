"""
Risk Management API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import asyncio

from app.database import get_db
from app.api.deps import get_current_user
from app.models.main_tables import Risk, Project
from app.schemas.project_schemas import RiskResponse, RiskCreate, RiskUpdate
from app.websocket.connection_manager import connection_manager

router = APIRouter()

@router.get("/", response_model=List[RiskResponse])
async def get_risks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    project_id: Optional[int] = None,
    risk_level: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all risks with optional filtering"""
    query = db.query(Risk).filter(Risk.is_active == True)
    
    if project_id:
        query = query.filter(Risk.project_id == project_id)
    if risk_level:
        query = query.filter(Risk.risk_level == risk_level)
    if status:
        query = query.filter(Risk.status == status)
    
    risks = query.offset(skip).limit(limit).all()
    return risks

@router.get("/{risk_id}", response_model=RiskResponse)
async def get_risk(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific risk by ID"""
    risk = db.query(Risk).filter(Risk.id == risk_id, Risk.is_active == True).first()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    return risk

@router.post("/", response_model=RiskResponse)
async def create_risk(
    risk: RiskCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new risk"""
    # Verify project exists
    project = db.query(Project).filter(Project.id == risk.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_risk = Risk(**risk.dict())
    db.add(db_risk)
    db.commit()
    db.refresh(db_risk)
    # WebSocket notify
    try:
        message = {"type": "risk_created", "risk_id": db_risk.id, "project_id": db_risk.project_id}
        connection_manager.queue_message(message, room="risks")
        asyncio.get_event_loop().create_task(connection_manager.broadcast_to_room(message, room="risks"))
    except Exception:
        pass
    return db_risk

@router.put("/{risk_id}", response_model=RiskResponse)
async def update_risk(
    risk_id: int,
    risk: RiskUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update an existing risk"""
    db_risk = db.query(Risk).filter(Risk.id == risk_id, Risk.is_active == True).first()
    if not db_risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    
    update_data = risk.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_risk, field, value)
    
    db.commit()
    db.refresh(db_risk)
    # WebSocket notify
    try:
        message = {"type": "risk_updated", "risk_id": db_risk.id, "project_id": db_risk.project_id}
        connection_manager.queue_message(message, room="risks")
        asyncio.get_event_loop().create_task(connection_manager.broadcast_to_room(message, room="risks"))
    except Exception:
        pass
    return db_risk

@router.delete("/{risk_id}")
async def delete_risk(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a risk (soft delete)"""
    db_risk = db.query(Risk).filter(Risk.id == risk_id, Risk.is_active == True).first()
    if not db_risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    
    db_risk.is_active = False
    db.commit()
    # WebSocket notify
    try:
        message = {"type": "risk_deleted", "risk_id": db_risk.id}
        connection_manager.queue_message(message, room="risks")
        asyncio.get_event_loop().create_task(connection_manager.broadcast_to_room(message, room="risks"))
    except Exception:
        pass
    return {"message": "Risk deleted successfully"}

@router.get("/project/{project_id}", response_model=List[RiskResponse])
async def get_project_risks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all risks for a specific project"""
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    risks = db.query(Risk).filter(
        Risk.project_id == project_id,
        Risk.is_active == True
    ).all()
    return risks
