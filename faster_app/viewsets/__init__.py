"""
ViewSet 模块 - 类似 Django REST Framework 的 ViewSet 实现

提供 ViewSet 基类、Mixin 类和常用 ViewSet，用于快速构建 RESTful API。
"""

from faster_app.viewsets.actions import action
from faster_app.viewsets.authentication import (
    BaseAuthentication,
    JWTAuthentication,
    NoAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)
from faster_app.viewsets.base import ViewSet
from faster_app.viewsets.filters import (
    BaseFilterBackend,
    DjangoFilterBackend,
    FieldFilter,
    OrderingFilter,
    SearchFilter,
)
from faster_app.viewsets.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from faster_app.viewsets.permissions import (
    AllowAny,
    BasePermission,
    IsAdminUser,
    IsAuthenticated,
    IsOwner,
    IsOwnerOrReadOnly,
)
from faster_app.viewsets.routers import as_router
from faster_app.viewsets.throttling import (
    AnonRateThrottle,
    BaseThrottle,
    NoThrottle,
    ScopedRateThrottle,
    SimpleRateThrottle,
    UserRateThrottle,
)
from faster_app.viewsets.viewsets import ModelViewSet, ReadOnlyModelViewSet

__all__ = [
    # 基类
    "ViewSet",
    # Mixin 类
    "ListModelMixin",
    "CreateModelMixin",
    "RetrieveModelMixin",
    "UpdateModelMixin",
    "DestroyModelMixin",
    # ViewSet 类
    "ModelViewSet",
    "ReadOnlyModelViewSet",
    # 权限类
    "BasePermission",
    "AllowAny",
    "IsAuthenticated",
    "IsAdminUser",
    "IsOwner",
    "IsOwnerOrReadOnly",
    # 认证类
    "BaseAuthentication",
    "NoAuthentication",
    "JWTAuthentication",
    "TokenAuthentication",
    "SessionAuthentication",
    # 过滤类
    "BaseFilterBackend",
    "SearchFilter",
    "OrderingFilter",
    "FieldFilter",
    "DjangoFilterBackend",
    # 限流类
    "BaseThrottle",
    "NoThrottle",
    "SimpleRateThrottle",
    "UserRateThrottle",
    "AnonRateThrottle",
    "ScopedRateThrottle",
    # 装饰器和工具
    "action",
    "as_router",
]
