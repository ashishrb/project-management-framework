#!/usr/bin/env python3
"""
Demo Data Generation Script for GenAI Metrics Dashboard
Generates comprehensive test data including 270+ features, 216+ backlogs, and realistic project management data
"""

import os
import sys
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from faker import Faker

from app.database import SessionLocal, engine
from app.models.main_tables import Project, Feature, Backlog, Resource, Task, Risk, Approval, Charter
from app.models.lookup_tables import (
    Function, Platform, Priority, Status, ProjectType, Portfolio, 
    InvestmentType, ProjectCriticalityLevel
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Faker
fake = Faker()

class DemoDataGenerator:
    """Main class for generating demo data"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.fake = fake
        self.generated_data = {
            'projects': [],
            'features': [],
            'backlogs': [],
            'resources': [],
            'tasks': [],
            'risks': [],
            'approvals': [],
            'charters': []
        }
        
        # Get lookup data
        self.lookup_data = self._get_lookup_data()
        
    def _get_lookup_data(self) -> Dict[str, List]:
        """Get all lookup table data"""
        return {
            'functions': self.db.query(Function).filter(Function.is_active == True).all(),
            'platforms': self.db.query(Platform).filter(Platform.is_active == True).all(),
            'priorities': self.db.query(Priority).filter(Priority.is_active == True).all(),
            'statuses': self.db.query(Status).filter(Status.is_active == True).all(),
            'project_types': self.db.query(ProjectType).filter(ProjectType.is_active == True).all(),
            'portfolios': self.db.query(Portfolio).filter(Portfolio.is_active == True).all(),
            'investment_types': self.db.query(InvestmentType).filter(InvestmentType.is_active == True).all(),
            'criticality_levels': self.db.query(ProjectCriticalityLevel).filter(ProjectCriticalityLevel.is_active == True).all()
        }
    
    def generate_projects(self, count: int = 50) -> List[Project]:
        """Generate realistic projects"""
        logger.info(f"Generating {count} projects...")
        
        projects = []
        project_templates = [
            {
                'name_prefix': 'AI-Powered',
                'description_template': 'AI-driven {type} solution for {industry}',
                'domains': ['Machine Learning', 'Natural Language Processing', 'Computer Vision']
            },
            {
                'name_prefix': 'Cloud-Native',
                'description_template': 'Cloud-native {type} platform for {industry}',
                'domains': ['Cloud Infrastructure', 'Microservices', 'DevOps']
            },
            {
                'name_prefix': 'Data-Driven',
                'description_template': 'Data analytics {type} system for {industry}',
                'domains': ['Data Analytics', 'Business Intelligence', 'Data Visualization']
            },
            {
                'name_prefix': 'Mobile-First',
                'description_template': 'Mobile-first {type} application for {industry}',
                'domains': ['Mobile Development', 'User Experience', 'Cross-Platform']
            },
            {
                'name_prefix': 'Enterprise',
                'description_template': 'Enterprise {type} solution for {industry}',
                'domains': ['Enterprise Software', 'Integration', 'Security']
            }
        ]
        
        industries = ['Healthcare', 'Finance', 'E-commerce', 'Manufacturing', 'Education', 'Retail', 'Technology']
        project_types = ['Platform', 'Application', 'Service', 'System', 'Solution', 'Tool', 'Framework']
        
        for i in range(count):
            template = random.choice(project_templates)
            industry = random.choice(industries)
            project_type = random.choice(project_types)
            
            # Generate realistic dates
            start_date = self.fake.date_between(start_date='-2y', end_date='+6m')
            duration_days = random.randint(30, 365)
            due_date = start_date + timedelta(days=duration_days)
            
            # Generate budget
            budget_amount = random.randint(50000, 5000000)
            
            # Generate unique project ID using timestamp and counter
            timestamp = int(time.time() * 1000) % 100000  # Last 5 digits of timestamp
            project_id = f"PRJ-{timestamp:05d}{i:03d}"
            
            project = Project(
                project_id=project_id,
                esa_id=f"ESA-{self.fake.random_int(min=1000, max=9999)}",
                name=f"{template['name_prefix']} {project_type} - {industry}",
                description=template['description_template'].format(type=project_type, industry=industry),
                project_type_id=random.choice(self.lookup_data['project_types']).id,
                status_id=random.choice(self.lookup_data['statuses']).id,
                priority_id=random.choice(self.lookup_data['priorities']).id,
                criticality_id=random.choice(self.lookup_data['criticality_levels']).id,
                portfolio_id=random.choice(self.lookup_data['portfolios']).id,
                sub_portfolio=f"Sub-{self.fake.word().title()}",
                top_level_portfolio=f"Portfolio-{self.fake.word().title()}",
                investment_type_id=random.choice(self.lookup_data['investment_types']).id,
                modernization_domain=random.choice(template['domains']),
                digitization_category=random.choice(['Digital Transformation', 'Process Automation', 'Data Analytics']),
                budget_amount=budget_amount,
                funding_status=random.choice(['Approved', 'Pending', 'Secured']),
                budget_status=random.choice(['On Track', 'Over Budget', 'Under Budget']),
                start_date=start_date,
                due_date=due_date,
                actual_start_date=start_date if random.random() > 0.2 else None,
                actual_end_date=due_date if random.random() > 0.7 else None,
                percent_complete=random.randint(0, 100),
                project_manager=self.fake.name(),
                technology_portfolio_leader=self.fake.name(),
                business_owner=self.fake.name(),
                owner=self.fake.name(),
                is_active=True,
                created_at=self.fake.date_time_between(start_date='-1y', end_date='now'),
                updated_at=self.fake.date_time_between(start_date='-6m', end_date='now'),
                created_by=self.fake.name(),
                updated_by=self.fake.name()
            )
            
            projects.append(project)
            self.generated_data['projects'].append(project)
        
        # Bulk insert projects
        self.db.add_all(projects)
        self.db.commit()
        logger.info(f"Generated {len(projects)} projects")
        
        return projects
    
    def generate_resources(self, count: int = 100) -> List[Resource]:
        """Generate realistic resources"""
        logger.info(f"Generating {count} resources...")
        
        resources = []
        roles = ['Software Engineer', 'Data Scientist', 'Product Manager', 'UX Designer', 
                'DevOps Engineer', 'QA Engineer', 'Project Manager', 'Business Analyst',
                'AI/ML Engineer', 'Cloud Architect', 'Security Engineer', 'Technical Lead']
        
        skills = ['Python', 'JavaScript', 'React', 'Node.js', 'AWS', 'Azure', 'Docker', 
                 'Kubernetes', 'Machine Learning', 'Data Analytics', 'Agile', 'Scrum']
        
        for i in range(count):
            role = random.choice(roles)
            skill_list = random.sample(skills, random.randint(3, 8))
            
            resource = Resource(
                name=self.fake.name(),
                email=f"{self.fake.user_name()}{i}@example.com",
                role=role,
                skills=skill_list,  # Store as JSON array, not comma-separated string
                experience_level=random.choice(['Junior', 'Mid', 'Senior', 'Lead', 'Principal']),
                is_active=True,
                availability_percentage=random.randint(50, 100),
                created_at=self.fake.date_time_between(start_date='-1y', end_date='now'),
                updated_at=self.fake.date_time_between(start_date='-6m', end_date='now'),
                created_by=self.fake.name(),
                updated_by=self.fake.name()
            )
            
            resources.append(resource)
            self.generated_data['resources'].append(resource)
        
        # Bulk insert resources
        self.db.add_all(resources)
        self.db.commit()
        logger.info(f"Generated {len(resources)} resources")
        
        return resources
    
    def generate_features(self, count: int = 270) -> List[Feature]:
        """Generate realistic features"""
        logger.info(f"Generating {count} features...")
        
        features = []
        feature_templates = [
            {
                'name_prefix': 'User Authentication',
                'description_template': 'Implement {type} authentication system with {features}',
                'types': ['OAuth', 'SSO', 'Multi-factor', 'Biometric', 'Token-based']
            },
            {
                'name_prefix': 'Data Analytics',
                'description_template': 'Build {type} analytics dashboard with {features}',
                'types': ['Real-time', 'Predictive', 'Business Intelligence', 'Machine Learning', 'Statistical']
            },
            {
                'name_prefix': 'API Integration',
                'description_template': 'Develop {type} API integration for {features}',
                'types': ['REST', 'GraphQL', 'WebSocket', 'gRPC', 'Event-driven']
            },
            {
                'name_prefix': 'Mobile Features',
                'description_template': 'Create {type} mobile functionality with {features}',
                'types': ['Push Notifications', 'Offline Sync', 'Location Services', 'Camera Integration', 'Payment Processing']
            },
            {
                'name_prefix': 'AI/ML Capabilities',
                'description_template': 'Implement {type} AI/ML features including {features}',
                'types': ['Natural Language Processing', 'Computer Vision', 'Recommendation Engine', 'Predictive Analytics', 'Chatbot']
            }
        ]
        
        feature_details = ['real-time updates', 'data visualization', 'user management', 'security controls', 
                          'performance optimization', 'scalability features', 'monitoring capabilities']
        
        for i in range(count):
            template = random.choice(feature_templates)
            feature_type = random.choice(template['types'])
            feature_list = random.sample(feature_details, random.randint(2, 4))
            
            # Assign to a random project
            project = random.choice(self.generated_data['projects'])
            
            feature = Feature(
                project_id=project.id,
                feature_name=f"{template['name_prefix']} - {feature_type}",
                description=template['description_template'].format(type=feature_type, features=', '.join(feature_list)),
                status_id=random.choice(self.lookup_data['statuses']).id,
                priority_id=random.choice(self.lookup_data['priorities']).id,
                business_value=f"Business value: {random.choice(['Improved efficiency', 'Enhanced user experience', 'Cost reduction', 'Revenue generation', 'Risk mitigation'])}",
                acceptance_criteria=f"Acceptance criteria: {random.choice(['Functional requirements met', 'Performance targets achieved', 'User acceptance testing passed', 'Security requirements satisfied'])}",
                complexity=random.choice(['Low', 'Medium', 'High']),
                effort_estimate=random.randint(1, 20),
                percent_complete=random.randint(0, 100),
                is_active=True,
                created_at=self.fake.date_time_between(start_date='-1y', end_date='now'),
                updated_at=self.fake.date_time_between(start_date='-6m', end_date='now'),
                created_by=self.fake.name(),
                updated_by=self.fake.name()
            )
            
            features.append(feature)
            self.generated_data['features'].append(feature)
        
        # Bulk insert features
        self.db.add_all(features)
        self.db.commit()
        logger.info(f"Generated {len(features)} features")
        
        return features
    
    def generate_backlogs(self, count: int = 216) -> List[Backlog]:
        """Generate realistic backlog items"""
        logger.info(f"Generating {count} backlog items...")
        
        backlogs = []
        backlog_templates = [
            {
                'name_prefix': 'Bug Fix',
                'description_template': 'Fix {issue} in {component} affecting {impact}',
                'issues': ['memory leak', 'performance issue', 'UI glitch', 'data inconsistency', 'security vulnerability']
            },
            {
                'name_prefix': 'Enhancement',
                'description_template': 'Enhance {component} with {feature} to improve {benefit}',
                'issues': ['user experience', 'performance', 'scalability', 'maintainability', 'security']
            },
            {
                'name_prefix': 'New Feature',
                'description_template': 'Implement {feature} for {component} to enable {capability}',
                'issues': ['user management', 'data processing', 'reporting', 'integration', 'automation']
            },
            {
                'name_prefix': 'Technical Debt',
                'description_template': 'Refactor {component} to {improvement} and {benefit}',
                'issues': ['code quality', 'architecture', 'performance', 'maintainability', 'testability']
            }
        ]
        
        components = ['API', 'Database', 'Frontend', 'Backend', 'Mobile App', 'Dashboard', 'Authentication', 'Analytics']
        impacts = ['user experience', 'system performance', 'data integrity', 'security', 'scalability']
        benefits = ['better performance', 'improved usability', 'enhanced security', 'reduced maintenance', 'increased reliability']
        capabilities = ['better user experience', 'improved efficiency', 'enhanced functionality', 'better integration', 'automated processes']
        
        for i in range(count):
            template = random.choice(backlog_templates)
            issue = random.choice(template['issues'])
            component = random.choice(components)
            
            if 'Bug Fix' in template['name_prefix']:
                impact = random.choice(impacts)
                description = template['description_template'].format(issue=issue, component=component, impact=impact)
            elif 'Enhancement' in template['name_prefix']:
                feature = random.choice(['new functionality', 'improved interface', 'better performance', 'enhanced security'])
                benefit = random.choice(benefits)
                description = template['description_template'].format(component=component, feature=feature, benefit=benefit)
            elif 'New Feature' in template['name_prefix']:
                feature = random.choice(['user dashboard', 'data export', 'notification system', 'search functionality'])
                capability = random.choice(capabilities)
                description = template['description_template'].format(feature=feature, component=component, capability=capability)
            else:  # Technical Debt
                improvement = random.choice(['improve code structure', 'optimize performance', 'enhance security', 'increase maintainability'])
                benefit = random.choice(benefits)
                description = template['description_template'].format(component=component, improvement=improvement, benefit=benefit)
            
            # Assign to a random project
            project = random.choice(self.generated_data['projects'])
            
            # Generate unique backlog ID using timestamp and counter
            timestamp = int(time.time() * 1000) % 100000  # Last 5 digits of timestamp
            backlog_id = f"BLG-{timestamp:05d}{i:03d}"
            
            backlog = Backlog(
                backlog_id=backlog_id,
                name=f"{template['name_prefix']} - {component}",
                description=description,
                priority_id=random.choice(self.lookup_data['priorities']).id,
                status_id=random.choice(self.lookup_data['statuses']).id,
                business_value=f"Business value: {random.choice(['Improved efficiency', 'Enhanced user experience', 'Cost reduction', 'Revenue generation', 'Risk mitigation'])}",
                user_story=f"As a {random.choice(['user', 'admin', 'developer', 'stakeholder'])}, I want {random.choice(['better functionality', 'improved performance', 'enhanced security', 'easier access'])} so that I can {random.choice(['work more efficiently', 'achieve better results', 'reduce errors', 'save time'])}",
                acceptance_criteria=f"Acceptance criteria: {random.choice(['Functional requirements met', 'Performance targets achieved', 'User acceptance testing passed', 'Security requirements satisfied'])}",
                complexity=random.choice(['Low', 'Medium', 'High']),
                effort_estimate=random.randint(1, 15),
                target_quarter=random.choice(['Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025', 'Q1 2026']),
                is_active=True,
                created_at=self.fake.date_time_between(start_date='-1y', end_date='now'),
                updated_at=self.fake.date_time_between(start_date='-6m', end_date='now'),
                created_by=self.fake.name(),
                updated_by=self.fake.name()
            )
            
            backlogs.append(backlog)
            self.generated_data['backlogs'].append(backlog)
        
        # Bulk insert backlogs
        self.db.add_all(backlogs)
        self.db.commit()
        logger.info(f"Generated {len(backlogs)} backlog items")
        
        return backlogs
    
    def generate_tasks(self, count: int = 500) -> List[Task]:
        """Generate realistic tasks"""
        logger.info(f"Generating {count} tasks...")
        
        tasks = []
        task_templates = [
            'Design {component} architecture',
            'Implement {feature} functionality',
            'Write unit tests for {component}',
            'Create API documentation for {endpoint}',
            'Optimize {component} performance',
            'Fix {issue} in {component}',
            'Review and refactor {component} code',
            'Deploy {component} to {environment}',
            'Configure {service} integration',
            'Update {component} dependencies'
        ]
        
        components = ['API', 'Database', 'Frontend', 'Backend', 'Mobile App', 'Dashboard', 'Authentication', 'Analytics']
        features = ['user management', 'data processing', 'reporting', 'notifications', 'search', 'filtering']
        issues = ['bug', 'performance issue', 'security vulnerability', 'UI glitch', 'data inconsistency']
        endpoints = ['users', 'projects', 'reports', 'analytics', 'notifications', 'settings']
        services = ['database', 'cache', 'message queue', 'file storage', 'monitoring']
        environments = ['development', 'staging', 'production', 'testing']
        
        for i in range(count):
            template = random.choice(task_templates)
            component = random.choice(components)
            
            if '{feature}' in template:
                feature = random.choice(features)
                task_name = template.format(component=component, feature=feature)
            elif '{issue}' in template:
                issue = random.choice(issues)
                task_name = template.format(issue=issue, component=component)
            elif '{endpoint}' in template:
                endpoint = random.choice(endpoints)
                task_name = template.format(endpoint=endpoint, component=component)
            elif '{service}' in template:
                service = random.choice(services)
                task_name = template.format(service=service, component=component)
            elif '{environment}' in template:
                environment = random.choice(environments)
                task_name = template.format(component=component, environment=environment)
            else:
                task_name = template.format(component=component)
            
            # Assign to a random project
            project = random.choice(self.generated_data['projects'])
            
            # Generate realistic dates
            start_date = self.fake.date_between(start_date='-6m', end_date='+3m')
            duration_days = random.randint(1, 14)
            due_date = start_date + timedelta(days=duration_days)
            
            task = Task(
                project_id=project.id,
                task_name=task_name,
                description=f"Detailed description for {task_name}",
                status_id=random.choice(self.lookup_data['statuses']).id,
                priority_id=random.choice(self.lookup_data['priorities']).id,
                estimated_hours=random.randint(2, 40),
                actual_hours=random.randint(0, 50),
                start_date=start_date,
                due_date=due_date,
                percent_complete=random.randint(0, 100),
                is_active=True,
                created_at=self.fake.date_time_between(start_date='-1y', end_date='now'),
                updated_at=self.fake.date_time_between(start_date='-6m', end_date='now'),
                created_by=self.fake.name(),
                updated_by=self.fake.name()
            )
            
            tasks.append(task)
            self.generated_data['tasks'].append(task)
        
        # Bulk insert tasks
        self.db.add_all(tasks)
        self.db.commit()
        logger.info(f"Generated {len(tasks)} tasks")
        
        return tasks
    
    def generate_risks(self, count: int = 150) -> List[Risk]:
        """Generate realistic risks"""
        logger.info(f"Generating {count} risks...")
        
        risks = []
        risk_templates = [
            {
                'title_prefix': 'Technical Risk',
                'description_template': 'Risk of {issue} affecting {component} due to {cause}',
                'issues': ['system failure', 'performance degradation', 'security breach', 'data loss', 'integration failure']
            },
            {
                'title_prefix': 'Resource Risk',
                'description_template': 'Risk of {issue} affecting project delivery due to {cause}',
                'issues': ['resource unavailability', 'skill shortage', 'budget overrun', 'schedule delay', 'quality issues']
            },
            {
                'title_prefix': 'Business Risk',
                'description_template': 'Risk of {issue} affecting business objectives due to {cause}',
                'issues': ['market changes', 'regulatory compliance', 'stakeholder dissatisfaction', 'competitive pressure', 'technology obsolescence']
            },
            {
                'title_prefix': 'Operational Risk',
                'description_template': 'Risk of {issue} affecting operations due to {cause}',
                'issues': ['process failure', 'communication breakdown', 'vendor issues', 'infrastructure problems', 'change management issues']
            }
        ]
        
        components = ['API', 'Database', 'Frontend', 'Backend', 'Mobile App', 'Dashboard', 'Authentication', 'Analytics']
        causes = ['insufficient testing', 'resource constraints', 'technical complexity', 'external dependencies', 'timeline pressure']
        mitigations = [
            'Implement comprehensive testing strategy',
            'Allocate additional resources',
            'Simplify technical approach',
            'Establish backup plans',
            'Increase monitoring and alerting'
        ]
        
        for i in range(count):
            template = random.choice(risk_templates)
            issue = random.choice(template['issues'])
            component = random.choice(components)
            cause = random.choice(causes)
            
            description = template['description_template'].format(issue=issue, component=component, cause=cause)
            mitigation = random.choice(mitigations)
            
            # Assign to a random project
            project = random.choice(self.generated_data['projects'])
            
            risk_level = random.choice(['Low', 'Medium', 'High', 'Critical'])
            probability = random.uniform(0.1, 1.0)
            impact = random.uniform(0.1, 1.0)
            risk_score = probability * impact
            
            risk = Risk(
                project_id=project.id,
                risk_name=f"{template['title_prefix']} - {component}",
                description=description,
                risk_level=risk_level,
                probability=probability,
                impact=impact,
                risk_score=risk_score,
                mitigation_plan=mitigation,
                mitigation_owner=self.fake.name(),
                mitigation_due_date=self.fake.date_between(start_date='now', end_date='+6m'),
                status=random.choice(['Open', 'In Progress', 'Mitigated', 'Closed']),
                is_active=True,
                created_at=self.fake.date_time_between(start_date='-1y', end_date='now'),
                updated_at=self.fake.date_time_between(start_date='-6m', end_date='now'),
                created_by=self.fake.name(),
                updated_by=self.fake.name()
            )
            
            risks.append(risk)
            self.generated_data['risks'].append(risk)
        
        # Bulk insert risks
        self.db.add_all(risks)
        self.db.commit()
        logger.info(f"Generated {len(risks)} risks")
        
        return risks
    
    def generate_all_data(self):
        """Generate all demo data"""
        logger.info("Starting comprehensive demo data generation...")
        
        try:
            # Generate data in order of dependencies
            self.generate_projects(50)
            self.generate_resources(100)
            self.generate_features(270)
            self.generate_backlogs(216)
            self.generate_tasks(500)
            self.generate_risks(150)
            
            logger.info("Demo data generation completed successfully!")
            self._print_summary()
            
        except Exception as e:
            logger.error(f"Error generating demo data: {e}")
            self.db.rollback()
            raise
        finally:
            self.db.close()
    
    def _print_summary(self):
        """Print generation summary"""
        print("\n" + "="*60)
        print("🎉 DEMO DATA GENERATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"📊 Projects Generated: {len(self.generated_data['projects'])}")
        print(f"👥 Resources Generated: {len(self.generated_data['resources'])}")
        print(f"⚡ Features Generated: {len(self.generated_data['features'])}")
        print(f"📋 Backlog Items Generated: {len(self.generated_data['backlogs'])}")
        print(f"✅ Tasks Generated: {len(self.generated_data['tasks'])}")
        print(f"⚠️  Risks Generated: {len(self.generated_data['risks'])}")
        print("="*60)
        print("🚀 Your GenAI Metrics Dashboard is now ready with realistic demo data!")
        print("="*60)

def main():
    """Main function to run data generation"""
    print("🚀 Starting GenAI Metrics Dashboard Demo Data Generation...")
    print("="*60)
    
    generator = DemoDataGenerator()
    generator.generate_all_data()

if __name__ == "__main__":
    main()
