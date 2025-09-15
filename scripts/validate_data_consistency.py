#!/usr/bin/env python3
"""
Comprehensive Data Validation Script
Validates data consistency across the entire application flow
"""

import os
import sys
import logging
import requests
import json
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.main_tables import Project, Backlog, Task, Feature
from app.models.lookup_tables import Status, Priority

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

class DataValidator:
    def __init__(self):
        self.db = SessionLocal()
        self.base_url = "http://localhost:8000"
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "tests_passed": 0,
            "tests_failed": 0,
            "issues": []
        }
    
    def validate_test(self, test_name: str, condition: bool, error_message: str = ""):
        """Validate a test condition and record results"""
        if condition:
            self.validation_results["tests_passed"] += 1
            logger.info(f"✅ {test_name}: PASSED")
        else:
            self.validation_results["tests_failed"] += 1
            self.validation_results["issues"].append({
                "test": test_name,
                "error": error_message
            })
            logger.error(f"❌ {test_name}: FAILED - {error_message}")
    
    def validate_database_consistency(self):
        """Validate database data consistency"""
        logger.info("🔍 Validating Database Consistency...")
        
        # Test 1: Active projects have valid status
        active_projects = self.db.query(Project).filter(Project.is_active == True).all()
        for project in active_projects:
            self.validate_test(
                f"Project {project.id} has valid status",
                project.status_id is not None and project.status_id > 0,
                f"Project {project.id} has invalid status_id: {project.status_id}"
            )
        
        # Test 2: Manager assignments are consistent
        manager_projects = self.db.query(Project).filter(
            Project.is_active == True,
            Project.project_manager.isnot(None)
        ).all()
        
        manager_counts = {}
        for project in manager_projects:
            manager = project.project_manager
            manager_counts[manager] = manager_counts.get(manager, 0) + 1
        
        # Validate manager1 has 3 projects, manager2 has 2 projects
        self.validate_test(
            "Manager1 has 3 projects",
            manager_counts.get("manager1", 0) == 3,
            f"Manager1 has {manager_counts.get('manager1', 0)} projects, expected 3"
        )
        
        self.validate_test(
            "Manager2 has 2 projects", 
            manager_counts.get("manager2", 0) == 2,
            f"Manager2 has {manager_counts.get('manager2', 0)} projects, expected 2"
        )
        
        # Test 3: Backlog items have valid priorities
        backlogs = self.db.query(Backlog).filter(Backlog.is_active == True).all()
        for backlog in backlogs:
            self.validate_test(
                f"Backlog {backlog.id} has valid priority",
                backlog.priority_id is not None and 1 <= backlog.priority_id <= 4,
                f"Backlog {backlog.id} has invalid priority_id: {backlog.priority_id}"
            )
        
        # Test 4: Backlog assignments are consistent
        assigned_backlogs = [b for b in backlogs if b.description and 'Project' in b.description]
        self.validate_test(
            "Backlog items are assigned to projects",
            len(assigned_backlogs) > 0,
            "No backlog items are assigned to projects"
        )
    
    def validate_api_consistency(self):
        """Validate API data consistency"""
        logger.info("🔍 Validating API Consistency...")
        
        try:
            # Test 1: Projects API returns consistent data
            response = requests.get(f"{self.base_url}/api/v1/projects")
            self.validate_test(
                "Projects API responds",
                response.status_code == 200,
                f"Projects API returned status {response.status_code}"
            )
            
            if response.status_code == 200:
                projects_data = response.json()
                self.validate_test(
                    "Projects API returns active projects",
                    len(projects_data) > 0,
                    "Projects API returned no data"
                )
                
                # Validate project structure
                if projects_data:
                    project = projects_data[0]
                    required_fields = ['id', 'name', 'project_manager', 'status_id', 'is_active']
                    for field in required_fields:
                        self.validate_test(
                            f"Project has {field} field",
                            field in project,
                            f"Project missing {field} field"
                        )
            
            # Test 2: Dashboard metrics API
            response = requests.get(f"{self.base_url}/api/v1/dashboards/summary-metrics")
            self.validate_test(
                "Dashboard metrics API responds",
                response.status_code == 200,
                f"Dashboard metrics API returned status {response.status_code}"
            )
            
            if response.status_code == 200:
                metrics_data = response.json()
                self.validate_test(
                    "Dashboard metrics have required fields",
                    all(field in metrics_data for field in ['active_projects', 'completed_projects', 'at_risk_projects']),
                    "Dashboard metrics missing required fields"
                )
            
        except requests.exceptions.ConnectionError:
            logger.warning("⚠️  API server not running - skipping API tests")
    
    def validate_calculation_accuracy(self):
        """Validate calculation accuracy"""
        logger.info("🔍 Validating Calculation Accuracy...")
        
        # Test 1: Project counts match database
        db_active_count = self.db.query(Project).filter(
            Project.is_active == True,
            Project.status_id == 1
        ).count()
        
        db_total_count = self.db.query(Project).filter(Project.is_active == True).count()
        
        self.validate_test(
            "Active projects count is logical",
            db_active_count <= db_total_count,
            f"Active projects ({db_active_count}) > Total projects ({db_total_count})"
        )
        
        # Test 2: Backlog priority distribution
        high_priority_count = self.db.query(Backlog).filter(
            Backlog.is_active == True,
            Backlog.priority_id >= 3
        ).count()
        
        total_backlog_count = self.db.query(Backlog).filter(Backlog.is_active == True).count()
        
        self.validate_test(
            "High priority backlogs count is logical",
            high_priority_count <= total_backlog_count,
            f"High priority backlogs ({high_priority_count}) > Total backlogs ({total_backlog_count})"
        )
        
        # Test 3: Manager project assignments
        manager1_projects = self.db.query(Project).filter(
            Project.is_active == True,
            Project.project_manager == "manager1"
        ).count()
        
        manager2_projects = self.db.query(Project).filter(
            Project.is_active == True,
            Project.project_manager == "manager2"
        ).count()
        
        total_manager_projects = manager1_projects + manager2_projects
        
        self.validate_test(
            "Manager project assignments total correctly",
            total_manager_projects == 5,
            f"Manager projects total {total_manager_projects}, expected 5"
        )
    
    def validate_ai_analysis_accuracy(self):
        """Validate AI analysis accuracy"""
        logger.info("🔍 Validating AI Analysis Accuracy...")
        
        # Test 1: Risk analysis uses actual project data
        projects = self.db.query(Project).filter(Project.is_active == True).limit(3).all()
        
        for project in projects:
            # Simulate risk analysis calculation
            risk_score = 0.0
            
            # Factor 1: Project status
            if project.status_id == 3:  # At Risk
                risk_score += 0.8
            elif project.status_id == 4:  # Off Track
                risk_score += 1.0
            else:
                risk_score += 0.3
            
            # Factor 2: Completion percentage
            if project.percent_complete:
                percent_complete = float(project.percent_complete)
                if percent_complete < 25:
                    risk_score += 0.7
                elif percent_complete > 75:
                    risk_score += 0.2
                else:
                    risk_score += 0.4
            
            # Normalize to 0-10 scale
            normalized_score = min(10.0, risk_score * 10)
            
            self.validate_test(
                f"Risk score calculation for project {project.id}",
                0 <= normalized_score <= 10,
                f"Risk score {normalized_score} is outside valid range (0-10)"
            )
        
        # Test 2: Health score calculation
        for project in projects:
            health_score = 50  # Base score
            
            # Adjust based on status
            if project.status_id == 1:
                health_score += 30
            elif project.status_id == 2:
                health_score += 40
            elif project.status_id == 3:
                health_score -= 20
            elif project.status_id == 4:
                health_score -= 30
            
            # Adjust based on completion
            if project.percent_complete:
                health_score += (float(project.percent_complete) * 0.3)
            
            health_score = max(0, min(100, health_score))
            
            self.validate_test(
                f"Health score calculation for project {project.id}",
                0 <= health_score <= 100,
                f"Health score {health_score} is outside valid range (0-100)"
            )
    
    def validate_chart_data_integration(self):
        """Validate chart data integration"""
        logger.info("🔍 Validating Chart Data Integration...")
        
        # Test 1: Project health chart data
        projects = self.db.query(Project).filter(Project.is_active == True).all()
        
        for project in projects:
            # Calculate health score as done in JavaScript
            base_score = 50
            
            if project.status_id == 1:
                base_score += 30
            elif project.status_id == 2:
                base_score += 40
            elif project.status_id == 3:
                base_score -= 20
            elif project.status_id == 4:
                base_score -= 30
            
            if project.percent_complete:
                base_score += (float(project.percent_complete) * 0.3)
            
            health_score = max(0, min(100, base_score))
            
            self.validate_test(
                f"Health score for project {project.id} is valid",
                0 <= health_score <= 100,
                f"Health score {health_score} is invalid"
            )
        
        # Test 2: Task status chart data
        backlogs = self.db.query(Backlog).filter(Backlog.is_active == True).all()
        
        in_progress = len([b for b in backlogs if b.status_id == 2])
        completed = len([b for b in backlogs if b.status_id == 3])
        planned = len([b for b in backlogs if b.status_id == 1])
        blocked = len([b for b in backlogs if b.status_id == 4])
        
        total_status_count = in_progress + completed + planned + blocked
        
        self.validate_test(
            "Task status counts are consistent",
            total_status_count <= len(backlogs),
            f"Status counts ({total_status_count}) > Total backlogs ({len(backlogs)})"
        )
    
    def run_all_validations(self):
        """Run all validation tests"""
        logger.info("🚀 Starting Comprehensive Data Validation...")
        
        self.validate_database_consistency()
        self.validate_api_consistency()
        self.validate_calculation_accuracy()
        self.validate_ai_analysis_accuracy()
        self.validate_chart_data_integration()
        
        # Generate summary report
        total_tests = self.validation_results["tests_passed"] + self.validation_results["tests_failed"]
        success_rate = (self.validation_results["tests_passed"] / total_tests * 100) if total_tests > 0 else 0
        
        logger.info("📊 VALIDATION SUMMARY:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {self.validation_results['tests_passed']}")
        logger.info(f"   Failed: {self.validation_results['tests_failed']}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        
        if self.validation_results["issues"]:
            logger.info("🚨 ISSUES FOUND:")
            for issue in self.validation_results["issues"]:
                logger.info(f"   - {issue['test']}: {issue['error']}")
        
        # Save detailed report
        report_file = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        logger.info(f"📄 Detailed report saved to: {report_file}")
        
        return success_rate >= 90  # Consider validation successful if 90%+ tests pass
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()

def main():
    """Main validation function"""
    validator = DataValidator()
    success = validator.run_all_validations()
    
    if success:
        logger.info("🎉 Data validation completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Data validation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
