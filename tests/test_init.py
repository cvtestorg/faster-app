"""Tests for the Faster APP package."""

import faster_app


def test_version():
    """Test that version is defined."""
    assert hasattr(faster_app, "__version__")
    assert faster_app.__version__ == "0.0.43"


def test_author():
    """Test that author is defined."""
    assert hasattr(faster_app, "__author__")
    assert faster_app.__author__ == "peizhenfei"


def test_email():
    """Test that email is defined."""
    assert hasattr(faster_app, "__email__")


def test_exports_base_classes():
    """Test that base classes are exported."""
    assert hasattr(faster_app, "UUIDModel")
    assert hasattr(faster_app, "DateTimeModel")
    assert hasattr(faster_app, "StatusModel")
    assert hasattr(faster_app, "ScopeModel")


def test_exports_command_class():
    """Test that BaseCommand is exported."""
    assert hasattr(faster_app, "BaseCommand")


def test_exports_response_class():
    """Test that ApiResponse is exported."""
    assert hasattr(faster_app, "ApiResponse")


def test_exports_discover_classes():
    """Test that discover classes are exported."""
    assert hasattr(faster_app, "BaseDiscover")
    assert hasattr(faster_app, "ModelDiscover")
    assert hasattr(faster_app, "CommandDiscover")
    assert hasattr(faster_app, "RoutesDiscover")


def test_all_exports():
    """Test that __all__ is properly defined."""
    assert hasattr(faster_app, "__all__")
    assert isinstance(faster_app.__all__, list)
    assert len(faster_app.__all__) > 0
