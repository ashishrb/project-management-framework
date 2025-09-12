"""
Approval Workflow API Endpoints
Handles project approval workflows and status tracking
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime
from app.database import get_db
from app.models.main_tables import Project
from app.models.project_detail_models import ProjectCharter
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ApprovalWorkflow:
    """Approval workflow management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_approval_status(self, project_id: str) -> Dict[str, Any]:
        """Get current approval status for a project"""
        project = self.db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        charter = self.db.query(ProjectCharter).filter(ProjectCharter.project_id == project.id).first()
        
        status = {
            "project_id": project_id,
            "overall_status": "Pending",
            "approvals": {
                "risk_management": {
                    "status": charter.risk_management_approval if charter else "Pending",
                    "approver": charter.risk_approver if charter else None,
                    "approval_date": charter.risk_approval_date if charter else None,
                    "required": True
                },
                "charter": {
                    "status": charter.charter_approved if charter else "Pending",
                    "approver": charter.charter_approver if charter else None,
                    "approval_date": charter.charter_approval_date if charter else None,
                    "required": True
                },
                "business_owner": {
                    "status": "Approved" if project.business_owner else "Pending",
                    "approver": project.business_owner,
                    "approval_date": project.updated_at,
                    "required": True
                }
            }
        }
        
        # Determine overall status
        all_approved = all(
            approval["status"] == "Approved" 
            for approval in status["approvals"].values() 
            if approval["required"]
        )
        
        if all_approved:
            status["overall_status"] = "Approved"
        elif any(approval["status"] == "Rejected" for approval in status["approvals"].values()):
            status["overall_status"] = "Rejected"
        else:
            status["overall_status"] = "Pending"
        
        return status
    
    def approve(self, project_id: str, approval_type: str, approver: str, comments: str = None) -> Dict[str, Any]:
        """Approve a specific approval type for a project"""
        project = self.db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        charter = self.db.query(ProjectCharter).filter(ProjectCharter.project_id == project.id).first()
        if not charter:
            charter = ProjectCharter(project_id=project.id)
            self.db.add(charter)
        
        if approval_type == "risk_management":
            charter.risk_management_approval = "Approved"
            charter.risk_approver = approver
            charter.risk_approval_date = datetime.now()
        elif approval_type == "charter":
            charter.charter_approved = "Approved"
            charter.charter_approver = approver
            charter.charter_approval_date = datetime.now()
        elif approval_type == "business_owner":
            project.business_owner = approver
            project.updated_at = datetime.now()
        else:
            raise HTTPException(status_code=400, detail="Invalid approval type")
        
        charter.updated_at = datetime.now()
        self.db.commit()
        
        logger.info(f"Approval {approval_type} approved for project {project_id} by {approver}")
        
        return {
            "message": f"{approval_type.replace('_', ' ').title()} approved successfully",
            "approver": approver,
            "approval_date": datetime.now()
        }
    
    def reject(self, project_id: str, approval_type: str, approver: str, reason: str) -> Dict[str, Any]:
        """Reject a specific approval type for a project"""
        project = self.db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        charter = self.db.query(ProjectCharter).filter(ProjectCharter.project_id == project.id).first()
        if not charter:
            charter = ProjectCharter(project_id=project.id)
            self.db.add(charter)
        
        if approval_type == "risk_management":
            charter.risk_management_approval = "Rejected"
            charter.risk_approver = approver
            charter.risk_approval_date = datetime.now()
        elif approval_type == "charter":
            charter.charter_approved = "Rejected"
            charter.charter_approver = approver
            charter.charter_approval_date = datetime.now()
        else:
            raise HTTPException(status_code=400, detail="Invalid approval type")
        
        charter.updated_at = datetime.now()
        self.db.commit()
        
        logger.info(f"Approval {approval_type} rejected for project {project_id} by {approver}. Reason: {reason}")
        
        return {
            "message": f"{approval_type.replace('_', ' ').title()} rejected",
            "approver": approver,
            "rejection_date": datetime.now(),
            "reason": reason
        }

@router.get("/project-detail/{project_id}/approval-status")
async def get_approval_status(
    project_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get approval status for a project"""
    workflow = ApprovalWorkflow(db)
    return workflow.get_approval_status(project_id)

@router.post("/project-detail/{project_id}/approve/{approval_type}")
async def approve_project(
    project_id: str,
    approval_type: str,
    approver: str,
    comments: str = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Approve a specific approval type for a project"""
    workflow = ApprovalWorkflow(db)
    return workflow.approve(project_id, approval_type, approver, comments)

@router.post("/project-detail/{project_id}/reject/{approval_type}")
async def reject_project(
    project_id: str,
    approval_type: str,
    approver: str,
    reason: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Reject a specific approval type for a project"""
    workflow = ApprovalWorkflow(db)
    return workflow.reject(project_id, approval_type, approver, reason)

@router.get("/project-detail/{project_id}/approval-history")
async def get_approval_history(
    project_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get approval history for a project"""
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    charter = db.query(ProjectCharter).filter(ProjectCharter.project_id == project.id).first()
    
    history = []
    
    if charter:
        if charter.risk_approval_date:
            history.append({
                "approval_type": "Risk Management",
                "status": charter.risk_management_approval,
                "approver": charter.risk_approver,
                "date": charter.risk_approval_date,
                "type": "approval"
            })
        
        if charter.charter_approval_date:
            history.append({
                "approval_type": "Charter",
                "status": charter.charter_approved,
                "approver": charter.charter_approver,
                "date": charter.charter_approval_date,
                "type": "approval"
            })
    
    # Sort by date (most recent first)
    history.sort(key=lambda x: x["date"], reverse=True)
    
    return {
        "project_id": project_id,
        "approval_history": history
    }
