"""
Pytest Configuration and Fixtures for Phase 8 Testing
"""

import asyncio
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import tempfile
import os
import shutil
from typing import Generator, AsyncGenerator

# Import application components
from app.main import app
from app.database import get_db, Base
from app.models.lookup_tables import Status, Priority, ProjectType, ProjectCriticalityLevel, Portfolio, Function, Platform, InvestmentType
from app.models.main_tables import Project, Resource, Feature, Task, Risk, Backlog, Approval, Charter
from app.api.deps import get_current_user

# Test Database Configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database tables
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    def override_get_current_user():
        return {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "is_active": True
        }
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="function")
def sample_project_data():
    """Sample project data for testing."""
    from datetime import date
    return {
        "project_id": "TEST-001",
        "esa_id": "ESA-001",
        "name": "Test Project",
        "description": "A test project for unit testing",
        "project_type_id": 1,
        "status_id": 1,
        "priority_id": 1,
        "criticality_id": 1,
        "portfolio_id": 1,
        "budget_amount": 100000.0,
        "start_date": date(2025, 1, 1),
        "due_date": date(2025, 12, 31),
        "project_manager": "Test Manager",
        "business_owner": "Test Owner"
    }

@pytest.fixture(scope="function")
def sample_resource_data():
    """Sample resource data for testing."""
    return {
        "name": "Test Resource",
        "email": "test@example.com",
        "role": "Developer",
        "skills": ["Python", "FastAPI", "PostgreSQL"],
        "experience_level": "Senior",
        "availability_percentage": 100.0
    }

@pytest.fixture(scope="function")
def sample_feature_data():
    """Sample feature data for testing."""
    return {
        "project_id": 1,
        "feature_name": "Test Feature",
        "description": "A test feature for unit testing",
        "status_id": 1,
        "priority_id": 1,
        "business_value": "High",
        "acceptance_criteria": "Feature works as expected",
        "complexity": "Medium",
        "effort_estimate": 40.0
    }

@pytest.fixture(scope="function")
def sample_task_data():
    """Sample task data for testing."""
    return {
        "project_id": 1,
        "task_name": "Test Task",
        "description": "A test task for unit testing",
        "status_id": 1,
        "priority_id": 1,
        "start_date": "2025-01-01",
        "due_date": "2025-01-31",
        "estimated_hours": 20.0
    }

@pytest.fixture(scope="function")
def sample_risk_data():
    """Sample risk data for testing."""
    return {
        "project_id": 1,
        "risk_name": "Test Risk",
        "description": "A test risk for unit testing",
        "risk_level": "Medium",
        "probability": 0.5,
        "impact": 0.7,
        "risk_score": 0.35,
        "mitigation_plan": "Monitor closely",
        "mitigation_owner": "Test Owner",
        "status": "Open"
    }

@pytest.fixture(scope="function")
def lookup_data(db_session):
    """Create lookup data for testing."""
    # Create status
    status = Status(
        name="Active",
        description="Active status",
        color_code="#28a745",
        is_active=True
    )
    db_session.add(status)
    
    # Create priority
    priority = Priority(
        name="High",
        description="High priority",
        level=1,
        color_code="#dc3545",
        is_active=True
    )
    db_session.add(priority)
    
    # Create project type
    project_type = ProjectType(
        name="Development",
        description="Development project",
        is_active=True
    )
    db_session.add(project_type)
    
    # Create criticality level
    criticality = ProjectCriticalityLevel(
        name="Critical",
        description="Critical project",
        level=1,
        color_code="#dc3545",
        is_active=True
    )
    db_session.add(criticality)
    
    # Create portfolio
    portfolio = Portfolio(
        name="IT Portfolio",
        level=1,
        description="IT Portfolio",
        is_active=True
    )
    db_session.add(portfolio)
    
    # Create investment type
    investment_type = InvestmentType(
        name="Capital",
        description="Capital investment",
        is_active=True
    )
    db_session.add(investment_type)
    
    db_session.commit()
    
    return {
        "status": status,
        "priority": priority,
        "project_type": project_type,
        "criticality": criticality,
        "portfolio": portfolio,
        "investment_type": investment_type
    }

@pytest.fixture(scope="function")
def test_project(db_session, sample_project_data, lookup_data):
    """Create a test project."""
    project = Project(
        project_id=sample_project_data["project_id"],
        esa_id=sample_project_data["esa_id"],
        name=sample_project_data["name"],
        description=sample_project_data["description"],
        project_type_id=lookup_data["project_type"].id,
        status_id=lookup_data["status"].id,
        priority_id=lookup_data["priority"].id,
        criticality_id=lookup_data["criticality"].id,
        portfolio_id=lookup_data["portfolio"].id,
        budget_amount=sample_project_data["budget_amount"],
        start_date=sample_project_data["start_date"],
        due_date=sample_project_data["due_date"],
        project_manager=sample_project_data["project_manager"],
        business_owner=sample_project_data["business_owner"],
        is_active=True
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project

@pytest.fixture(scope="function")
def test_resource(db_session, sample_resource_data):
    """Create a test resource."""
    resource = Resource(
        name=sample_resource_data["name"],
        email=sample_resource_data["email"],
        role=sample_resource_data["role"],
        skills=sample_resource_data["skills"],
        experience_level=sample_resource_data["experience_level"],
        availability_percentage=sample_resource_data["availability_percentage"],
        is_active=True
    )
    db_session.add(resource)
    db_session.commit()
    db_session.refresh(resource)
    return resource

@pytest.fixture(scope="function")
def test_feature(db_session, test_project, sample_feature_data, lookup_data):
    """Create a test feature."""
    feature = Feature(
        project_id=test_project.id,
        feature_name=sample_feature_data["feature_name"],
        description=sample_feature_data["description"],
        status_id=lookup_data["status"].id,
        priority_id=lookup_data["priority"].id,
        business_value=sample_feature_data["business_value"],
        acceptance_criteria=sample_feature_data["acceptance_criteria"],
        complexity=sample_feature_data["complexity"],
        effort_estimate=sample_feature_data["effort_estimate"],
        is_active=True
    )
    db_session.add(feature)
    db_session.commit()
    db_session.refresh(feature)
    return feature

@pytest.fixture(scope="function")
def test_task(db_session, test_project, sample_task_data, lookup_data):
    """Create a test task."""
    task = Task(
        project_id=test_project.id,
        task_name=sample_task_data["task_name"],
        description=sample_task_data["description"],
        status_id=lookup_data["status"].id,
        priority_id=lookup_data["priority"].id,
        start_date=sample_task_data["start_date"],
        due_date=sample_task_data["due_date"],
        estimated_hours=sample_task_data["estimated_hours"],
        is_active=True
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task

@pytest.fixture(scope="function")
def test_risk(db_session, test_project, sample_risk_data):
    """Create a test risk."""
    risk = Risk(
        project_id=test_project.id,
        risk_name=sample_risk_data["risk_name"],
        description=sample_risk_data["description"],
        risk_level=sample_risk_data["risk_level"],
        probability=sample_risk_data["probability"],
        impact=sample_risk_data["impact"],
        risk_score=sample_risk_data["risk_score"],
        mitigation_plan=sample_risk_data["mitigation_plan"],
        mitigation_owner=sample_risk_data["mitigation_owner"],
        status=sample_risk_data["status"],
        is_active=True
    )
    db_session.add(risk)
    db_session.commit()
    db_session.refresh(risk)
    return risk

@pytest.fixture(scope="function")
def multiple_projects(db_session, lookup_data):
    """Create multiple test projects."""
    projects = []
    for i in range(5):
        project = Project(
            project_id=f"TEST-{i+1:03d}",
            esa_id=f"ESA-{i+1:03d}",
            name=f"Test Project {i+1}",
            description=f"Test project {i+1} description",
            project_type_id=lookup_data["project_type"].id,
            status_id=lookup_data["status"].id,
            priority_id=lookup_data["priority"].id,
            criticality_id=lookup_data["criticality"].id,
            portfolio_id=lookup_data["portfolio"].id,
            budget_amount=100000.0 + (i * 10000),
            start_date="2025-01-01",
            due_date="2025-12-31",
            project_manager=f"Manager {i+1}",
            business_owner=f"Owner {i+1}",
            is_active=True
        )
        db_session.add(project)
        projects.append(project)
    
    db_session.commit()
    for project in projects:
        db_session.refresh(project)
    return projects

@pytest.fixture(scope="function")
def multiple_resources(db_session):
    """Create multiple test resources."""
    resources = []
    for i in range(10):
        resource = Resource(
            name=f"Resource {i+1}",
            email=f"resource{i+1}@example.com",
            role=f"Role {i+1}",
            skills=[f"Skill {i+1}", f"Skill {i+2}"],
            experience_level="Senior" if i % 2 == 0 else "Junior",
            availability_percentage=80.0 + (i * 2),
            is_active=True
        )
        db_session.add(resource)
        resources.append(resource)
    
    db_session.commit()
    for resource in resources:
        db_session.refresh(resource)
    return resources

# Performance Testing Fixtures
@pytest.fixture(scope="function")
def performance_data(db_session, lookup_data):
    """Create performance test data."""
    projects = []
    for i in range(100):
        project = Project(
            project_id=f"PERF-{i+1:03d}",
            esa_id=f"ESA-{i+1:03d}",
            name=f"Performance Project {i+1}",
            description=f"Performance test project {i+1}",
            project_type_id=lookup_data["project_type"].id,
            status_id=lookup_data["status"].id,
            priority_id=lookup_data["priority"].id,
            criticality_id=lookup_data["criticality"].id,
            portfolio_id=lookup_data["portfolio"].id,
            budget_amount=100000.0 + (i * 1000),
            start_date="2025-01-01",
            due_date="2025-12-31",
            project_manager=f"Manager {i+1}",
            business_owner=f"Owner {i+1}",
            is_active=True
        )
        db_session.add(project)
        projects.append(project)
    
    db_session.commit()
    for project in projects:
        db_session.refresh(project)
    return projects

# Security Testing Fixtures
@pytest.fixture(scope="function")
def malicious_inputs():
    """Malicious input data for security testing."""
    return {
        "sql_injection": [
            "'; DROP TABLE projects; --",
            "1' OR '1'='1",
            "'; INSERT INTO projects VALUES (1, 'hack'); --"
        ],
        "xss_payloads": [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>"
        ],
        "path_traversal": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd"
        ]
    }
