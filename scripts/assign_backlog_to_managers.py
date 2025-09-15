#!/usr/bin/env python3
"""
Script to assign backlog items to manager projects for demo purposes.
This creates realistic backlog assignments for the two managers.
"""

import os
import sys
import logging

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.main_tables import Project, Backlog

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

def assign_backlog_to_managers():
    """Assign backlog items to manager projects for demo"""
    logger.info("🔧 Assigning backlog items to manager projects...")
    db: Session = SessionLocal()
    try:
        # Get manager projects
        manager1_projects = db.query(Project).filter(
            Project.project_manager == "manager1",
            Project.is_active == True
        ).all()
        
        manager2_projects = db.query(Project).filter(
            Project.project_manager == "manager2", 
            Project.is_active == True
        ).all()
        
        logger.info(f"📊 Found {len(manager1_projects)} projects for manager1")
        logger.info(f"📊 Found {len(manager2_projects)} projects for manager2")
        
        # Get available backlog items
        backlog_items = db.query(Backlog).limit(20).all()
        logger.info(f"📋 Found {len(backlog_items)} backlog items to assign")
        
        # For demo purposes, we'll add a project_manager field to backlog items
        # Assign backlog items to manager1 projects (3 projects)
        manager1_project_ids = [p.id for p in manager1_projects]
        manager1_backlog_count = 0
        
        for i, backlog in enumerate(backlog_items[:12]):  # Assign first 12 items
            if i < len(manager1_project_ids):
                project_id = manager1_project_ids[i % len(manager1_project_ids)]
                # Add project manager assignment to description for demo
                backlog.description = f"{backlog.description or ''} [Assigned to Project {project_id} - Manager1]"
                manager1_backlog_count += 1
                logger.info(f"✅ Assigned '{backlog.name}' to manager1 project {project_id}")
        
        # Assign remaining backlog items to manager2 projects (2 projects)
        manager2_project_ids = [p.id for p in manager2_projects]
        manager2_backlog_count = 0
        
        for i, backlog in enumerate(backlog_items[12:]):  # Assign remaining items
            if i < len(manager2_project_ids):
                project_id = manager2_project_ids[i % len(manager2_project_ids)]
                # Add project manager assignment to description for demo
                backlog.description = f"{backlog.description or ''} [Assigned to Project {project_id} - Manager2]"
                manager2_backlog_count += 1
                logger.info(f"✅ Assigned '{backlog.name}' to manager2 project {project_id}")
        
        # Commit changes
        db.commit()
        logger.info("💾 Changes committed to database")
        
        # Verify assignments
        logger.info("📊 Backlog Assignment Summary:")
        logger.info(f"  Manager1: {manager1_backlog_count} backlog items across {len(manager1_projects)} projects")
        logger.info(f"  Manager2: {manager2_backlog_count} backlog items across {len(manager2_projects)} projects")
        
        # Show project details
        for project in manager1_projects:
            # Count backlog items assigned to this project (by description)
            project_backlogs = db.query(Backlog).filter(
                Backlog.description.like(f"%Project {project.id} - Manager1%")
            ).count()
            logger.info(f"  📋 {project.name}: {project_backlogs} backlog items")
            
        for project in manager2_projects:
            # Count backlog items assigned to this project (by description)
            project_backlogs = db.query(Backlog).filter(
                Backlog.description.like(f"%Project {project.id} - Manager2%")
            ).count()
            logger.info(f"  📋 {project.name}: {project_backlogs} backlog items")
        
        logger.info("🎉 Backlog assignment completed successfully!")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error assigning backlog items: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    assign_backlog_to_managers()
