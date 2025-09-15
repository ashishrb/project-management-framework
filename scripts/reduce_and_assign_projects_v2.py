#!/usr/bin/env python3
"""
Reduce projects to 5 and assign them to managers (handling foreign key constraints)
"""

import asyncio
import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models.main_tables import Project, Task, Feature, Backlog
from app.core.logging import get_logger

logger = get_logger("scripts.reduce_and_assign_projects_v2")

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
            projects_to_keep = all_projects[:5]
        else:
            # Keep only the first 5 projects
            projects_to_keep = all_projects[:5]
            projects_to_delete = all_projects[5:]
            
            # Get IDs of projects to delete
            delete_ids = [p.id for p in projects_to_delete]
            logger.info(f"🗑️ Will delete {len(delete_ids)} projects: {delete_ids}")
            
            # Delete related data first (in correct order to avoid FK violations)
            logger.info("🧹 Cleaning up related data...")
            
            # Delete tasks for projects to be deleted
            db.execute(text("DELETE FROM tasks WHERE project_id = ANY(:project_ids)"), {"project_ids": delete_ids})
            logger.info("✅ Deleted related tasks")
            
            # Delete features for projects to be deleted
            db.execute(text("DELETE FROM features WHERE project_id = ANY(:project_ids)"), {"project_ids": delete_ids})
            logger.info("✅ Deleted related features")
            
            # Delete backlogs for projects to be deleted
            db.execute(text("DELETE FROM backlogs WHERE project_id = ANY(:project_ids)"), {"project_ids": delete_ids})
            logger.info("✅ Deleted related backlogs")
            
            # Now delete the projects
            db.execute(text("DELETE FROM projects WHERE id = ANY(:project_ids)"), {"project_ids": delete_ids})
            logger.info(f"🗑️ Deleted {len(delete_ids)} projects")
        
        # Update the 5 projects with proper assignments
        project_assignments = [
            {"id": 1, "name": "AI-Powered Analytics Platform", "manager": "manager1"},
            {"id": 2, "name": "Digital Transformation Initiative", "manager": "manager1"},
            {"id": 3, "name": "Customer Experience Enhancement", "manager": "manager1"},
            {"id": 4, "name": "Cloud Migration Project", "manager": "manager2"},
            {"id": 5, "name": "Mobile App Development", "manager": "manager2"}
        ]
        
        # Get the remaining projects (they might have different IDs now)
        remaining_projects = db.query(Project).all()
        logger.info(f"📊 Remaining projects: {len(remaining_projects)}")
        
        for i, assignment in enumerate(project_assignments):
            if i < len(remaining_projects):
                project = remaining_projects[i]
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
