"""
Seed lookup data for GenAI Metrics Dashboard
Based on PROJECT_FLOW_DIAGRAM.md specifications
"""
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from app.database import engine, Base
from app.models.lookup_tables import *

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def seed_functions():
    """Seed 17 functions as specified in the project flow diagram"""
    functions = [
        "Human Resources", "Finance", "Technology", "Operations", "Marketing",
        "Sales", "Customer Service", "Legal", "Compliance", "Security",
        "Data Management", "Analytics", "Research & Development", "Quality Assurance",
        "Procurement", "Facilities", "Training & Development"
    ]
    
    for name in functions:
        function = Function(
            name=name,
            description=f"{name} function for enterprise operations",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(function)
    
    print(f"✅ Seeded {len(functions)} functions")

def seed_platforms():
    """Seed 9 platforms as specified in the project flow diagram"""
    platforms = [
        "LC Platform", "Commercial", "Custom", "Cloud", "On-Premise",
        "Hybrid", "Mobile", "Web", "API"
    ]
    
    for name in platforms:
        platform = Platform(
            name=name,
            description=f"{name} platform for enterprise applications",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(platform)
    
    print(f"✅ Seeded {len(platforms)} platforms")

def seed_priorities():
    """Seed 6 priority levels as specified in the project flow diagram"""
    priorities = [
        {"name": "Critical", "level": 0, "color_code": "#FF0000"},
        {"name": "High", "level": 1, "color_code": "#FFA500"},
        {"name": "Medium", "level": 2, "color_code": "#FFFF00"},
        {"name": "Low", "level": 3, "color_code": "#00FF00"},
        {"name": "Nice to Have", "level": 4, "color_code": "#00BFFF"},
        {"name": "Future", "level": 5, "color_code": "#808080"}
    ]
    
    for priority_data in priorities:
        priority = Priority(
            name=priority_data["name"],
            level=priority_data["level"],
            description=f"{priority_data['name']} priority level",
            color_code=priority_data["color_code"],
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(priority)
    
    print(f"✅ Seeded {len(priorities)} priorities")

def seed_statuses():
    """Seed 4 status types as specified in the project flow diagram"""
    statuses = [
        {"name": "Active", "color_code": "#00FF00"},
        {"name": "Completed", "color_code": "#008000"},
        {"name": "At Risk", "color_code": "#FFA500"},
        {"name": "Off Track", "color_code": "#FF0000"}
    ]
    
    for status_data in statuses:
        status = Status(
            name=status_data["name"],
            description=f"{status_data['name']} status",
            color_code=status_data["color_code"],
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(status)
    
    print(f"✅ Seeded {len(statuses)} statuses")

def seed_portfolios():
    """Seed portfolios with L1/L2 hierarchy as specified in the project flow diagram"""
    portfolios = [
        {"name": "Human Resources", "level": 1, "parent_id": None},
        {"name": "Corporate Services", "level": 1, "parent_id": None},
        {"name": "Health Sciences", "level": 1, "parent_id": None},
        {"name": "Technology", "level": 1, "parent_id": None},
        {"name": "Finance", "level": 1, "parent_id": None},
        {"name": "HR Payroll", "level": 2, "parent_id": 1},
        {"name": "HR Talent Management", "level": 2, "parent_id": 1},
        {"name": "HR Benefits", "level": 2, "parent_id": 1},
        {"name": "Corporate IT", "level": 2, "parent_id": 2},
        {"name": "Corporate Security", "level": 2, "parent_id": 2}
    ]
    
    for portfolio_data in portfolios:
        portfolio = Portfolio(
            name=portfolio_data["name"],
            level=portfolio_data["level"],
            parent_id=portfolio_data["parent_id"],
            description=f"{portfolio_data['name']} portfolio",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(portfolio)
    
    print(f"✅ Seeded {len(portfolios)} portfolios")

def seed_applications():
    """Seed applications with SOX/Non-SOX classification"""
    applications = [
        {"name": "ServiceNow", "sox_classification": "SOX"},
        {"name": "TruTime", "sox_classification": "SOX"},
        {"name": "GoPerform", "sox_classification": "SOX"},
        {"name": "Connect Me", "sox_classification": "Non-SOX"},
        {"name": "MyCareer", "sox_classification": "Non-SOX"},
        {"name": "Payroll System", "sox_classification": "SOX"},
        {"name": "HR Portal", "sox_classification": "Non-SOX"},
        {"name": "Procurement System", "sox_classification": "SOX"}
    ]
    
    for app_data in applications:
        application = Application(
            name=app_data["name"],
            sox_classification=app_data["sox_classification"],
            description=f"{app_data['name']} application",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(application)
    
    print(f"✅ Seeded {len(applications)} applications")

def seed_investment_types():
    """Seed investment types as specified in the project flow diagram"""
    investment_types = [
        "Transform", "Enhance", "Maintain", "Innovate", "Compliance"
    ]
    
    for name in investment_types:
        investment_type = InvestmentType(
            name=name,
            description=f"{name} investment type",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(investment_type)
    
    print(f"✅ Seeded {len(investment_types)} investment types")

def seed_journey_maps():
    """Seed journey maps"""
    journey_maps = [
        "Employee Onboarding", "Customer Journey", "Vendor Management",
        "Project Lifecycle", "Risk Management", "Compliance Process"
    ]
    
    for name in journey_maps:
        journey_map = JourneyMap(
            name=name,
            description=f"{name} journey map",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(journey_map)
    
    print(f"✅ Seeded {len(journey_maps)} journey maps")

def seed_project_types():
    """Seed 4 project types as specified in the project flow diagram"""
    project_types = [
        "Development", "Enhancement", "Maintenance", "Migration"
    ]
    
    for name in project_types:
        project_type = ProjectType(
            name=name,
            description=f"{name} project type",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(project_type)
    
    print(f"✅ Seeded {len(project_types)} project types")

def seed_project_classifications():
    """Seed project classifications"""
    # Project Status Classifications
    status_classifications = [
        "Execution", "Planning", "Review", "On Hold", "Cancelled"
    ]
    
    for name in status_classifications:
        status_class = ProjectStatusClassification(
            name=name,
            description=f"{name} status classification",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(status_class)
    
    # Project Priority Classifications
    priority_classifications = [
        "P0 - Critical", "P1 - High", "P2 - Medium", "P3 - Low", "P4 - Future"
    ]
    
    for name in priority_classifications:
        priority_class = ProjectPriorityClassification(
            name=name,
            description=f"{name} priority classification",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(priority_class)
    
    print(f"✅ Seeded {len(status_classifications)} status classifications and {len(priority_classifications)} priority classifications")

def seed_project_criticality_levels():
    """Seed project criticality levels as specified in the project flow diagram"""
    criticality_levels = [
        {"name": "Critical (P0)", "level": 0, "color_code": "#FF0000"},
        {"name": "High (P1)", "level": 1, "color_code": "#FFA500"},
        {"name": "Medium (P2)", "level": 2, "color_code": "#FFFF00"},
        {"name": "Low (P3)", "level": 3, "color_code": "#00FF00"},
        {"name": "Future (P4)", "level": 4, "color_code": "#808080"}
    ]
    
    for criticality_data in criticality_levels:
        criticality = ProjectCriticalityLevel(
            name=criticality_data["name"],
            level=criticality_data["level"],
            description=f"{criticality_data['name']} criticality level",
            color_code=criticality_data["color_code"],
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(criticality)
    
    print(f"✅ Seeded {len(criticality_levels)} criticality levels")

def main():
    """Main function to seed all lookup data"""
    print("🌱 Starting to seed lookup data for GenAI Metrics Dashboard...")
    
    try:
        # Seed all lookup tables
        seed_functions()
        seed_platforms()
        seed_priorities()
        seed_statuses()
        seed_portfolios()
        seed_applications()
        seed_investment_types()
        seed_journey_maps()
        seed_project_types()
        seed_project_classifications()
        seed_project_criticality_levels()
        
        # Commit all changes
        db.commit()
        print("✅ All lookup data seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
