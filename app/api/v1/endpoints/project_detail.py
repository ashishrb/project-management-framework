"""
Project Detail Management API Endpoints
Comprehensive project detail management based on screenshots
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from app.database import get_db
from app.models.main_tables import Project
from app.models.project_detail_models import (
    ProjectStakeholder, ProjectCharter, ProjectNIST, 
    ProjectLifecycle, ProjectDependency, ProjectApplication,
    ProjectBaseline, ProjectStatusDetail
)
from app.models.project_detail_lookups import (
    DemandCategory, ModernizationDomain, DigitizationCategory,
    DeliveryOrganization, ExpenseType, BusinessProcess,
    GenerativeAIImpact, ProjectPhase, ProjectState,
    NISTDomain, NISTMapping
)
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/project-detail/{project_id}")
async def get_project_detail(
    project_id: str,
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get comprehensive project detail information"""
    try:
        # Get project basic information
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get project stakeholders
        stakeholders = db.query(ProjectStakeholder).filter(
            ProjectStakeholder.project_id == project.id
        ).all()
        
        # Get project charter
        charter = db.query(ProjectCharter).filter(
            ProjectCharter.project_id == project.id
        ).first()
        
        # Get project NIST information
        nist_info = db.query(ProjectNIST).filter(
            ProjectNIST.project_id == project.id
        ).first()
        
        # Get project lifecycle
        lifecycle = db.query(ProjectLifecycle).filter(
            ProjectLifecycle.project_id == project.id
        ).first()
        
        # Get project dependencies
        dependencies = db.query(ProjectDependency).filter(
            ProjectDependency.project_id == project.id
        ).all()
        
        # Get project applications
        applications = db.query(ProjectApplication).filter(
            ProjectApplication.project_id == project.id
        ).all()
        
        # Get project baseline
        baseline = db.query(ProjectBaseline).filter(
            ProjectBaseline.project_id == project.id
        ).first()
        
        # Get project status details
        status_detail = db.query(ProjectStatusDetail).filter(
            ProjectStatusDetail.project_id == project.id
        ).first()
        
        # Get lookup data
        lookup_data = {
            "demand_categories": db.query(DemandCategory).all(),
            "modernization_domains": db.query(ModernizationDomain).all(),
            "digitization_categories": db.query(DigitizationCategory).all(),
            "delivery_organizations": db.query(DeliveryOrganization).all(),
            "expense_types": db.query(ExpenseType).all(),
            "business_processes": db.query(BusinessProcess).all(),
            "generative_ai_impacts": db.query(GenerativeAIImpact).all(),
            "project_phases": db.query(ProjectPhase).all(),
            "project_states": db.query(ProjectState).all(),
            "nist_domains": db.query(NISTDomain).all(),
            "nist_mappings": db.query(NISTMapping).all(),
        }
        
        return {
            "project": project,
            "stakeholders": stakeholders,
            "charter": charter,
            "nist_info": nist_info,
            "lifecycle": lifecycle,
            "dependencies": dependencies,
            "applications": applications,
            "baseline": baseline,
            "status_detail": status_detail,
            "lookup_data": lookup_data
        }
        
    except Exception as e:
        logger.error(f"Error getting project detail: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/project-detail-lookups")
async def get_project_detail_lookups(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get all lookup data for project detail forms"""
    try:
        return {
            "demand_categories": db.query(DemandCategory).all(),
            "modernization_domains": db.query(ModernizationDomain).all(),
            "digitization_categories": db.query(DigitizationCategory).all(),
            "delivery_organizations": db.query(DeliveryOrganization).all(),
            "expense_types": db.query(ExpenseType).all(),
            "business_processes": db.query(BusinessProcess).all(),
            "generative_ai_impacts": db.query(GenerativeAIImpact).all(),
            "project_phases": db.query(ProjectPhase).all(),
            "project_states": db.query(ProjectState).all(),
            "nist_domains": db.query(NISTDomain).all(),
            "nist_mappings": db.query(NISTMapping).all(),
        }
    except Exception as e:
        logger.error(f"Error getting lookup data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/project-detail/{project_id}/stakeholders")
async def update_project_stakeholders(
    project_id: str,
    stakeholders_data: List[Dict[str, Any]],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update project stakeholders"""
    try:
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Delete existing stakeholders
        db.query(ProjectStakeholder).filter(
            ProjectStakeholder.project_id == project.id
        ).delete()
        
        # Add new stakeholders
        for stakeholder_data in stakeholders_data:
            stakeholder = ProjectStakeholder(
                project_id=project.id,
                stakeholder_type=stakeholder_data.get("stakeholder_type"),
                name=stakeholder_data.get("name"),
                email=stakeholder_data.get("email"),
                role=stakeholder_data.get("role"),
                department=stakeholder_data.get("department"),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(stakeholder)
        
        db.commit()
        return {"message": "Stakeholders updated successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating stakeholders: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/project-detail/{project_id}/charter")
async def update_project_charter(
    project_id: str,
    charter_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update project charter"""
    try:
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get or create charter
        charter = db.query(ProjectCharter).filter(
            ProjectCharter.project_id == project.id
        ).first()
        
        if not charter:
            charter = ProjectCharter(project_id=project.id)
            db.add(charter)
        
        # Update charter data
        for key, value in charter_data.items():
            if hasattr(charter, key):
                setattr(charter, key, value)
        
        charter.updated_at = datetime.now()
        db.commit()
        
        return {"message": "Charter updated successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating charter: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/project-detail/{project_id}/nist")
async def update_project_nist(
    project_id: str,
    nist_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update project NIST information"""
    try:
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get or create NIST info
        nist_info = db.query(ProjectNIST).filter(
            ProjectNIST.project_id == project.id
        ).first()
        
        if not nist_info:
            nist_info = ProjectNIST(project_id=project.id)
            db.add(nist_info)
        
        # Update NIST data
        for key, value in nist_data.items():
            if hasattr(nist_info, key):
                setattr(nist_info, key, value)
        
        nist_info.updated_at = datetime.now()
        db.commit()
        
        return {"message": "NIST information updated successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating NIST information: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/project-detail/{project_id}/lifecycle")
async def update_project_lifecycle(
    project_id: str,
    lifecycle_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update project lifecycle"""
    try:
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get or create lifecycle
        lifecycle = db.query(ProjectLifecycle).filter(
            ProjectLifecycle.project_id == project.id
        ).first()
        
        if not lifecycle:
            lifecycle = ProjectLifecycle(project_id=project.id)
            db.add(lifecycle)
        
        # Update lifecycle data
        for key, value in lifecycle_data.items():
            if hasattr(lifecycle, key):
                setattr(lifecycle, key, value)
        
        lifecycle.updated_at = datetime.now()
        db.commit()
        
        return {"message": "Lifecycle updated successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating lifecycle: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/project-detail/{project_id}")
async def save_project_detail(
    project_id: str,
    project_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Save comprehensive project detail data"""
    try:
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Update basic project information
        if 'esa_id' in project_data:
            project.esa_id = project_data['esa_id']
        if 'top_level_portfolio' in project_data:
            project.top_level_portfolio = project_data['top_level_portfolio']
        if 'sub_portfolio' in project_data:
            project.sub_portfolio = project_data['sub_portfolio']
        if 'modernization_domain' in project_data:
            project.modernization_domain = project_data['modernization_domain']
        if 'digitization_category' in project_data:
            project.digitization_category = project_data['digitization_category']
        if 'business_owner' in project_data:
            project.business_owner = project_data['business_owner']
        if 'technology_portfolio_leader' in project_data:
            project.technology_portfolio_leader = project_data['technology_portfolio_leader']
        
        project.updated_at = datetime.now()
        
        # Save stakeholders
        if 'stakeholders' in project_data:
            await update_project_stakeholders(project_id, [project_data['stakeholders']], db)
        
        # Save charter information
        if 'charter' in project_data:
            await update_project_charter(project_id, project_data['charter'], db)
        
        # Save NIST information
        if 'nist' in project_data:
            await update_project_nist(project_id, project_data['nist'], db)
        
        # Save lifecycle information
        if 'lifecycle' in project_data:
            await update_project_lifecycle(project_id, project_data['lifecycle'], db)
        
        db.commit()
        
        action = project_data.get('action', 'save')
        message = f"Project {'draft saved' if action == 'draft' else 'submitted'} successfully"
        
        return {"message": message, "project_id": project_id}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving project detail: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
