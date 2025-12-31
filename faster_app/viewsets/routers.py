"""
ViewSet 路由注册

提供将 ViewSet 转换为 FastAPI Router 的功能。
"""

from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi_pagination import Params

from faster_app.viewsets.base import ViewSet
from faster_app.viewsets.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)


class ViewSetRouter:
    """
    ViewSet 路由注册器
    
    将 ViewSet 转换为 FastAPI Router
    """

    def __init__(
        self,
        viewset_class: type[ViewSet],
        prefix: str = "",
        tags: list[str] | None = None,
        operations: str = "CRUDL",
    ):
        """
        初始化路由注册器

        Args:
            viewset_class: ViewSet 类
            prefix: 路由前缀
            tags: OpenAPI 标签
            operations: 支持的操作 (C=Create, R=Retrieve, U=Update, D=Destroy, L=List)
        """
        self.viewset_class = viewset_class
        self.prefix = prefix
        self.tags = tags or []
        self.operations = operations.upper()

    def get_router(self) -> APIRouter:
        """
        生成 FastAPI Router

        Returns:
            APIRouter 实例

        Note:
            ViewSet 实例在每次请求时创建，确保无状态性
        """
        router = APIRouter(prefix=self.prefix, tags=self.tags)

        # 创建一个临时实例用于检查类型和获取序列化器类
        temp_instance = self.viewset_class()

        # 注册标准 CRUD 路由（每次请求创建新实例）
        if "L" in self.operations and isinstance(temp_instance, ListModelMixin):
            self._register_list_route(router, self.viewset_class)

        if "C" in self.operations and isinstance(temp_instance, CreateModelMixin):
            self._register_create_route(router, self.viewset_class)

        if "R" in self.operations and isinstance(temp_instance, RetrieveModelMixin):
            self._register_retrieve_route(router, self.viewset_class)

        if "U" in self.operations and isinstance(temp_instance, UpdateModelMixin):
            self._register_update_route(router, self.viewset_class)
            self._register_partial_update_route(router, self.viewset_class)

        if "D" in self.operations and isinstance(temp_instance, DestroyModelMixin):
            self._register_destroy_route(router, self.viewset_class)

        # 注册自定义 action 路由
        self._register_custom_actions(router, self.viewset_class)

        return router

    def _register_list_route(
        self, router: APIRouter, viewset_class: type[ViewSet]
    ) -> None:
        """注册列表路由"""

        @router.get("/", response_model=Any)
        async def list_view(request: Request, pagination: Params = Depends()):
            # 每次请求创建新的 ViewSet 实例，确保无状态
            viewset = viewset_class()
            return await viewset.list(request, pagination)

    def _register_create_route(
        self, router: APIRouter, viewset_class: type[ViewSet]
    ) -> None:
        """注册创建路由"""
        # 创建临时实例获取序列化器类
        temp_instance = viewset_class()
        serializer_class = temp_instance.create_serializer_class or temp_instance.serializer_class

        @router.post("/", response_model=Any)
        async def create_view(request: Request, create_data: serializer_class):
            # 每次请求创建新的 ViewSet 实例，确保无状态
            viewset = viewset_class()
            return await viewset.create(request, create_data)

    def _register_retrieve_route(
        self, router: APIRouter, viewset_class: type[ViewSet]
    ) -> None:
        """注册单个查询路由"""

        @router.get("/{pk}", response_model=Any)
        async def retrieve_view(request: Request, pk: str):
            # 每次请求创建新的 ViewSet 实例，确保无状态
            viewset = viewset_class()
            return await viewset.retrieve(request, pk)

    def _register_update_route(
        self, router: APIRouter, viewset_class: type[ViewSet]
    ) -> None:
        """注册完整更新路由"""
        # 创建临时实例获取序列化器类
        temp_instance = viewset_class()
        serializer_class = temp_instance.update_serializer_class or temp_instance.serializer_class

        @router.put("/{pk}", response_model=Any)
        async def update_view(request: Request, pk: str, update_data: serializer_class):
            # 每次请求创建新的 ViewSet 实例，确保无状态
            viewset = viewset_class()
            return await viewset.update(request, pk, update_data)

    def _register_partial_update_route(
        self, router: APIRouter, viewset_class: type[ViewSet]
    ) -> None:
        """注册部分更新路由"""
        # 创建临时实例获取序列化器类
        temp_instance = viewset_class()
        serializer_class = temp_instance.update_serializer_class or temp_instance.serializer_class

        @router.patch("/{pk}", response_model=Any)
        async def partial_update_view(
            request: Request, pk: str, update_data: serializer_class
        ):
            # 每次请求创建新的 ViewSet 实例，确保无状态
            viewset = viewset_class()
            return await viewset.partial_update(request, pk, update_data)

    def _register_destroy_route(
        self, router: APIRouter, viewset_class: type[ViewSet]
    ) -> None:
        """注册删除路由"""

        @router.delete("/{pk}")
        async def destroy_view(request: Request, pk: str):
            # 每次请求创建新的 ViewSet 实例，确保无状态
            viewset = viewset_class()
            return await viewset.destroy(request, pk)

    def _register_custom_actions(
        self, router: APIRouter, viewset_class: type[ViewSet]
    ) -> None:
        """注册自定义 action 路由"""
        # 获取 ViewSet 类的方法（不是实例方法）
        for attr_name in dir(viewset_class):
            # 跳过私有方法和特殊方法
            if attr_name.startswith("_") or attr_name in [
                "get_queryset",
                "get_object",
                "get_serializer_class",
                "get_object_name",
                "list",
                "create",
                "retrieve",
                "update",
                "partial_update",
                "destroy",
            ]:
                continue

            attr = getattr(viewset_class, attr_name)
            if not callable(attr) or not hasattr(attr, "action"):
                continue

            methods = getattr(attr, "action_methods", ["GET"])
            detail = getattr(attr, "action_detail", False)
            url_path = getattr(attr, "action_url_path", attr_name.replace("_", "-"))
            action_kwargs = getattr(attr, "action_kwargs", {})

            # 构建路由路径
            if detail:
                route_path = f"/{{pk}}/{url_path}"
            else:
                route_path = f"/{url_path}"

            # 为每个方法创建独立的处理函数
            # 使用默认参数来避免闭包问题
            for method in methods:
                # 使用默认参数来捕获当前循环的值
                def make_handler(
                    action_method=attr,
                    is_detail=detail,
                    vs_class=viewset_class,
                    action_name=attr_name,
                ):
                    if is_detail:
                        async def handler(request: Request, pk: str, **kwargs):
                            # 每次请求创建新的 ViewSet 实例，确保无状态
                            viewset = vs_class()
                            # 检查限流
                            await viewset.check_throttles(request)
                            # 执行认证和权限检查
                            await viewset.perform_authentication(request)
                            await viewset.check_permissions(request, action_name)
                            # 如果是对象级操作，获取对象并检查对象权限
                            instance = await viewset.get_object(pk)
                            if instance:
                                await viewset.check_object_permissions(request, instance, action_name)
                            return await action_method(viewset, request, pk, **kwargs)
                        return handler
                    else:
                        async def handler(request: Request, **kwargs):
                            # 每次请求创建新的 ViewSet 实例，确保无状态
                            viewset = vs_class()
                            # 检查限流
                            await viewset.check_throttles(request)
                            # 执行认证和权限检查
                            await viewset.perform_authentication(request)
                            await viewset.check_permissions(request, action_name)
                            return await action_method(viewset, request, **kwargs)
                        return handler

                handler = make_handler()
                router.add_api_route(
                    route_path,
                    handler,
                    methods=[method],
                    **action_kwargs,
                )


def as_router(
    viewset_class: type[ViewSet],
    prefix: str = "",
    tags: list[str] | None = None,
    operations: str = "CRUDL",
) -> APIRouter:
    """
    将 ViewSet 转换为 FastAPI Router

    Args:
        viewset_class: ViewSet 类
        prefix: 路由前缀
        tags: OpenAPI 标签
        operations: 支持的操作 (C=Create, R=Retrieve, U=Update, D=Destroy, L=List)

    Returns:
        APIRouter 实例

    Example:
        class DemoViewSet(ModelViewSet):
            model = DemoModel

        router = as_router(DemoViewSet, prefix="/demos", tags=["Demo"])
    """
    router_builder = ViewSetRouter(
        viewset_class=viewset_class,
        prefix=prefix,
        tags=tags,
        operations=operations,
    )
    return router_builder.get_router()
