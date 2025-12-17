"""Tests for command base class."""

import pytest
from faster_app.commands.base import BaseCommand


def test_base_command_initialization():
    """Test that BaseCommand initializes properly."""
    cmd = BaseCommand()
    assert cmd is not None


def test_get_command_name_strips_suffix():
    """Test that _get_command_name strips common suffixes."""
    
    class ServerCommand(BaseCommand):
        pass
    
    name = ServerCommand._get_command_name()
    assert name == "server"


def test_get_command_name_strips_multiple_suffixes():
    """Test suffix stripping with different command classes."""
    
    class AppOperations(BaseCommand):
        pass
    
    name = AppOperations._get_command_name()
    assert name == "app"


def test_get_command_name_with_custom_class_name():
    """Test _get_command_name with explicit class name."""
    name = BaseCommand._get_command_name("TestCommand")
    assert name == "test"


def test_get_command_name_lowercase():
    """Test that command names are lowercased."""
    name = BaseCommand._get_command_name("DatabaseOperations")
    assert name == "database"
    assert name.islower()
