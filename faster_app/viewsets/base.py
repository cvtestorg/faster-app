"""
ViewSet 基类

提供 ViewSet 的基础功能，包括查询集管理、序列化器管理、对象获取等。
"""

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from fastapi import Request
from pydantic import BaseModel
from tortoise import Model
from tortoise.contrib.pydantic import PydanticModel
from tortoise.contrib.pydantic import pydantic_model_creator

from faster_app.exceptions import ForbiddenError, TooManyRequestsError, UnauthorizedError
from faster_app.viewsets.authentication import BaseAuthentication, NoAuthentication
from faster_app.viewsets.filters import BaseFilterBackend
from faster_app.viewsets.permissions import AllowAny, BasePermission
from faster_app.viewsets.throttling import BaseThrottle, NoThrottle

ModelType = TypeVar("ModelType", bound=Model)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=PydanticModel)


class ViewSet(ABC):
    """
    ViewSet 基类 - 类似 DRF 的 ViewSet
    
    提供标准的 CRUD 操作基础功能，包括：
    - 查询集管理
    - 序列化器管理
    - 对象获取
    - 钩子函数支持
    - 权限和认证
    """

    # 模型和序列化器（子类必须定义）
    model: type[Model] | None = None
    serializer_class: type[PydanticModel] | None = None
    create_serializer_class: type[BaseModel] | None = None
    update_serializer_class: type[BaseModel] | None = None

    # 权限和认证（可选，有默认值）
    permission_classes: list[type[BasePermission]] = [AllowAny]
    authentication_classes: list[type[BaseAuthentication]] = [NoAuthentication]

    # 过滤和排序（可选）
    filter_backends: list[type[BaseFilterBackend]] = []
    search_fields: list[str] = []
    ordering_fields: list[str] = []
    ordering: list[str] = []
    filter_fields: dict[str, str] = {}

    # 限流（可选）
    throttle_classes: list[type[BaseThrottle]] = [NoThrottle]
    throttle_scope: str | None = None

    # 序列化器缓存（类级别，避免重复生成）
    _serializer_cache: dict[str, type[PydanticModel]] = {}

    def __init__(self):
        """初始化 ViewSet"""
        if self.model is None:
            raise ValueError(
                f"{self.__class__.__name__} 必须定义 model 属性"
            )
        
        # 如果没有提供序列化器，自动生成（使用缓存避免重复生成）
        if self.serializer_class is None:
            cache_key = f"{self.model.__name__}_Response"
            if cache_key not in self._serializer_cache:
                self._serializer_cache[cache_key] = pydantic_model_creator(
                    self.model, name=f"{self.model.__name__}Response"
                )
            self.serializer_class = self._serializer_cache[cache_key]
        
        if self.create_serializer_class is None:
            cache_key = f"{self.model.__name__}_Create"
            if cache_key not in self._serializer_cache:
                self._serializer_cache[cache_key] = pydantic_model_creator(
                    self.model,
                    name=f"{self.model.__name__}Create",
                    exclude_readonly=True,
                    exclude=("id", "created_at", "updated_at"),
                )
            self.create_serializer_class = self._serializer_cache[cache_key]
        
        if self.update_serializer_class is None:
            cache_key = f"{self.model.__name__}_Update"
            if cache_key not in self._serializer_cache:
                self._serializer_cache[cache_key] = pydantic_model_creator(
                    self.model,
                    name=f"{self.model.__name__}Update",
                    exclude_readonly=True,
                    exclude=("id", "created_at", "updated_at"),
                    optional=tuple(
                        field_name
                        for field_name in self.model._meta.fields_map
                        if field_name not in ("id", "created_at", "updated_at")
                    ),
                )
            self.update_serializer_class = self._serializer_cache[cache_key]

    def get_queryset(self) -> Any:
        """
        获取查询集（可被子类重写）

        Returns:
            查询集对象（Tortoise QuerySet）
        """
        return self.model.all()

    def get_serializer_class(self, action: str) -> type[PydanticModel]:
        """
        根据操作获取序列化器类（可被子类重写）

        Args:
            action: 操作名称（list, create, retrieve, update, destroy）

        Returns:
            序列化器类
        """
        if action == "create":
            return self.create_serializer_class or self.serializer_class
        elif action in ("update", "partial_update"):
            return self.update_serializer_class or self.serializer_class
        else:
            return self.serializer_class

    async def get_object(self, pk: Any, prefetch: list[str] | None = None) -> Model | None:
        """
        根据主键获取对象（可被子类重写）

        Args:
            pk: 主键值
            prefetch: 需要预加载的关联字段列表

        Returns:
            模型实例或 None
        """
        query = self.model.get_or_none(id=pk)
        if query is None:
            return None
        if prefetch:
            query = query.prefetch_related(*prefetch)
        return await query

    def get_object_name(self) -> str:
        """
        获取对象名称（用于错误消息等）

        Returns:
            对象名称
        """
        if self.model:
            return self.model.__name__
        return "对象"

    # 权限实例缓存（类级别，无状态组件可以复用）
    _permission_cache: dict[type[BasePermission], BasePermission] = {}

    def get_permissions(self) -> list[BasePermission]:
        """
        获取权限实例列表（可被子类重写）

        Returns:
            权限实例列表

        Note:
            使用缓存避免重复创建无状态的权限实例
        """
        result = []
        for permission_class in self.permission_classes:
            if permission_class not in self._permission_cache:
                self._permission_cache[permission_class] = permission_class()
            result.append(self._permission_cache[permission_class])
        return result

    # 认证实例缓存（类级别，无状态组件可以复用）
    _authenticator_cache: dict[type[BaseAuthentication], BaseAuthentication] = {}

    def get_authenticators(self) -> list[BaseAuthentication]:
        """
        获取认证实例列表（可被子类重写）

        Returns:
            认证实例列表

        Note:
            使用缓存避免重复创建无状态的认证实例
        """
        result = []
        for auth_class in self.authentication_classes:
            if auth_class not in self._authenticator_cache:
                self._authenticator_cache[auth_class] = auth_class()
            result.append(self._authenticator_cache[auth_class])
        return result

    async def perform_authentication(self, request: Request) -> None:
        """
        执行认证（可被子类重写）

        Args:
            request: FastAPI 请求对象

        Raises:
            UnauthorizedError: 认证失败
        """
        authenticators = self.get_authenticators()
        for authenticator in authenticators:
            result = await authenticator.authenticate(request)
            if result is not None:
                user, token = result
                # 将用户信息存储到 request.state
                request.state.user = user
                if token:
                    request.state.auth_token = token
                return

        # 如果没有认证成功，且不是 NoAuthentication，则抛出异常
        if not isinstance(authenticators[0] if authenticators else None, NoAuthentication):
            # 如果没有设置用户，但不强制要求认证，则不抛出异常
            # 这允许某些操作不需要认证
            pass

    async def check_permissions(self, request: Request, action: str = "") -> None:
        """
        检查权限（可被子类重写）

        Args:
            request: FastAPI 请求对象
            action: 操作名称（可选）

        Raises:
            ForbiddenError: 权限不足
        """
        permissions = self.get_permissions()
        for permission in permissions:
            if not await permission.has_permission(request, self):
                raise ForbiddenError(
                    message="您没有权限执行此操作",
                    data={"action": action},
                )

    async def check_object_permissions(
        self, request: Request, obj: Any, action: str = ""
    ) -> None:
        """
        检查对象级权限（可被子类重写）

        Args:
            request: FastAPI 请求对象
            obj: 要操作的对象
            action: 操作名称（可选）

        Raises:
            ForbiddenError: 权限不足
        """
        permissions = self.get_permissions()
        for permission in permissions:
            if not await permission.has_object_permission(request, self, obj):
                raise ForbiddenError(
                    message="您没有权限操作此对象",
                    data={"action": action, "object_id": getattr(obj, "id", None)},
                )

    # 过滤后端实例缓存（类级别，无状态组件可以复用）
    _filter_backend_cache: dict[type[BaseFilterBackend], BaseFilterBackend] = {}

    def get_filter_backends(self) -> list[BaseFilterBackend]:
        """
        获取过滤后端实例列表（可被子类重写）

        Returns:
            过滤后端实例列表

        Note:
            使用缓存避免重复创建无状态的过滤后端实例
        """
        result = []
        for backend_class in self.filter_backends:
            if backend_class not in self._filter_backend_cache:
                self._filter_backend_cache[backend_class] = backend_class()
            result.append(self._filter_backend_cache[backend_class])
        return result

    async def filter_queryset(self, queryset: Any, request: Request) -> Any:
        """
        过滤查询集（可被子类重写）

        Args:
            queryset: 查询集对象
            request: FastAPI 请求对象

        Returns:
            过滤后的查询集
        """
        for backend in self.get_filter_backends():
            queryset = await backend.filter_queryset(request, queryset, self)
        return queryset

    def get_throttles(self) -> list[BaseThrottle]:
        """
        获取限流实例列表（可被子类重写）

        Returns:
            限流实例列表
        """
        return [throttle() for throttle in self.throttle_classes]

    async def check_throttles(self, request: Request) -> None:
        """
        检查限流（可被子类重写）

        Args:
            request: FastAPI 请求对象

        Raises:
            TooManyRequestsError: 请求频率过高
        """
        for throttle in self.get_throttles():
            if not await throttle.allow_request(request, self):
                wait_time = throttle.wait()
                raise TooManyRequestsError(
                    message="请求频率过高，请稍后再试",
                    data={"wait_time": wait_time} if wait_time else None,
                )
