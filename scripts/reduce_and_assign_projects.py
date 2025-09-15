#!/usr/bin/env python3
"""
Reduce projects to 5 and assign them to managers
"""

import asyncio
import sys
import os
from sqlalchemy.orm import Session

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models.main_tables import Project
from app.core.logging import get_logger

logger = get_logger("scripts.reduce_and_assign_projects")

def reduce_and_assign_projects():
    """Reduce projects to 5 and assign them to managers"""
    logger.info("🔧 Reducing projects to 5 and assigning to managers...")
    
    db = SessionLocal()
    try:
        # Get all projects
        all_projects = db.query(Project).all()
        logger.info(f"📊 Total projects found: {len(all_projects)}")
        
        if len(all_projects) <= 5:
            logger.info("✅ Already have 5 or fewer projects, no reduction needed")
            # Just assign the existing projects
            projects_to_keep = all_projects[:5]
        else:
            # Keep only the first 5 projects
            projects_to_keep = all_projects[:5]
            
            # Delete the rest
            projects_to_delete = all_projects[5:]
            for project in projects_to_delete:
                db.delete(project)
            
            logger.info(f"🗑️ Deleted {len(projects_to_delete)} projects")
        
        # Update the 5 projects with proper assignments
        project_assignments = [
            {"id": 1, "name": "AI-Powered Analytics Platform", "manager": "manager1"},
            {"id": 2, "name": "Digital Transformation Initiative", "manager": "manager1"},
            {"id": 3, "name": "Customer Experience Enhancement", "manager": "manager1"},
            {"id": 4, "name": "Cloud Migration Project", "manager": "manager2"},
            {"id": 5, "name": "Mobile App Development", "manager": "manager2"}
        ]
        
        for i, assignment in enumerate(project_assignments):
            if i < len(projects_to_keep):
                project = projects_to_keep[i]
                project.project_name = assignment["name"]
                project.manager_name = assignment["manager"]
                project.is_active = True
                
                # Update project details for demo
                project.description = f"Comprehensive {assignment['name'].lower()} project managed by {assignment['manager']}"
                project.status_id = 1  # Active status
                project.priority_id = 1  # High priority
                
                logger.info(f"✅ Updated project {project.id}: {assignment['name']} -> {assignment['manager']}")
        
        # Commit changes
        db.commit()
        logger.info("💾 Changes committed to database")
        
        # Verify the changes
        final_projects = db.query(Project).filter(Project.is_active == True).all()
        logger.info(f"📊 Final project count: {len(final_projects)}")
        
        for project in final_projects:
            logger.info(f"  📋 Project {project.id}: {project.project_name} (Manager: {project.manager_name})")
        
        logger.info("🎉 Project reduction and assignment completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error reducing and assigning projects: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    reduce_and_assign_projects()
