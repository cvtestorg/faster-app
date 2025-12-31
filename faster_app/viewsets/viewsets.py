"""
ViewSet 实现类

提供常用的 ViewSet 组合类，包括 ModelViewSet 和 ReadOnlyModelViewSet。
"""

from typing import Any

from fastapi import APIRouter, Request

from faster_app.viewsets.actions import action
from faster_app.viewsets.base import ViewSet
from faster_app.viewsets.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)


class ModelViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    ViewSet,
):
    """
    ModelViewSet - 提供完整的 CRUD 操作

    组合了所有 Mixin，提供：
    - list() - 列表查询（GET /）
    - create() - 创建（POST /）
    - retrieve() - 单个查询（GET /{pk}）
    - update() - 完整更新（PUT /{pk}）
    - partial_update() - 部分更新（PATCH /{pk}）
    - destroy() - 删除（DELETE /{pk}）

    Example:
        class DemoViewSet(ModelViewSet):
            model = DemoModel
            serializer_class = DemoResponse
            create_serializer_class = DemoCreate
            update_serializer_class = DemoUpdate

            def get_queryset(self):
                return self.model.filter(status=1)

            @action(detail=True, methods=["POST"])
            async def activate(self, request: Request, pk: str):
                instance = await self.get_object(pk)
                if not instance:
                    raise NotFoundError(message="记录不存在")
                instance.status = 1
                await instance.save()
                serializer_class = self.get_serializer_class("retrieve")
                return await serializer_class.from_tortoise_orm(instance)

        # 注册路由
        router = as_router(DemoViewSet, prefix="/demos", tags=["Demo"])
        # 或使用类方法
        router = DemoViewSet.as_router(prefix="/demos", tags=["Demo"])
    """

    @classmethod
    def as_router(
        cls,
        prefix: str = "",
        tags: list[str] | None = None,
        operations: str = "CRUDL",
    ):
        """
        类方法：将 ViewSet 转换为 Router（便捷方法）

        Args:
            prefix: 路由前缀
            tags: OpenAPI 标签
            operations: 支持的操作

        Returns:
            APIRouter 实例

        Example:
            router = DemoViewSet.as_router(prefix="/demos", tags=["Demo"])
        """
        from faster_app.viewsets.routers import as_router
        return as_router(cls, prefix=prefix, tags=tags, operations=operations)


class ReadOnlyModelViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    ViewSet,
):
    """
    ReadOnlyModelViewSet - 只读 ViewSet

    只提供查询操作：
    - list() - 列表查询（GET /）
    - retrieve() - 单个查询（GET /{pk}）

    Example:
        class LogViewSet(ReadOnlyModelViewSet):
            model = LogModel
            serializer_class = LogResponse

        # 注册路由
        router = as_router(LogViewSet, prefix="/logs", tags=["Log"])
    """

    @classmethod
    def as_router(
        cls,
        prefix: str = "",
        tags: list[str] | None = None,
        operations: str = "RL",  # 只读模式默认只有 R 和 L
    ):
        """
        类方法：将 ViewSet 转换为 Router（便捷方法）

        Args:
            prefix: 路由前缀
            tags: OpenAPI 标签
            operations: 支持的操作（默认 "RL"）

        Returns:
            APIRouter 实例
        """
        from faster_app.viewsets.routers import as_router
        return as_router(cls, prefix=prefix, tags=tags, operations=operations)
