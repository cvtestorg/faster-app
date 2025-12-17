"""Tests for API response utilities."""

import pytest
from http import HTTPStatus
from faster_app.utils.response import ApiResponse


def test_success_response():
    """Test successful API response creation."""
    response = ApiResponse.success(data={"key": "value"}, message="Success")
    
    assert response.status_code == HTTPStatus.OK
    body = response.body.decode()
    assert "success" in body
    assert "true" in body.lower()
    assert "Success" in body


def test_success_response_with_custom_code():
    """Test success response with custom status code."""
    response = ApiResponse.success(
        data={"id": 123},
        code=201,
        status_code=HTTPStatus.CREATED
    )
    
    assert response.status_code == HTTPStatus.CREATED


def test_error_response():
    """Test error API response creation."""
    response = ApiResponse.error(message="Error occurred", code=400)
    
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    body = response.body.decode()
    assert "success" in body
    assert "false" in body.lower()
    assert "Error occurred" in body


def test_error_response_with_detail():
    """Test error response with additional detail."""
    response = ApiResponse.error(
        message="Validation failed",
        code=422,
        error_detail="Field 'email' is required"
    )
    
    body = response.body.decode()
    assert "error_detail" in body
    assert "Field 'email' is required" in body


def test_paginated_response():
    """Test paginated API response creation."""
    data = [{"id": 1}, {"id": 2}, {"id": 3}]
    response = ApiResponse.paginated(
        data=data,
        total=25,
        page=1,
        page_size=10
    )
    
    assert response.status_code == HTTPStatus.OK
    body = response.body.decode()
    assert "pagination" in body
    assert "total" in body
    assert "25" in body


def test_paginated_response_metadata():
    """Test pagination metadata calculation."""
    response = ApiResponse.paginated(
        data=[{"id": 1}],
        total=50,
        page=2,
        page_size=10
    )
    
    body = response.body.decode()
    # Should have next page (page 3)
    assert "has_next" in body
    # Should have previous page (page 1)
    assert "has_prev" in body
    # Total pages = 50/10 = 5
    assert "total_pages" in body
