# Faster APP Tests

This directory contains the test suite for Faster APP.

## Running Tests

### Run all tests:
```bash
uv run pytest
```

### Run with coverage:
```bash
uv run pytest --cov=faster_app --cov-report=html
```

### Run specific test file:
```bash
uv run pytest tests/test_models.py -v
```

### Run specific test function:
```bash
uv run pytest tests/test_models.py::test_uuid_model_has_id_field -v
```

## Test Structure

- `conftest.py` - Common fixtures and configuration
- `test_init.py` - Tests for package initialization
- `test_models.py` - Tests for model base classes
- `test_commands.py` - Tests for command base class
- `test_response.py` - Tests for API response utilities

## Writing Tests

Follow these guidelines when writing tests:

1. Use descriptive test names that explain what is being tested
2. Use pytest fixtures for common setup
3. Keep tests independent and isolated
4. Test both success and failure cases
5. Use appropriate assertions

Example:
```python
def test_feature_works_correctly():
    """Test that feature produces expected result."""
    result = my_function()
    assert result == expected_value
```
