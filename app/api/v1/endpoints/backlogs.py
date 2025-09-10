"""
Backlogs API Endpoints
Provides endpoints for managing project backlogs
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.main_tables import Backlog
from app.schemas.project_schemas import BacklogResponse, BacklogCreate, BacklogUpdate
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.get("/", response_model=List[BacklogResponse])
async def get_all_backlogs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all backlogs with pagination"""
    try:
        logger.log_function_entry("get_all_backlogs", [skip, limit])
        
        backlogs = db.query(Backlog).offset(skip).limit(limit).all()
        
        logger.log_function_exit("get_all_backlogs", {"count": len(backlogs)})
        return backlogs
        
    except Exception as e:
        logger.log_error("get_all_backlogs", e, {"skip": skip, "limit": limit})
        raise HTTPException(status_code=500, detail="Failed to fetch backlogs")

@router.get("/{backlog_id}", response_model=BacklogResponse)
async def get_backlog(
    backlog_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific backlog by ID"""
    try:
        logger.log_function_entry("get_backlog", [backlog_id])
        
        backlog = db.query(Backlog).filter(Backlog.id == backlog_id).first()
        if not backlog:
            raise HTTPException(status_code=404, detail="Backlog not found")
        
        logger.log_function_exit("get_backlog", {"backlog_id": backlog_id})
        return backlog
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error("get_backlog", e, {"backlog_id": backlog_id})
        raise HTTPException(status_code=500, detail="Failed to fetch backlog")

@router.post("/", response_model=BacklogResponse)
async def create_backlog(
    backlog: BacklogCreate,
    db: Session = Depends(get_db)
):
    """Create a new backlog item"""
    try:
        logger.log_function_entry("create_backlog", [backlog])
        
        db_backlog = Backlog(**backlog.dict())
        db.add(db_backlog)
        db.commit()
        db.refresh(db_backlog)
        
        logger.log_function_exit("create_backlog", {"backlog_id": db_backlog.id})
        return db_backlog
        
    except Exception as e:
        logger.log_error("create_backlog", e, {"backlog": backlog.dict()})
        raise HTTPException(status_code=500, detail="Failed to create backlog")

@router.put("/{backlog_id}", response_model=BacklogResponse)
async def update_backlog(
    backlog_id: int,
    backlog: BacklogUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing backlog item"""
    try:
        logger.log_function_entry("update_backlog", [backlog_id, backlog])
        
        db_backlog = db.query(Backlog).filter(Backlog.id == backlog_id).first()
        if not db_backlog:
            raise HTTPException(status_code=404, detail="Backlog not found")
        
        for field, value in backlog.dict(exclude_unset=True).items():
            setattr(db_backlog, field, value)
        
        db.commit()
        db.refresh(db_backlog)
        
        logger.log_function_exit("update_backlog", {"backlog_id": backlog_id})
        return db_backlog
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error("update_backlog", e, {"backlog_id": backlog_id, "backlog": backlog.dict()})
        raise HTTPException(status_code=500, detail="Failed to update backlog")

@router.delete("/{backlog_id}")
async def delete_backlog(
    backlog_id: int,
    db: Session = Depends(get_db)
):
    """Delete a backlog item"""
    try:
        logger.log_function_entry("delete_backlog", [backlog_id])
        
        db_backlog = db.query(Backlog).filter(Backlog.id == backlog_id).first()
        if not db_backlog:
            raise HTTPException(status_code=404, detail="Backlog not found")
        
        db.delete(db_backlog)
        db.commit()
        
        logger.log_function_exit("delete_backlog", {"backlog_id": backlog_id})
        return {"message": "Backlog deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error("delete_backlog", e, {"backlog_id": backlog_id})
        raise HTTPException(status_code=500, detail="Failed to delete backlog")
