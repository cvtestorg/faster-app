"""Tests for base model classes."""

import pytest
from faster_app.models.base import (
    UUIDModel,
    DateTimeModel,
    StatusModel,
    ScopeModel,
)


def test_uuid_model_has_id_field():
    """Test that UUIDModel has an id field."""
    assert hasattr(UUIDModel, "id")


def test_datetime_model_has_timestamp_fields():
    """Test that DateTimeModel has created_at and updated_at fields."""
    assert hasattr(DateTimeModel, "created_at")
    assert hasattr(DateTimeModel, "updated_at")


def test_status_model_has_status_field():
    """Test that StatusModel has a status field."""
    assert hasattr(StatusModel, "status")


def test_status_enum_values():
    """Test StatusModel.StatusEnum has correct values."""
    assert StatusModel.StatusEnum.ACTIVE == 1
    assert StatusModel.StatusEnum.INACTIVE == 0


def test_scope_model_has_scope_field():
    """Test that ScopeModel has a scope field."""
    assert hasattr(ScopeModel, "scope")


def test_scope_enum_values():
    """Test ScopeModel.ScopeEnum has expected values."""
    scope_enum = ScopeModel.ScopeEnum
    assert scope_enum.SYSTEM == "system"
    assert scope_enum.TENANT == "tenant"
    assert scope_enum.PROJECT == "project"
    assert scope_enum.OBJECT == "object"
