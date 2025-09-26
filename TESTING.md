# Testing Guide

This document provides comprehensive information about testing in the backend-integration-ai project.

## Test Structure

The project uses pytest for testing with the following structure:

```
tests/
├── conftest.py          # Shared fixtures and configuration
├── e2e/                 # End-to-end tests
│   └── test_complete_workflow.py
├── integration/         # Integration tests
│   ├── test_evaluation_endpoints.py
│   └── test_upload_endpoints.py
├── unit/                # Unit tests
│   ├── test_file_service.py
│   └── test_llm_service.py
└── fixtures/            # Test data and mock objects
    ├── mock_files.py
    └── sample_data.py
```

## Test Categories

### Unit Tests
- Test individual components in isolation
- Mock external dependencies
- Fast execution
- Located in `tests/unit/`

### Integration Tests
- Test API endpoints with real FastAPI test client
- Use temporary databases and file systems
- Test component interactions
- Located in `tests/integration/`

### End-to-End Tests
- Test complete workflows from start to finish
- Simulate real user interactions
- Test asynchronous processing
- Located in `tests/e2e/`

## Running Tests

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Specific Test Categories
```bash
# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests only
python -m pytest tests/integration/ -v

# E2E tests only
python -m pytest tests/e2e/ -v
```

### Run Tests by Markers
```bash
# Run only unit tests (using markers)
python -m pytest -m unit -v

# Run only integration tests
python -m pytest -m integration -v

# Run only e2e tests
python -m pytest -m e2e -v
```

### Run Specific Test Files
```bash
# Run file service tests
python -m pytest tests/unit/test_file_service.py -v

# Run evaluation endpoint tests
python -m pytest tests/integration/test_evaluation_endpoints.py -v
```

### Run with Coverage
```bash
# Generate coverage report
python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
```

## Test Configuration

The project uses `pytest.ini` for configuration:

- **Test Discovery**: Automatically finds test files matching `test_*.py`
- **Coverage**: Generates HTML and terminal coverage reports
- **Markers**: Defines custom markers for test categorization
- **Coverage Threshold**: Requires 80% code coverage

## Key Testing Patterns

### Async Testing
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

### Mocking External Services
```python
@patch('app.services.llm_service.LLMService.evaluate_cv')
def test_with_mock(mock_evaluate):
    mock_evaluate.return_value = {"score": 85}
    # Test logic here
```

### Temporary File Testing
```python
def test_file_operations(temp_upload_dir):
    file_path = os.path.join(temp_upload_dir, "test.txt")
    # File operations here
```

### API Testing
```python
def test_api_endpoint(client):
    response = client.post("/api/v1/upload", files={"file": ("test.pdf", b"content")})
    assert response.status_code == 200
```

## Test Data and Fixtures

### Shared Fixtures (conftest.py)
- `client`: FastAPI test client
- `temp_upload_dir`: Temporary directory for file operations
- `mock_llm_service`: Mocked LLM service

### Mock Files (fixtures/mock_files.py)
- Sample PDF, DOCX, and TXT files for testing
- Various file sizes and content types

### Sample Data (fixtures/sample_data.py)
- Job descriptions
- CV content
- Expected evaluation results

## Debugging Tests

### Run with Detailed Output
```bash
python -m pytest tests/ -v -s
```

### Run Specific Test with Debug
```bash
python -m pytest tests/unit/test_file_service.py::TestFileService::test_save_file_success -v -s
```

### Use pytest-pdb for Interactive Debugging
```bash
pip install pytest-pdb
python -m pytest tests/ --pdb
```

## Continuous Integration

Tests are designed to run in CI environments:

1. **Fast Execution**: Unit tests complete in seconds
2. **No External Dependencies**: All external services are mocked
3. **Deterministic**: Tests produce consistent results
4. **Isolated**: Tests don't interfere with each other

## Best Practices

1. **Test Naming**: Use descriptive names that explain what is being tested
2. **Arrange-Act-Assert**: Structure tests clearly
3. **Mock External Dependencies**: Don't rely on external services
4. **Use Fixtures**: Share common setup code
5. **Test Edge Cases**: Include error conditions and boundary cases
6. **Keep Tests Fast**: Unit tests should run quickly
7. **Independent Tests**: Each test should be able to run in isolation

## Common Issues and Solutions

### Async Context Manager Mocking
When mocking async file operations, ensure proper async context manager setup:
```python
async_context = Mock()
async_context.__aenter__ = Mock(return_value=async_context)
async_context.__aexit__ = Mock(return_value=None)
```

### File Upload Testing
Use proper async mock for file.read():
```python
async def async_read():
    return b"file content"
mock_file.read = async_read
```

### API Response Testing
For asynchronous APIs, test the job creation, not the final result:
```python
response = client.post("/api/v1/evaluate", json=data)
assert response.status_code == 200
assert "id" in response.json()
assert response.json()["status"] == "queued"
```

## Coverage Reports

After running tests with coverage, view the HTML report:
```bash
open htmlcov/index.html
```

The coverage report shows:
- Line coverage by file
- Missing lines
- Branch coverage
- Overall project coverage

## Performance Testing

For performance-sensitive operations, use timing assertions:
```python
import time
start_time = time.time()
# Operation to test
duration = time.time() - start_time
assert duration < 1.0  # Should complete within 1 second
```

## Summary

This testing guide provides comprehensive documentation for the project's testing strategy, covering:

- **Test Structure**: Unit, integration, and end-to-end tests organized in separate directories
- **Test Execution**: Various ways to run tests with different filters and configurations
- **Coverage**: Automated coverage reporting with HTML and terminal output
- **Best Practices**: Guidelines for writing maintainable and reliable tests
- **Debugging**: Tools and techniques for troubleshooting test issues

The testing framework is configured to ensure code quality and reliability through automated testing and coverage requirements.

## Quick Reference

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test category
pytest -m unit
pytest -m integration
pytest -m e2e

# Run specific test file
pytest tests/unit/test_file_service.py

# Debug mode
pytest -v -s
```

For more detailed information, refer to the specific sections above.