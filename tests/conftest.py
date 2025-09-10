"""
Test Configuration and Fixtures
Provides shared test configuration and fixtures for all test modules
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import tempfile
import os
from datetime import datetime, timedelta

from app.main import app
from app.database import get_db, Base
from app.core.cache import cache_manager
from app.core.memory_manager import memory_monitor, websocket_manager
from app.models import *  # Import all models

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test engine with in-memory SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def async_client(db_session):
    """Create an async test client."""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Use httpx for async testing
    import httpx
    async with httpx.AsyncClient(app=app, base_url="http://test") as async_client:
        yield async_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def cache_client():
    """Create a test cache client."""
    # Initialize cache manager for testing
    await cache_manager.initialize()
    
    try:
        yield cache_manager
    finally:
        await cache_manager.shutdown()


@pytest.fixture(scope="function")
def sample_project_data():
    """Sample project data for testing."""
    return {
        "project_id": "TEST-001",
        "esa_id": "TEST-ESA-001",
        "name": "Test Project",
        "description": "A test project for unit testing",
        "status_id": 1,
        "priority_id": 1,
        "criticality_id": 1,
        "portfolio_id": 1,
        "budget_amount": 100000.00,
        "start_date": "2025-01-01",
        "due_date": "2025-12-31",
        "percent_complete": 0.0,
        "project_manager": "Test Manager",
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "created_by": "test_user",
        "updated_by": "test_user"
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
        "business_value": "High business value",
        "acceptance_criteria": "Feature works correctly",
        "complexity": "Medium",
        "effort_estimate": 8.0,
        "planned_start_date": "2025-01-01",
        "planned_end_date": "2025-03-31",
        "percent_complete": 0.0,
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "created_by": "test_user",
        "updated_by": "test_user"
    }


@pytest.fixture(scope="function")
def sample_backlog_data():
    """Sample backlog data for testing."""
    return {
        "backlog_id": "BL-TEST-001",
        "name": "Test Backlog Item",
        "description": "A test backlog item for unit testing",
        "priority_id": 1,
        "status_id": 1,
        "business_value": "High business value",
        "user_story": "As a user, I want to test the system",
        "acceptance_criteria": "System works correctly",
        "complexity": "Low",
        "effort_estimate": 5.0,
        "target_quarter": "Q1 2025",
        "planned_start_date": "2025-01-01",
        "planned_end_date": "2025-02-28",
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "created_by": "test_user",
        "updated_by": "test_user"
    }


@pytest.fixture(scope="function")
def sample_resource_data():
    """Sample resource data for testing."""
    return {
        "name": "Test Resource",
        "email": "test.resource@example.com",
        "role": "Developer",
        "skills": ["Python", "FastAPI", "PostgreSQL"],
        "experience_level": "Senior",
        "is_active": True,
        "availability_percentage": 100.0,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "created_by": "test_user",
        "updated_by": "test_user"
    }


@pytest.fixture(scope="function")
def sample_lookup_data(db_session):
    """Create sample lookup data for testing."""
    # Create sample status
    status = Status(
        name="Active",
        description="Active status",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(status)
    
    # Create sample priority
    priority = Priority(
        name="High",
        description="High priority",
        level=1,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(priority)
    
    # Create sample criticality
    criticality = ProjectCriticalityLevel(
        name="Critical",
        description="Critical project",
        level=1,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(criticality)
    
    # Create sample portfolio
    portfolio = Portfolio(
        name="Test Portfolio",
        description="Test portfolio",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(portfolio)
    
    # Create sample project type
    project_type = ProjectType(
        name="Development",
        description="Development project",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(project_type)
    
    # Create sample investment type
    investment_type = InvestmentType(
        name="Capital",
        description="Capital investment",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(investment_type)
    
    db_session.commit()
    
    return {
        "status": status,
        "priority": priority,
        "criticality": criticality,
        "portfolio": portfolio,
        "project_type": project_type,
        "investment_type": investment_type
    }


@pytest.fixture(scope="function")
def sample_project(db_session, sample_project_data, sample_lookup_data):
    """Create a sample project for testing."""
    project = Project(**sample_project_data)
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture(scope="function")
def sample_feature(db_session, sample_feature_data, sample_project):
    """Create a sample feature for testing."""
    feature_data = sample_feature_data.copy()
    feature_data["project_id"] = sample_project.id
    feature = Feature(**feature_data)
    db_session.add(feature)
    db_session.commit()
    db_session.refresh(feature)
    return feature


@pytest.fixture(scope="function")
def sample_backlog(db_session, sample_backlog_data):
    """Create a sample backlog for testing."""
    backlog = Backlog(**sample_backlog_data)
    db_session.add(backlog)
    db_session.commit()
    db_session.refresh(backlog)
    return backlog


@pytest.fixture(scope="function")
def sample_resource(db_session, sample_resource_data):
    """Create a sample resource for testing."""
    resource = Resource(**sample_resource_data)
    db_session.add(resource)
    db_session.commit()
    db_session.refresh(resource)
    return resource


@pytest.fixture(scope="function")
def mock_websocket():
    """Mock WebSocket connection for testing."""
    class MockWebSocket:
        def __init__(self):
            self.sent_messages = []
            self.is_closed = False
        
        async def send_json(self, data):
            self.sent_messages.append(data)
        
        async def close(self):
            self.is_closed = True
        
        def is_active(self):
            return not self.is_closed
    
    return MockWebSocket()


@pytest.fixture(scope="function")
def performance_test_data():
    """Performance test data for load testing."""
    return {
        "projects": [
            {
                "project_id": f"PERF-{i:03d}",
                "name": f"Performance Test Project {i}",
                "description": f"Performance test project {i}",
                "status_id": 1,
                "priority_id": 1,
                "criticality_id": 1,
                "portfolio_id": 1,
                "budget_amount": 100000.00,
                "start_date": "2025-01-01",
                "due_date": "2025-12-31",
                "percent_complete": 0.0,
                "project_manager": f"Manager {i}",
                "is_active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "created_by": "perf_test",
                "updated_by": "perf_test"
            }
            for i in range(1, 101)  # 100 projects
        ],
        "features": [
            {
                "project_id": (i % 100) + 1,  # Distribute across projects
                "feature_name": f"Performance Test Feature {i}",
                "description": f"Performance test feature {i}",
                "status_id": 1,
                "priority_id": 1,
                "business_value": "Performance testing",
                "acceptance_criteria": "Meets performance requirements",
                "complexity": "Medium",
                "effort_estimate": 8.0,
                "planned_start_date": "2025-01-01",
                "planned_end_date": "2025-03-31",
                "percent_complete": 0.0,
                "is_active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "created_by": "perf_test",
                "updated_by": "perf_test"
            }
            for i in range(1, 201)  # 200 features
        ]
    }


# Test utilities
class TestUtils:
    """Utility functions for testing."""
    
    @staticmethod
    def assert_response_success(response, expected_status=200):
        """Assert that response is successful."""
        assert response.status_code == expected_status
        assert response.json() is not None
    
    @staticmethod
    def assert_response_error(response, expected_status=400):
        """Assert that response is an error."""
        assert response.status_code == expected_status
        assert "error" in response.json() or "detail" in response.json()
    
    @staticmethod
    def assert_pagination(response_data):
        """Assert that response has pagination structure."""
        assert "data" in response_data
        assert "pagination" in response_data
        pagination = response_data["pagination"]
        assert "page" in pagination
        assert "per_page" in pagination
        assert "total" in pagination
        assert "pages" in pagination
    
    @staticmethod
    def assert_performance_metrics(metrics):
        """Assert that performance metrics are valid."""
        assert "timestamp" in metrics
        assert "database" in metrics
        assert "memory" in metrics
        assert "websockets" in metrics
        assert "cache" in metrics


@pytest.fixture
def test_utils():
    """Provide test utilities."""
    return TestUtils


# Performance testing fixtures
@pytest.fixture(scope="function")
def performance_monitor():
    """Performance monitoring for tests."""
    import time
    import psutil
    
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.start_memory = None
            self.measurements = []
        
        def start(self):
            self.start_time = time.time()
            self.start_memory = psutil.Process().memory_info().rss
        
        def stop(self):
            if self.start_time:
                duration = time.time() - self.start_time
                current_memory = psutil.Process().memory_info().rss
                memory_delta = current_memory - self.start_memory
                
                measurement = {
                    "duration": duration,
                    "memory_delta": memory_delta,
                    "timestamp": datetime.now()
                }
                self.measurements.append(measurement)
                return measurement
            return None
        
        def get_stats(self):
            if not self.measurements:
                return None
            
            durations = [m["duration"] for m in self.measurements]
            memory_deltas = [m["memory_delta"] for m in self.measurements]
            
            return {
                "count": len(self.measurements),
                "avg_duration": sum(durations) / len(durations),
                "max_duration": max(durations),
                "min_duration": min(durations),
                "avg_memory_delta": sum(memory_deltas) / len(memory_deltas),
                "max_memory_delta": max(memory_deltas),
                "min_memory_delta": min(memory_deltas)
            }
    
    return PerformanceMonitor()


# Cleanup fixtures
@pytest.fixture(scope="function", autouse=True)
def cleanup_test_data():
    """Clean up test data after each test."""
    yield
    # Cleanup is handled by db_session fixture
    pass


# Test configuration
pytest_plugins = []

# Test markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "api: mark test as API test"
    )
    config.addinivalue_line(
        "markers", "database: mark test as database test"
    )
    config.addinivalue_line(
        "markers", "cache: mark test as cache test"
    )
    config.addinivalue_line(
        "markers", "websocket: mark test as websocket test"
    )
