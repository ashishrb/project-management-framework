"""
Features API Endpoints
Provides REST API for feature management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.main_tables import Feature
from app.schemas.project_schemas import FeatureResponse, FeatureCreate, FeatureUpdate
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=List[FeatureResponse])
def get_features(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all features with pagination."""
    try:
        features = db.query(Feature).offset(skip).limit(limit).all()
        return features
    except Exception as e:
        logger.error(f"Error fetching features: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{feature_id}", response_model=FeatureResponse)
def get_feature(
    feature_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific feature by ID."""
    try:
        feature = db.query(Feature).filter(Feature.id == feature_id).first()
        if not feature:
            raise HTTPException(status_code=404, detail="Feature not found")
        return feature
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching feature {feature_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=FeatureResponse)
def create_feature(
    feature: FeatureCreate,
    db: Session = Depends(get_db)
):
    """Create a new feature."""
    try:
        db_feature = Feature(**feature.dict())
        db.add(db_feature)
        db.commit()
        db.refresh(db_feature)
        return db_feature
    except Exception as e:
        logger.error(f"Error creating feature: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{feature_id}", response_model=FeatureResponse)
def update_feature(
    feature_id: int,
    feature: FeatureUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing feature."""
    try:
        db_feature = db.query(Feature).filter(Feature.id == feature_id).first()
        if not db_feature:
            raise HTTPException(status_code=404, detail="Feature not found")
        
        for field, value in feature.dict(exclude_unset=True).items():
            setattr(db_feature, field, value)
        
        db.commit()
        db.refresh(db_feature)
        return db_feature
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating feature {feature_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{feature_id}")
def delete_feature(
    feature_id: int,
    db: Session = Depends(get_db)
):
    """Delete a feature."""
    try:
        db_feature = db.query(Feature).filter(Feature.id == feature_id).first()
        if not db_feature:
            raise HTTPException(status_code=404, detail="Feature not found")
        
        db.delete(db_feature)
        db.commit()
        return {"message": "Feature deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting feature {feature_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
