#!/usr/bin/env python3
"""
Clear existing demo data from the database
"""

import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.main_tables import Project, Feature, Backlog, Resource, Task, Risk

def clear_demo_data():
    """Clear all demo data from the database"""
    db = SessionLocal()
    
    try:
        print("🧹 Clearing existing demo data...")
        
        # Clear in reverse order of dependencies
        print("  - Clearing risks...")
        db.query(Risk).delete()
        
        print("  - Clearing tasks...")
        db.query(Task).delete()
        
        print("  - Clearing backlogs...")
        db.query(Backlog).delete()
        
        print("  - Clearing features...")
        db.query(Feature).delete()
        
        print("  - Clearing resources...")
        db.query(Resource).delete()
        
        print("  - Clearing projects...")
        db.query(Project).delete()
        
        db.commit()
        print("✅ Demo data cleared successfully!")
        
    except Exception as e:
        print(f"❌ Error clearing demo data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    clear_demo_data()
