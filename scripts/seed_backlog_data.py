#!/usr/bin/env python3
"""
Seed Backlog Data Script
Populates the backlog table with realistic sample data
"""

import sys
import os
from datetime import datetime, date, timedelta
from decimal import Decimal

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.main_tables import Backlog
from app.models.lookup_tables import Status, Priority

def create_backlog_data():
    """Create realistic backlog data"""
    
    db = SessionLocal()
    
    try:
        # Get status and priority data
        statuses = db.query(Status).all()
        priorities = db.query(Priority).all()
        
        if not statuses:
            print("❌ No statuses found in database. Please run seed_lookup_data.py first.")
            return False
            
        if not priorities:
            print("❌ No priorities found in database. Please run seed_lookup_data.py first.")
            return False
        
        # Create status and priority mappings
        status_map = {status.name: status.id for status in statuses}
        priority_map = {priority.name: priority.id for priority in priorities}
        
        # Sample backlog items
        backlog_items = [
            {
                "backlog_id": "BL-001",
                "name": "User Authentication System",
                "description": "Implement secure user authentication with multi-factor authentication support",
                "priority_id": priority_map.get("High", 1),
                "status_id": status_map.get("In Progress", 1),
                "business_value": "Critical for security and user management",
                "user_story": "As a user, I want to securely log in to the system so that my data is protected",
                "acceptance_criteria": "User can log in with email/password, MFA is supported, session management works",
                "complexity": "High",
                "effort_estimate": Decimal("40.0"),
                "target_quarter": "Q1 2025",
                "planned_start_date": date(2025, 1, 15),
                "planned_end_date": date(2025, 3, 15),
                "is_active": True,
                "created_at": datetime.now(),
                "created_by": "System Admin"
            },
            {
                "backlog_id": "BL-002",
                "name": "Dashboard Analytics",
                "description": "Create comprehensive analytics dashboard with real-time data visualization",
                "priority_id": priority_map.get("Critical", 1),
                "status_id": status_map.get("Not Started", 1),
                "business_value": "Provides key insights for decision making",
                "user_story": "As a manager, I want to see real-time analytics so that I can make informed decisions",
                "acceptance_criteria": "Dashboard loads in under 2 seconds, shows real-time data, supports filtering",
                "complexity": "Medium",
                "effort_estimate": Decimal("25.0"),
                "target_quarter": "Q1 2025",
                "planned_start_date": date(2025, 2, 1),
                "planned_end_date": date(2025, 4, 1),
                "is_active": True,
                "created_at": datetime.now(),
                "created_by": "Product Manager"
            },
            {
                "backlog_id": "BL-003",
                "name": "Mobile App Development",
                "description": "Develop native mobile application for iOS and Android platforms",
                "priority_id": priority_map.get("High", 1),
                "status_id": status_map.get("Planning", 1),
                "business_value": "Expands user accessibility and engagement",
                "user_story": "As a mobile user, I want to access the system from my phone so that I can work on the go",
                "acceptance_criteria": "App works on iOS and Android, offline functionality, push notifications",
                "complexity": "High",
                "effort_estimate": Decimal("80.0"),
                "target_quarter": "Q2 2025",
                "planned_start_date": date(2025, 4, 1),
                "planned_end_date": date(2025, 8, 1),
                "is_active": True,
                "created_at": datetime.now(),
                "created_by": "Mobile Team Lead"
            },
            {
                "backlog_id": "BL-004",
                "name": "API Rate Limiting",
                "description": "Implement rate limiting for API endpoints to prevent abuse",
                "priority_id": priority_map.get("Medium", 1),
                "status_id": status_map.get("Completed", 1),
                "business_value": "Protects system resources and ensures fair usage",
                "user_story": "As a system administrator, I want rate limiting so that the API is protected from abuse",
                "acceptance_criteria": "Rate limits are configurable, different limits for different endpoints, proper error responses",
                "complexity": "Medium",
                "effort_estimate": Decimal("15.0"),
                "target_quarter": "Q4 2024",
                "planned_start_date": date(2024, 10, 1),
                "planned_end_date": date(2024, 11, 15),
                "is_active": True,
                "created_at": datetime.now(),
                "created_by": "Backend Developer"
            },
            {
                "backlog_id": "BL-005",
                "name": "Data Export Functionality",
                "description": "Add ability to export data in multiple formats (CSV, Excel, PDF)",
                "priority_id": priority_map.get("Medium", 1),
                "status_id": status_map.get("In Progress", 1),
                "business_value": "Enables data portability and reporting",
                "user_story": "As a user, I want to export my data so that I can use it in other tools",
                "acceptance_criteria": "Export to CSV, Excel, and PDF formats, large data sets handled efficiently",
                "complexity": "Medium",
                "effort_estimate": Decimal("20.0"),
                "target_quarter": "Q1 2025",
                "planned_start_date": date(2025, 1, 1),
                "planned_end_date": date(2025, 2, 28),
                "is_active": True,
                "created_at": datetime.now(),
                "created_by": "Data Engineer"
            },
            {
                "backlog_id": "BL-006",
                "name": "Notification System",
                "description": "Implement real-time notification system with email and in-app notifications",
                "priority_id": priority_map.get("High", 1),
                "status_id": status_map.get("Not Started", 1),
                "business_value": "Improves user engagement and communication",
                "user_story": "As a user, I want to receive notifications so that I stay informed about important updates",
                "acceptance_criteria": "Real-time notifications, email notifications, notification preferences",
                "complexity": "Medium",
                "effort_estimate": Decimal("30.0"),
                "target_quarter": "Q2 2025",
                "planned_start_date": date(2025, 3, 1),
                "planned_end_date": date(2025, 5, 1),
                "is_active": True,
                "created_at": datetime.now(),
                "created_by": "Frontend Developer"
            },
            {
                "backlog_id": "BL-007",
                "name": "Search Functionality",
                "description": "Implement advanced search with filters and full-text search",
                "priority_id": priority_map.get("Medium", 1),
                "status_id": status_map.get("Planning", 1),
                "business_value": "Improves data discoverability and user experience",
                "user_story": "As a user, I want to search for information so that I can find what I need quickly",
                "acceptance_criteria": "Full-text search, advanced filters, search suggestions, search history",
                "complexity": "High",
                "effort_estimate": Decimal("35.0"),
                "target_quarter": "Q2 2025",
                "planned_start_date": date(2025, 4, 15),
                "planned_end_date": date(2025, 6, 15),
                "is_active": True,
                "created_at": datetime.now(),
                "created_by": "Search Engineer"
            },
            {
                "backlog_id": "BL-008",
                "name": "Performance Optimization",
                "description": "Optimize database queries and improve application performance",
                "priority_id": priority_map.get("Critical", 1),
                "status_id": status_map.get("In Progress", 1),
                "business_value": "Improves user experience and system scalability",
                "user_story": "As a user, I want the system to be fast so that I can work efficiently",
                "acceptance_criteria": "Page load times under 2 seconds, database queries optimized, caching implemented",
                "complexity": "High",
                "effort_estimate": Decimal("45.0"),
                "target_quarter": "Q1 2025",
                "planned_start_date": date(2025, 1, 1),
                "planned_end_date": date(2025, 3, 31),
                "is_active": True,
                "created_at": datetime.now(),
                "created_by": "Performance Engineer"
            },
            {
                "backlog_id": "BL-009",
                "name": "User Role Management",
                "description": "Implement role-based access control with granular permissions",
                "priority_id": priority_map.get("High", 1),
                "status_id": status_map.get("Not Started", 1),
                "business_value": "Ensures proper access control and security",
                "user_story": "As an administrator, I want to manage user roles so that access is properly controlled",
                "acceptance_criteria": "Role creation, permission assignment, role inheritance, audit trail",
                "complexity": "Medium",
                "effort_estimate": Decimal("25.0"),
                "target_quarter": "Q1 2025",
                "planned_start_date": date(2025, 2, 15),
                "planned_end_date": date(2025, 4, 15),
                "is_active": True,
                "created_at": datetime.now(),
                "created_by": "Security Engineer"
            },
            {
                "backlog_id": "BL-010",
                "name": "Integration with External APIs",
                "description": "Integrate with third-party services and external APIs",
                "priority_id": priority_map.get("Medium", 1),
                "status_id": status_map.get("Completed", 1),
                "business_value": "Extends functionality and improves interoperability",
                "user_story": "As a user, I want to integrate with external services so that I can use additional features",
                "acceptance_criteria": "API integration working, error handling, rate limiting, documentation",
                "complexity": "Medium",
                "effort_estimate": Decimal("20.0"),
                "target_quarter": "Q4 2024",
                "planned_start_date": date(2024, 11, 1),
                "planned_end_date": date(2024, 12, 15),
                "is_active": True,
                "created_at": datetime.now(),
                "created_by": "Integration Specialist"
            }
        ]
        
        # Insert backlog items
        created_count = 0
        for item_data in backlog_items:
            # Check if item already exists
            existing = db.query(Backlog).filter(Backlog.backlog_id == item_data["backlog_id"]).first()
            if existing:
                print(f"⚠️  Backlog item {item_data['backlog_id']} already exists, skipping...")
                continue
                
            backlog_item = Backlog(**item_data)
            db.add(backlog_item)
            created_count += 1
        
        # Commit the changes
        db.commit()
        print(f"✅ Successfully created {created_count} backlog items")
        
        # Display created items
        print("\n📋 Created backlog items:")
        for item_data in backlog_items[:created_count]:
            print(f"  - {item_data['backlog_id']}: {item_data['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating backlog data: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🌱 Seeding backlog data...")
    success = create_backlog_data()
    if success:
        print("✅ Backlog data seeding completed successfully!")
    else:
        print("❌ Backlog data seeding failed!")
        sys.exit(1)
