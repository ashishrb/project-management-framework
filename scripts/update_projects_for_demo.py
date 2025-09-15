#!/usr/bin/env python3
"""
Update projects for demo - assign first 5 projects to managers
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

logger = get_logger("scripts.update_projects_for_demo")

def update_projects_for_demo():
    """Update first 5 projects for demo with manager assignments"""
    logger.info("🔧 Updating projects for demo...")
    
    db = SessionLocal()
    try:
        # Get first 5 projects
        projects = db.query(Project).limit(5).all()
        logger.info(f"📊 Found {len(projects)} projects to update")
        
        # Project assignments
        project_assignments = [
            {"name": "AI-Powered Analytics Platform", "manager": "manager1"},
            {"name": "Digital Transformation Initiative", "manager": "manager1"},
            {"name": "Customer Experience Enhancement", "manager": "manager1"},
            {"name": "Cloud Migration Project", "manager": "manager2"},
            {"name": "Mobile App Development", "manager": "manager2"}
        ]
        
        # Update each project
        for i, project in enumerate(projects):
            if i < len(project_assignments):
                assignment = project_assignments[i]
                
                # Update project details
                project.name = assignment["name"]
                project.manager_name = assignment["manager"]
                project.is_active = True
                project.description = f"Comprehensive {assignment['name'].lower()} project managed by {assignment['manager']}"
                project.status_id = 1  # Active status
                project.priority_id = 1  # High priority
                
                logger.info(f"✅ Updated project {project.id}: {assignment['name']} -> {assignment['manager']}")
        
        # Deactivate all other projects (don't delete to avoid FK issues)
        other_projects = db.query(Project).offset(5).all()
        for project in other_projects:
            project.is_active = False
            logger.info(f"🔒 Deactivated project {project.id}: {project.name}")
        
        # Commit changes
        db.commit()
        logger.info("💾 Changes committed to database")
        
        # Verify the changes
        active_projects = db.query(Project).filter(Project.is_active == True).all()
        logger.info(f"📊 Active project count: {len(active_projects)}")
        
        for project in active_projects:
            logger.info(f"  📋 Project {project.id}: {project.name} (Manager: {project.manager_name})")
        
        logger.info("🎉 Project update completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error updating projects: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_projects_for_demo()
