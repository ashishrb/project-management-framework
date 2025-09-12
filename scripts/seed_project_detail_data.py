#!/usr/bin/env python3
"""
Seed Project Detail Management Data
Populates lookup tables for comprehensive project detail system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import get_db
from app.models.project_detail_lookups import (
    DemandCategory, ModernizationDomain, DigitizationCategory,
    DeliveryOrganization, ExpenseType, BusinessProcess,
    GenerativeAIImpact, ProjectPhase, ProjectState,
    NISTDomain, NISTMapping
)
from datetime import datetime

def seed_project_detail_lookups():
    """Seed all project detail lookup tables"""
    db = next(get_db())
    
    try:
        # Demand Categories
        demand_categories = [
            {"name": "Transform", "description": "Transformational initiatives"},
            {"name": "Enhance", "description": "Enhancement initiatives"},
            {"name": "Maintain", "description": "Maintenance initiatives"},
            {"name": "Optimize", "description": "Optimization initiatives"},
        ]
        
        for category in demand_categories:
            if not db.query(DemandCategory).filter(DemandCategory.name == category["name"]).first():
                db.add(DemandCategory(
                    name=category["name"],
                    description=category["description"],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ))
        
        # Modernization Domains
        modernization_domains = [
            {"name": "Cloud Migration", "description": "Cloud migration initiatives"},
            {"name": "Digital Transformation", "description": "Digital transformation projects"},
            {"name": "Legacy Modernization", "description": "Legacy system modernization"},
            {"name": "API Modernization", "description": "API modernization projects"},
            {"name": "Data Modernization", "description": "Data platform modernization"},
            {"name": "Security Modernization", "description": "Security infrastructure modernization"},
        ]
        
        for domain in modernization_domains:
            if not db.query(ModernizationDomain).filter(ModernizationDomain.name == domain["name"]).first():
                db.add(ModernizationDomain(
                    name=domain["name"],
                    description=domain["description"],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ))
        
        # Digitization Categories
        digitization_categories = [
            {"name": "Process Digitization", "description": "Business process digitization"},
            {"name": "Document Digitization", "description": "Document management digitization"},
            {"name": "Workflow Digitization", "description": "Workflow automation"},
            {"name": "Customer Experience", "description": "Customer experience digitization"},
            {"name": "Operations Digitization", "description": "Operations digitization"},
        ]
        
        for category in digitization_categories:
            if not db.query(DigitizationCategory).filter(DigitizationCategory.name == category["name"]).first():
                db.add(DigitizationCategory(
                    name=category["name"],
                    description=category["description"],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ))
        
        # Delivery Organizations
        delivery_organizations = [
            {"name": "IT Delivery", "level": 1, "description": "IT Delivery Organization"},
            {"name": "Business Delivery", "level": 1, "description": "Business Delivery Organization"},
            {"name": "Enterprise Architecture", "level": 2, "parent_id": 1, "description": "EA Team"},
            {"name": "Application Development", "level": 2, "parent_id": 1, "description": "App Dev Team"},
            {"name": "Infrastructure", "level": 2, "parent_id": 1, "description": "Infrastructure Team"},
            {"name": "Security", "level": 2, "parent_id": 1, "description": "Security Team"},
        ]
        
        for org in delivery_organizations:
            if not db.query(DeliveryOrganization).filter(DeliveryOrganization.name == org["name"]).first():
                db.add(DeliveryOrganization(
                    name=org["name"],
                    level=org["level"],
                    parent_id=org.get("parent_id"),
                    description=org["description"],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ))
        
        # Expense Types
        expense_types = [
            {"name": "Capital Expenditure", "code": "CAPEX", "description": "Capital expenditure"},
            {"name": "Operational Expenditure", "code": "OPEX", "description": "Operational expenditure"},
            {"name": "Work Item", "code": "WI", "description": "Work item expense"},
            {"name": "Contractor", "code": "CONTRACT", "description": "Contractor expense"},
            {"name": "Software License", "code": "LICENSE", "description": "Software license expense"},
        ]
        
        for expense in expense_types:
            if not db.query(ExpenseType).filter(ExpenseType.code == expense["code"]).first():
                db.add(ExpenseType(
                    name=expense["name"],
                    code=expense["code"],
                    description=expense["description"],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ))
        
        # Business Processes
        business_processes = [
            {"name": "Order to Cash", "category": "Sales", "description": "Order to cash process"},
            {"name": "Procure to Pay", "category": "Procurement", "description": "Procure to pay process"},
            {"name": "Hire to Retire", "category": "HR", "description": "Employee lifecycle process"},
            {"name": "Lead to Opportunity", "category": "Sales", "description": "Lead management process"},
            {"name": "Plan to Produce", "category": "Manufacturing", "description": "Production planning process"},
            {"name": "Request to Resolution", "category": "IT", "description": "IT service request process"},
        ]
        
        for process in business_processes:
            if not db.query(BusinessProcess).filter(BusinessProcess.name == process["name"]).first():
                db.add(BusinessProcess(
                    name=process["name"],
                    category=process["category"],
                    description=process["description"],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ))
        
        # Generative AI Impact
        ai_impacts = [
            {"name": "No Impact", "impact_level": 1, "description": "No generative AI impact"},
            {"name": "Low Impact", "impact_level": 2, "description": "Low generative AI impact"},
            {"name": "Medium Impact", "impact_level": 3, "description": "Medium generative AI impact"},
            {"name": "High Impact", "impact_level": 4, "description": "High generative AI impact"},
            {"name": "Critical Impact", "impact_level": 5, "description": "Critical generative AI impact"},
        ]
        
        for impact in ai_impacts:
            if not db.query(GenerativeAIImpact).filter(GenerativeAIImpact.name == impact["name"]).first():
                db.add(GenerativeAIImpact(
                    name=impact["name"],
                    impact_level=impact["impact_level"],
                    description=impact["description"],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ))
        
        # Project Phases
        project_phases = [
            {"name": "Initiation", "phase_order": 1, "color_code": "#3498db", "description": "Project initiation phase"},
            {"name": "Planning", "phase_order": 2, "color_code": "#f39c12", "description": "Project planning phase"},
            {"name": "Execution", "phase_order": 3, "color_code": "#27ae60", "description": "Project execution phase"},
            {"name": "Closure", "phase_order": 4, "color_code": "#95a5a6", "description": "Project closure phase"},
        ]
        
        for phase in project_phases:
            if not db.query(ProjectPhase).filter(ProjectPhase.name == phase["name"]).first():
                db.add(ProjectPhase(
                    name=phase["name"],
                    phase_order=phase["phase_order"],
                    color_code=phase["color_code"],
                    description=phase["description"],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ))
        
        # Project States
        project_states = [
            {"name": "Active", "color_code": "#27ae60", "description": "Project is active"},
            {"name": "Inactive", "color_code": "#95a5a6", "description": "Project is inactive"},
            {"name": "Suspended", "color_code": "#f39c12", "description": "Project is suspended"},
            {"name": "Cancelled", "color_code": "#e74c3c", "description": "Project is cancelled"},
        ]
        
        for state in project_states:
            if not db.query(ProjectState).filter(ProjectState.name == state["name"]).first():
                db.add(ProjectState(
                    name=state["name"],
                    color_code=state["color_code"],
                    description=state["description"],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ))
        
        # NIST Domains
        nist_domains = [
            {"name": "Identify", "domain_code": "ID", "description": "NIST Identify domain"},
            {"name": "Protect", "domain_code": "PR", "description": "NIST Protect domain"},
            {"name": "Detect", "domain_code": "DE", "description": "NIST Detect domain"},
            {"name": "Respond", "domain_code": "RS", "description": "NIST Respond domain"},
            {"name": "Recover", "domain_code": "RC", "description": "NIST Recover domain"},
        ]
        
        for domain in nist_domains:
            if not db.query(NISTDomain).filter(NISTDomain.domain_code == domain["domain_code"]).first():
                db.add(NISTDomain(
                    name=domain["name"],
                    domain_code=domain["domain_code"],
                    description=domain["description"],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ))
        
        # NIST Mappings
        nist_mappings = [
            {"name": "Asset Management", "mapping_code": "ID.AM", "description": "Asset management mapping"},
            {"name": "Business Environment", "mapping_code": "ID.BE", "description": "Business environment mapping"},
            {"name": "Governance", "mapping_code": "ID.GV", "description": "Governance mapping"},
            {"name": "Risk Assessment", "mapping_code": "ID.RA", "description": "Risk assessment mapping"},
            {"name": "Risk Management", "mapping_code": "ID.RM", "description": "Risk management mapping"},
        ]
        
        for mapping in nist_mappings:
            if not db.query(NISTMapping).filter(NISTMapping.mapping_code == mapping["mapping_code"]).first():
                db.add(NISTMapping(
                    name=mapping["name"],
                    mapping_code=mapping["mapping_code"],
                    description=mapping["description"],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ))
        
        db.commit()
        print("✅ Project detail lookup tables seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding project detail lookup tables: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_project_detail_lookups()
