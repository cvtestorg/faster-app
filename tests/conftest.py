"""
Test configuration and fixtures.

This module provides common pytest fixtures and configuration
for the test suite.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    """
    Provide a FastAPI test client for integration testing.
    
    Returns:
        TestClient instance for making HTTP requests to the app
    """
    from faster_app.app import get_app
    
    app = get_app()
    return TestClient(app)


@pytest.fixture
def mock_settings():
    """
    Provide mock settings for testing.
    
    Returns:
        Dictionary with mock configuration values
    """
    return {
        "DEBUG": True,
        "PROJECT_NAME": "Test Project",
        "VERSION": "0.0.1",
        "HOST": "127.0.0.1",
        "PORT": 8000,
    }
