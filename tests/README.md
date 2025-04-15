# AITradeStrategist Testing Framework

This directory contains the testing framework for the AITradeStrategist application. The tests are organized into different categories based on their scope and purpose.

## Test Categories

- **Unit Tests**: Tests for individual components in isolation.
- **Integration Tests**: Tests for interactions between components.
- **Functional Tests**: Tests for complete features from a user's perspective.

## Test Structure

```
tests/
├── conftest.py                # Shared fixtures and configuration
├── unit/                      # Unit tests
│   ├── test_models.py         # Tests for database models
│   ├── test_gpu_utils.py      # Tests for GPU utilities
│   └── ...
├── integration/               # Integration tests
│   ├── test_freqtrade_integration.py  # Tests for Freqtrade integration
│   └── ...
└── functional/                # Functional tests
    ├── test_routes.py         # Tests for application routes
    ├── test_ui.py             # Tests for the web UI
    └── ...
```

## Running Tests

You can use the `run_tests.py` script at the root of the project to run tests. Here are some examples:

### Run all tests

```bash
python run_tests.py
```

### Run unit tests only

```bash
python run_tests.py --unit
```

### Run integration tests only

```bash
python run_tests.py --integration
```

### Run functional tests only

```bash
python run_tests.py --functional
```

### Run tests with verbose output

```bash
python run_tests.py -v
```

### Generate a coverage report

```bash
python run_tests.py --cov
```

### Generate an HTML coverage report

```bash
python run_tests.py --cov --html
```

## Writing Tests

### Unit Tests

Unit tests should focus on testing individual components in isolation. Use mocks to avoid testing dependencies.

```python
def test_function_name():
    # Arrange
    input_data = ...
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_result
```

### Integration Tests

Integration tests should focus on testing the interactions between components.

```python
def test_component_interaction():
    # Arrange
    component1 = Component1()
    component2 = Component2()
    
    # Act
    result = component1.interact_with(component2)
    
    # Assert
    assert result == expected_result
```

### Functional Tests

Functional tests should focus on testing complete features from a user's perspective.

```python
def test_user_workflow(client):
    # Arrange
    client.post('/login', data={'username': 'test', 'password': 'test'})
    
    # Act
    response = client.get('/dashboard')
    
    # Assert
    assert response.status_code == 200
    assert 'Welcome, test' in response.data.decode('utf-8')
```

## Test Fixtures

Common test fixtures are defined in `conftest.py`. These include:

- `flask_app`: A Flask application for testing.
- `client`: A test client for the Flask application.
- `db_session`: A database session for testing.

## Continuous Integration

The tests are run automatically as part of the CI/CD pipeline. You can view the results in the CI/CD dashboard.