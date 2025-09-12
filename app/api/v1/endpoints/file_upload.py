"""
File Upload API Endpoints
Handles file uploads for project documents
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from pathlib import Path
from datetime import datetime
import uuid
from app.database import get_db
from app.models.main_tables import Project
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Configure upload directory
UPLOAD_DIR = Path("uploads/project_documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/project-detail/{project_id}/upload-charter")
async def upload_charter_document(
    project_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload charter document for a project"""
    try:
        # Verify project exists
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Validate file type
        allowed_types = ['.pdf', '.doc', '.docx', '.txt']
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{project_id}_charter_{file_id}{file_extension}"
        file_path = UPLOAD_DIR / filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Store file metadata in database (you can extend this)
        file_info = {
            "project_id": project_id,
            "original_filename": file.filename,
            "stored_filename": filename,
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size,
            "upload_date": datetime.now(),
            "file_type": "charter"
        }
        
        logger.info(f"Charter document uploaded for project {project_id}: {filename}")
        
        return {
            "message": "Charter document uploaded successfully",
            "file_info": file_info
        }
        
    except Exception as e:
        logger.error(f"Error uploading charter document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/project-detail/{project_id}/upload-documents")
async def upload_project_documents(
    project_id: str,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload multiple documents for a project"""
    try:
        # Verify project exists
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        uploaded_files = []
        
        for file in files:
            # Validate file type
            allowed_types = ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.png', '.jpg', '.jpeg']
            file_extension = Path(file.filename).suffix.lower()
            if file_extension not in allowed_types:
                continue  # Skip invalid files
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            filename = f"{project_id}_doc_{file_id}{file_extension}"
            file_path = UPLOAD_DIR / filename
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append({
                "original_filename": file.filename,
                "stored_filename": filename,
                "file_size": file_path.stat().st_size,
                "upload_date": datetime.now()
            })
        
        logger.info(f"Uploaded {len(uploaded_files)} documents for project {project_id}")
        
        return {
            "message": f"Successfully uploaded {len(uploaded_files)} documents",
            "uploaded_files": uploaded_files
        }
        
    except Exception as e:
        logger.error(f"Error uploading documents: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/project-detail/{project_id}/documents")
async def get_project_documents(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Get list of uploaded documents for a project"""
    try:
        # Verify project exists
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # List files in upload directory for this project
        project_files = []
        for file_path in UPLOAD_DIR.glob(f"{project_id}_*"):
            if file_path.is_file():
                project_files.append({
                    "filename": file_path.name,
                    "file_size": file_path.stat().st_size,
                    "modified_date": datetime.fromtimestamp(file_path.stat().st_mtime),
                    "file_type": file_path.suffix.lower()
                })
        
        return {
            "project_id": project_id,
            "documents": project_files
        }
        
    except Exception as e:
        logger.error(f"Error getting project documents: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/project-detail/{project_id}/documents/{filename}")
async def delete_project_document(
    project_id: str,
    filename: str,
    db: Session = Depends(get_db)
):
    """Delete a specific document for a project"""
    try:
        # Verify project exists
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Verify file belongs to project
        if not filename.startswith(project_id):
            raise HTTPException(status_code=403, detail="File does not belong to this project")
        
        file_path = UPLOAD_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete file
        file_path.unlink()
        
        logger.info(f"Deleted document {filename} for project {project_id}")
        
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
