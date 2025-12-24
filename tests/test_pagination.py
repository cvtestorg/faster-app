"""
Tests for pagination utilities.

This module tests the unified pagination functionality provided by
faster_app.utils.pagination module.
"""

import pytest
from faster_app.utils.pagination import Page, Params, CustomParams, paginate


def test_page_model_structure():
    """Test that Page model has expected structure."""
    # Page should be a generic type that can be parameterized
    assert Page is not None
    assert hasattr(Page, "__class_getitem__")


def test_params_default_values():
    """Test default pagination parameters."""
    params = Params()
    assert params.page == 1
    assert params.size == 50  # default size in fastapi-pagination


def test_custom_params_default_values():
    """Test custom pagination parameters with modified defaults."""
    params = CustomParams()
    assert params.page == 1
    assert params.size == 20  # custom default


def test_paginate_with_list():
    """Test pagination with a simple list."""
    items = list(range(100))
    params = Params(page=1, size=10)
    
    result = paginate(items, params)
    
    assert result is not None
    assert hasattr(result, "items")
    assert hasattr(result, "total")
    assert hasattr(result, "page")
    assert hasattr(result, "size")
    assert len(result.items) == 10
    assert result.total == 100
    assert result.page == 1
    assert result.size == 10


def test_paginate_with_list_second_page():
    """Test pagination on second page."""
    items = list(range(100))
    params = Params(page=2, size=10)
    
    result = paginate(items, params)
    
    assert len(result.items) == 10
    assert result.items[0] == 10  # second page starts at index 10
    assert result.page == 2


def test_paginate_with_empty_list():
    """Test pagination with empty list."""
    items = []
    params = Params(page=1, size=10)
    
    result = paginate(items, params)
    
    assert result.total == 0
    assert len(result.items) == 0


def test_paginate_with_less_items_than_page_size():
    """Test pagination when total items < page size."""
    items = list(range(5))
    params = Params(page=1, size=10)
    
    result = paginate(items, params)
    
    assert result.total == 5
    assert len(result.items) == 5


def test_paginate_with_custom_params():
    """Test pagination with custom params."""
    items = list(range(100))
    params = CustomParams(page=1, size=20)
    
    result = paginate(items, params)
    
    assert len(result.items) == 20
    assert result.size == 20


def test_params_validation():
    """Test that Params validates input correctly."""
    # page must be >= 1
    with pytest.raises(Exception):
        Params(page=0, size=10)
    
    # size must be >= 1
    with pytest.raises(Exception):
        Params(page=1, size=0)


def test_custom_params_max_size():
    """Test that CustomParams enforces max size."""
    # size must be <= 100
    with pytest.raises(Exception):
        CustomParams(page=1, size=101)
