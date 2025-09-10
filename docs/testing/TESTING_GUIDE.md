# Testing Guide

## Overview

This guide provides comprehensive information about testing the GenAI Metrics Dashboard application. The testing strategy includes unit tests, integration tests, performance tests, and security tests.

## Testing Strategy

### Test Categories

1. **Unit Tests** (`tests/unit/`)
   - Test individual components in isolation
   - Mock external dependencies
   - Fast execution (< 1 second per test)
   - High coverage (95%+)

2. **Integration Tests** (`tests/integration/`)
   - Test component interactions
   - Use real database and external services
   - Test API endpoints end-to-end
   - Moderate execution time

3. **Performance Tests** (`tests/performance/`)
   - Test system performance under load
   - Measure response times and throughput
   - Memory usage and leak detection
   - Longer execution time

4. **Security Tests**
   - Vulnerability scanning
   - Security best practices validation
   - Authentication and authorization testing

## Running Tests

### Prerequisites

1. **Python Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate     # Windows
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**
   ```bash
   # PostgreSQL (for integration tests)
   createdb test_db
   
   # Redis (for cache tests)
   redis-server
   ```

### Test Commands

#### Using the Test Runner Script

```bash
# Run all tests
python scripts/run_tests.py all

# Run specific test types
python scripts/run_tests.py unit
python scripts/run_tests.py integration
python scripts/run_tests.py performance

# Run with verbose output
python scripts/run_tests.py all --verbose

# Run without coverage
python scripts/run_tests.py all --no-coverage

# Run specific test file
python scripts/run_tests.py specific --test-path tests/unit/test_database.py
```

#### Using Pytest Directly

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m performance

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_database.py

# Run specific test function
pytest tests/unit/test_database.py::TestDatabaseConfiguration::test_database_engine_creation
```

#### Using Pre-commit Hooks

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run all hooks
pre-commit run --all-files
```

## Test Structure

### Test Organization

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── unit/                       # Unit tests
│   ├── test_database.py       # Database tests
│   ├── test_cache.py          # Cache tests
│   ├── test_memory_manager.py # Memory management tests
│   └── test_query_optimizer.py # Query optimization tests
├── integration/                # Integration tests
│   ├── test_api_endpoints.py  # API endpoint tests
│   ├── test_database_integration.py # Database integration
│   └── test_cache_integration.py   # Cache integration
└── performance/                # Performance tests
    ├── test_load_performance.py # Load testing
    ├── test_api_performance.py   # API performance
    └── test_database_performance.py # Database performance
```

### Test Fixtures

#### Database Fixtures
- `db_session`: Fresh database session for each test
- `sample_project_data`: Sample project data
- `sample_feature_data`: Sample feature data
- `sample_backlog_data`: Sample backlog data
- `sample_resource_data`: Sample resource data

#### API Fixtures
- `client`: FastAPI test client
- `async_client`: Async test client
- `sample_project`: Created project instance
- `sample_feature`: Created feature instance
- `sample_backlog`: Created backlog instance
- `sample_resource`: Created resource instance

#### Performance Fixtures
- `performance_monitor`: Performance monitoring
- `performance_test_data`: Large dataset for performance testing

## Writing Tests

### Unit Test Example

```python
import pytest
from unittest.mock import Mock, patch
from app.core.cache import RedisCache

class TestRedisCache:
    """Test Redis cache functionality."""
    
    @pytest.fixture
    def mock_redis_client(self):
        """Mock Redis client for testing."""
        mock_client = AsyncMock()
        mock_client.ping.return_value = True
        return mock_client
    
    @pytest.mark.asyncio
    async def test_redis_cache_connect_success(self, mock_redis_client):
        """Test successful Redis connection."""
        cache = RedisCache()
        
        with patch('redis.asyncio.Redis') as mock_redis_class:
            mock_redis_class.return_value = mock_redis_client
            
            await cache.connect()
            
            assert cache.redis_client is not None
            mock_redis_client.ping.assert_called_once()
```

### Integration Test Example

```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.integration
class TestProjectAPI:
    """Integration tests for project API endpoints."""
    
    def test_get_projects_endpoint(self, client, sample_project):
        """Test GET /api/v1/projects endpoint."""
        response = client.get("/api/v1/projects")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check project structure
        project = data[0]
        assert "id" in project
        assert "project_id" in project
        assert "name" in project
```

### Performance Test Example

```python
import pytest
import time
import statistics

@pytest.mark.performance
class TestLoadPerformance:
    """Load performance tests."""
    
    def test_response_time_consistency(self, client):
        """Test response time consistency across multiple requests."""
        response_times = []
        
        # Make 100 requests and measure response times
        for _ in range(100):
            start_time = time.time()
            response = client.get("/api/v1/projects")
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        # Calculate statistics
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        # Response times should be consistent
        assert avg_response_time < 0.5  # Average less than 500ms
        assert max_response_time < 1.0  # Max less than 1 second
```

## Test Configuration

### Pytest Configuration (`pytest.ini`)

```ini
[tool:pytest]
testpaths = tests
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --cov=app
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml:coverage.xml
    --cov-fail-under=95

markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    slow: Slow running tests
    api: API tests
    database: Database tests
    cache: Cache tests
```

### Coverage Configuration

- **Target Coverage**: 95%+
- **Coverage Reports**: HTML, XML, Terminal
- **Excluded Files**: Tests, migrations, virtual environments
- **Coverage Threshold**: Fails if below 95%

## CI/CD Integration

### GitHub Actions Workflow

The CI/CD pipeline includes:

1. **Code Quality Checks**
   - Pre-commit hooks
   - Black formatting
   - isort import sorting
   - Flake8 linting
   - MyPy type checking
   - Bandit security scanning

2. **Test Execution**
   - Unit tests
   - Integration tests
   - Performance tests
   - Security tests

3. **Coverage Reporting**
   - Code coverage metrics
   - Coverage reports
   - Coverage thresholds

4. **Docker Testing**
   - Docker image build
   - Container testing
   - Service health checks

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        args: [--line-length=100]
  
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100]
```

## Performance Benchmarks

### Response Time Targets

| Endpoint | Target | Threshold |
|----------|--------|-----------|
| `/api/v1/projects` | 500ms | 1s |
| `/api/v1/features` | 500ms | 1s |
| `/api/v1/dashboard` | 1s | 2s |
| `/api/v1/performance/health` | 200ms | 500ms |

### Throughput Targets

- **Concurrent Users**: 100+
- **Requests per Second**: 50+
- **Database Queries**: < 100ms average
- **Memory Usage**: < 100MB increase under load

### Load Testing

```bash
# Run performance tests
pytest tests/performance/ -m performance

# Run specific performance test
pytest tests/performance/test_load_performance.py::TestLoadPerformance::test_concurrent_requests_performance
```

## Debugging Tests

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Check PostgreSQL is running
   pg_isready
   
   # Check Redis is running
   redis-cli ping
   ```

2. **Import Errors**
   ```bash
   # Check Python path
   export PYTHONPATH=/path/to/project:$PYTHONPATH
   ```

3. **Test Failures**
   ```bash
   # Run with verbose output
   pytest -v --tb=long
   
   # Run specific test with debugging
   pytest tests/unit/test_database.py::TestDatabaseConfiguration::test_database_engine_creation -v -s
   ```

### Test Debugging Tools

1. **Pytest Debugging**
   ```python
   import pytest
   
   def test_debug_example():
       # Add breakpoint
       pytest.set_trace()
       
       # Or use pdb
       import pdb; pdb.set_trace()
   ```

2. **Coverage Debugging**
   ```bash
   # Generate coverage report
   pytest --cov=app --cov-report=html
   
   # View coverage report
   open htmlcov/index.html
   ```

## Best Practices

### Test Writing Guidelines

1. **Test Naming**
   - Use descriptive test names
   - Follow pattern: `test_<function>_<condition>_<expected_result>`
   - Example: `test_get_project_by_id_not_found`

2. **Test Structure**
   - Arrange: Set up test data
   - Act: Execute the function/endpoint
   - Assert: Verify the results

3. **Test Isolation**
   - Each test should be independent
   - Use fixtures for setup/teardown
   - Clean up after tests

4. **Mocking**
   - Mock external dependencies
   - Use realistic mock data
   - Test error conditions

### Performance Testing Guidelines

1. **Realistic Data**
   - Use production-like data volumes
   - Test with various data sizes
   - Include edge cases

2. **Load Patterns**
   - Test gradual load increase
   - Test peak load conditions
   - Test sustained load

3. **Resource Monitoring**
   - Monitor memory usage
   - Monitor CPU usage
   - Monitor database connections

## Troubleshooting

### Common Test Failures

1. **Database Connection Errors**
   - Check database is running
   - Verify connection string
   - Check database permissions

2. **Import Errors**
   - Check PYTHONPATH
   - Verify package installation
   - Check import paths

3. **Timeout Errors**
   - Increase timeout values
   - Check system resources
   - Optimize slow tests

4. **Coverage Failures**
   - Review uncovered code
   - Add missing tests
   - Check coverage configuration

### Getting Help

1. **Check Logs**
   ```bash
   # Run tests with logging
   pytest --log-cli-level=INFO
   ```

2. **Review Documentation**
   - Check this guide
   - Review pytest documentation
   - Check FastAPI testing docs

3. **Debug Mode**
   ```bash
   # Run with debugging
   pytest -v -s --pdb
   ```

## Conclusion

This testing guide provides comprehensive coverage of the testing strategy for the GenAI Metrics Dashboard. Following these guidelines ensures high code quality, reliability, and performance of the application.

For questions or issues, refer to the troubleshooting section or check the project documentation.
