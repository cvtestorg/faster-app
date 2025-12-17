"""
Base model classes using Tortoise ORM.

This module provides reusable base model classes with common fields
and functionality for database models.
"""

from enum import IntEnum, StrEnum
from tortoise import Model
from tortoise.fields import (
    IntEnumField,
    UUIDField,
    DatetimeField,
    CharEnumField,
)


class UUIDModel(Model):
    """Base model class with UUID primary key.
    
    Provides a UUID field as the primary key for models that need
    globally unique identifiers.
    
    Attributes:
        id: UUID field serving as the primary key
    """

    id = UUIDField(primary_key=True, verbose_name="ID")

    class Meta:
        abstract = True


class DateTimeModel(Model):
    """Base model class with automatic timestamp fields.
    
    Provides created_at and updated_at fields that are automatically
    managed by the ORM.
    
    Attributes:
        created_at: Timestamp when the record was created
        updated_at: Timestamp when the record was last updated
    """

    created_at = DatetimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = DatetimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True


class StatusModel(Model):
    """Base model class with status field.
    
    Provides a status field with predefined enum values for tracking
    record state (active/inactive).
    
    Attributes:
        status: Integer status field with ACTIVE=1 or INACTIVE=0
    """

    class StatusEnum(IntEnum):
        """Status enumeration for model records."""

        ACTIVE = 1
        INACTIVE = 0

    status = IntEnumField(default=1, verbose_name="状态", enum_type=StatusEnum)

    class Meta:
        abstract = True


class ScopeModel(Model):
    """Base model class with scope field for multi-tenancy support.
    
    Provides a scope field to support different levels of data isolation
    in multi-tenant applications.
    
    Attributes:
        scope: String enum defining the isolation level of the record
    """

    class ScopeEnum(StrEnum):
        """Scope enumeration for multi-tenant isolation levels."""

        SYSTEM = "system"
        TENANT = "tenant"
        PROJECT = "project"
        OBJECT = "object"

    scope = CharEnumField(ScopeEnum, default=ScopeEnum.PROJECT, verbose_name="作用域")

    class Meta:
        abstract = True
