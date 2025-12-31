"""
Demo 路由 - 全面展示 ViewSet 特性

本文件展示了 ViewSet 系统的所有核心特性：
1. 基础 CRUD 操作
2. 认证和权限系统
3. 过滤和排序
4. 限流控制
5. 自定义 Action
6. 钩子函数
7. 组合使用
"""

from datetime import datetime

from fastapi import BackgroundTasks, Request

from faster_app.apps.demo.models import DemoModel
from faster_app.apps.demo.schemas import (
    BackgroundTaskRequest,
    DemoCreate,
    DemoResponse,
    DemoStatistics,
    DemoUpdate,
)
from faster_app.apps.demo.tasks import send_notification, write_log_to_file
from faster_app.exceptions import ConflictError, NotFoundError
from faster_app.settings import logger
from faster_app.utils.response import ApiResponse
from faster_app.viewsets import (
    AnonRateThrottle,
    FieldFilter,
    IsAdminUser,
    IsAuthenticated,
    IsOwnerOrReadOnly,
    JWTAuthentication,
    ModelViewSet,
    OrderingFilter,
    SearchFilter,
    SimpleRateThrottle,
    UserRateThrottle,
    action,
    as_router,
)


class DemoBasicViewSet(ModelViewSet):
    """
    Demo ViewSet - 基础 CRUD

    特性一: 基础 CRUD 操作

    展示 ViewSet 的基础功能，包括：
    - list() - 列表查询（支持分页）
    - create() - 创建
    - retrieve() - 单个查询
    - update() - 完整更新
    - partial_update() - 部分更新
    - destroy() - 删除
    """

    model = DemoModel
    serializer_class = DemoResponse
    create_serializer_class = DemoCreate
    update_serializer_class = DemoUpdate

    def get_queryset(self):
        """自定义查询集"""
        return self.model.all()


demo_basic_router = as_router(
    DemoBasicViewSet,
    prefix="/demos",
    tags=["Demo - 基础 CRUD"],
)


class DemoAuthViewSet(ModelViewSet):
    """
    Demo ViewSet - 认证示例

    特性二: 认证和权限系统

    所有操作都需要 JWT 认证。
    """

    model = DemoModel
    serializer_class = DemoResponse
    create_serializer_class = DemoCreate
    update_serializer_class = DemoUpdate

    # 配置认证类
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """自定义查询集"""
        return self.model.all()


class DemoOwnerViewSet(ModelViewSet):
    """
    Demo ViewSet - 所有者权限示例

    特性二: 认证和权限系统

    只有所有者可以修改和删除自己的记录，其他人只能查看。
    """

    model = DemoModel
    serializer_class = DemoResponse
    create_serializer_class = DemoCreate
    update_serializer_class = DemoUpdate

    # 配置认证和权限
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        """自定义查询集"""
        return self.model.all()

    @action(detail=True, methods=["POST"])
    async def activate(self, request: Request, pk: str):
        """
        激活操作 - 需要所有者权限

        访问路径: POST /demos-owner/{pk}/activate
        """
        instance = await self.get_object(pk)
        if not instance:
            raise NotFoundError(message="记录不存在", data={"pk": pk})
        instance.status = 1
        await instance.save()
        return await DemoResponse.from_orm_model(instance)


class DemoAdminViewSet(ModelViewSet):
    """
    Demo ViewSet - 管理员权限示例

    特性二: 认证和权限系统

    只有管理员可以执行所有操作。
    """

    model = DemoModel
    serializer_class = DemoResponse
    create_serializer_class = DemoCreate
    update_serializer_class = DemoUpdate

    # 配置认证和权限
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        """管理员可以查看所有记录"""
        return self.model.all()

    @action(detail=False, methods=["GET"])
    async def admin_stats(self, request: Request):
        """
        管理员统计 - 只有管理员可以访问

        访问路径: GET /demos-admin/admin-stats
        """
        total = await self.model.all().count()
        active = await self.model.filter(status=1).count()
        return {
            "total": total,
            "active": active,
            "inactive": total - active,
            "message": "管理员专用统计",
        }


demo_auth_router = as_router(
    DemoAuthViewSet,
    prefix="/demos-auth",
    tags=["Demo - 认证示例"],
)

demo_owner_router = as_router(
    DemoOwnerViewSet,
    prefix="/demos-owner",
    tags=["Demo - 所有者权限"],
)

demo_admin_router = as_router(
    DemoAdminViewSet,
    prefix="/demos-admin",
    tags=["Demo - 管理员权限"],
)


class DemoFilterViewSet(ModelViewSet):
    """
    Demo ViewSet - 过滤和排序示例

    特性三: 过滤和排序

    展示如何使用过滤和排序功能。
    """

    model = DemoModel
    serializer_class = DemoResponse
    create_serializer_class = DemoCreate
    update_serializer_class = DemoUpdate

    # 配置过滤后端
    filter_backends = [SearchFilter, OrderingFilter, FieldFilter]

    # 搜索字段配置
    search_fields = ["name"]  # 支持在 name 字段中搜索

    # 排序字段配置
    ordering_fields = ["created_at", "updated_at", "status", "name"]
    ordering = ["-created_at"]  # 默认按创建时间倒序

    # 字段过滤配置
    filter_fields = {
        "status": "exact",  # 精确匹配: ?status=1
        "name": "icontains",  # 包含匹配: ?name=test
    }

    def get_queryset(self):
        """自定义查询集"""
        return self.model.all()


class DemoAdvancedFilterViewSet(ModelViewSet):
    """
    Demo ViewSet - 高级过滤示例

    特性三: 过滤和排序

    展示更复杂的过滤配置，包括多种查询类型和字段前缀。
    """

    model = DemoModel
    serializer_class = DemoResponse

    # 配置多个过滤后端
    filter_backends = [SearchFilter, OrderingFilter, FieldFilter]

    # 搜索字段配置（支持字段前缀）
    search_fields = [
        "name",  # 默认：包含匹配
        "^id",  # ^ 前缀：精确匹配
        "=status",  # = 前缀：相等匹配
    ]

    # 排序字段配置
    ordering_fields = ["created_at", "updated_at", "status", "name"]
    ordering = ["-created_at", "-updated_at"]  # 默认多字段排序

    # 字段过滤配置（支持多种查询类型）
    filter_fields = {
        "status": "exact",  # 精确匹配: ?status=1
        "name": "icontains",  # 包含匹配: ?name=test
        "created_at": "gte",  # 大于等于: ?created_at=2024-01-01
        "updated_at": "lte",  # 小于等于: ?updated_at=2024-12-31
        "id": "in",  # 在列表中: ?id=1,2,3
    }

    def get_queryset(self):
        """自定义查询集"""
        return self.model.all()

    @action(detail=False, methods=["GET"])
    async def filtered_stats(self, request: Request):
        """
        过滤后的统计 - 展示如何使用过滤后的查询集

        访问路径: GET /demos-filter-advanced/filtered-stats?status=1&name=test
        """
        # 获取基础查询集
        queryset = self.get_queryset()
        # 应用过滤
        queryset = await self.filter_queryset(queryset, request)

        total = await queryset.count()
        active = await queryset.filter(status=1).count()

        return {
            "total": total,
            "active": active,
            "inactive": total - active,
            "message": "基于过滤条件的统计",
        }


demo_filter_router = as_router(
    DemoFilterViewSet,
    prefix="/demos-filter",
    tags=["Demo - 过滤排序"],
)

demo_advanced_filter_router = as_router(
    DemoAdvancedFilterViewSet,
    prefix="/demos-filter-advanced",
    tags=["Demo - 高级过滤"],
)


class DemoThrottleViewSet(ModelViewSet):
    """
    Demo ViewSet - 限流示例

    特性四: 限流控制

    对用户和匿名用户分别进行限流。
    默认从 settings.THROTTLE_RATES 读取速率配置。
    """

    model = DemoModel
    serializer_class = DemoResponse
    create_serializer_class = DemoCreate
    update_serializer_class = DemoUpdate

    # 配置限流类（使用配置文件中的默认速率）
    throttle_classes = [
        UserRateThrottle(),  # 从配置读取 "user" 速率（默认 "100/hour"）
        AnonRateThrottle(),  # 从配置读取 "anon" 速率（默认 "20/hour"）
    ]

    def get_queryset(self):
        """自定义查询集"""
        return self.model.all()


class DemoScopedThrottleViewSet(ModelViewSet):
    """
    Demo ViewSet - 作用域限流示例

    特性四: 限流控制

    使用作用域限流，从配置中读取特定作用域的速率。
    """

    model = DemoModel
    serializer_class = DemoResponse

    # 配置限流类（使用作用域配置）
    throttle_classes = [SimpleRateThrottle()]
    throttle_scope = "demo"  # 从 settings.THROTTLE_RATES["demo"] 读取速率

    def get_queryset(self):
        """自定义查询集"""
        return self.model.all()

    @action(detail=False, methods=["GET"])
    async def stats(self, request: Request):
        """
        统计操作 - 使用作用域限流

        访问路径: GET /demos-throttle-scoped/stats
        """
        total = await self.model.all().count()
        active = await self.model.filter(status=1).count()
        return {
            "total": total,
            "active": active,
            "inactive": total - active,
        }


class DemoCustomThrottleViewSet(ModelViewSet):
    """
    Demo ViewSet - 自定义限流示例

    特性四: 限流控制

    直接指定限流速率，覆盖配置。
    """

    model = DemoModel
    serializer_class = DemoResponse

    # 直接指定速率（覆盖配置）
    throttle_classes = [SimpleRateThrottle(rate="100/hour")]

    def get_queryset(self):
        """自定义查询集"""
        return self.model.all()


demo_throttle_router = as_router(
    DemoThrottleViewSet,
    prefix="/demos-throttle",
    tags=["Demo - 限流示例"],
)

demo_scoped_throttle_router = as_router(
    DemoScopedThrottleViewSet,
    prefix="/demos-throttle-scoped",
    tags=["Demo - 作用域限流"],
)

demo_custom_throttle_router = as_router(
    DemoCustomThrottleViewSet,
    prefix="/demos-throttle-custom",
    tags=["Demo - 自定义限流"],
)


class DemoActionViewSet(ModelViewSet):
    """
    Demo ViewSet - 自定义 Action 示例

    特性五: 自定义 Action

    展示如何使用 @action 装饰器定义自定义路由。
    """

    model = DemoModel
    serializer_class = DemoResponse
    create_serializer_class = DemoCreate
    update_serializer_class = DemoUpdate

    def get_queryset(self):
        """自定义查询集"""
        return self.model.all()

    @action(detail=False, methods=["GET"], response_model=DemoStatistics)
    async def statistics(self, request: Request):
        """
        统计信息 - 列表级别的 action

        访问路径: GET /demos-action/statistics
        """
        total = await self.model.all().count()
        active = await self.model.filter(status=1).count()
        inactive = await self.model.filter(status=0).count()

        return DemoStatistics(
            total=total,
            active=active,
            inactive=inactive,
        )

    @action(detail=True, methods=["POST"])
    async def activate(self, request: Request, pk: str):
        """
        激活操作 - 对象级别的 action

        访问路径: POST /demos-action/{pk}/activate
        """
        instance = await self.get_object(pk)
        if not instance:
            raise NotFoundError(message="记录不存在", data={"pk": pk})
        instance.status = 1
        await instance.save()
        return await DemoResponse.from_orm_model(instance)

    @action(detail=True, methods=["POST"])
    async def deactivate(self, request: Request, pk: str):
        """
        停用操作 - 对象级别的 action

        访问路径: POST /demos-action/{pk}/deactivate
        """
        instance = await self.get_object(pk)
        if not instance:
            raise NotFoundError(message="记录不存在", data={"pk": pk})
        instance.status = 0
        await instance.save()
        return await DemoResponse.from_orm_model(instance)

    @action(detail=False, methods=["POST"])
    async def batch_create(self, request: Request, items_data: list[DemoCreate]):
        """
        批量创建 - 列表级别的 action

        访问路径: POST /demos-action/batch-create
        """
        created_records = []
        for create_data in items_data:
            instance = await self.perform_create(create_data)
            created_records.append(instance)

        return ApiResponse.success(
            data={"count": len(created_records)},
            message=f"成功创建 {len(created_records)} 条记录",
        )

    @action(detail=False, methods=["POST"])
    async def background_task(
        self,
        request: Request,
        task_request: BackgroundTaskRequest,
        background_tasks: BackgroundTasks,
    ):
        """
        后台任务 - 展示 FastAPI BackgroundTasks 的使用

        访问路径: POST /demos-action/background-task
        """
        background_tasks.add_task(
            send_notification, email=task_request.email, message=task_request.message
        )
        background_tasks.add_task(
            write_log_to_file, task_id=task_request.task_id, data=task_request.model_dump()
        )

        logger.info("[主请求] 已添加后台任务, 立即返回响应")

        return ApiResponse.success(
            data={
                "task_id": task_request.task_id,
                "status": "processing",
                "message": "任务已提交, 正在后台处理",
                "submitted_at": datetime.now().isoformat(),
            },
            message="后台任务已启动",
        )


demo_action_router = as_router(
    DemoActionViewSet,
    prefix="/demos-action",
    tags=["Demo - 自定义 Action"],
)


class DemoHookViewSet(ModelViewSet):
    """
    Demo ViewSet - 钩子函数示例

    特性六: 钩子函数

    展示如何使用钩子函数在 CRUD 操作前后执行自定义逻辑。
    """

    model = DemoModel
    serializer_class = DemoResponse
    create_serializer_class = DemoCreate
    update_serializer_class = DemoUpdate

    def get_queryset(self):
        """自定义查询集"""
        return self.model.all()

    async def perform_create_hook(self, create_data: DemoCreate, request: Request) -> DemoCreate:
        """
        创建前钩子 - 在创建记录前执行

        可以用于：
        - 数据验证
        - 数据转换
        - 业务逻辑检查
        """
        # 检查名称是否重复
        existing = await self.model.filter(name=create_data.name).first()
        if existing:
            raise ConflictError(message="名称已存在", data={"name": create_data.name})

        logger.info(f"[创建前] 准备创建记录: {create_data.name}")
        return create_data

    async def perform_create_after_hook(self, instance: DemoModel, request: Request) -> DemoModel:
        """
        创建后钩子 - 在创建记录后执行

        可以用于：
        - 发送通知
        - 记录日志
        - 触发其他操作
        """
        logger.info(f"[创建后] 已创建记录: {instance.id} - {instance.name}")
        return instance

    async def perform_update_hook(
        self, instance: DemoModel, update_data: DemoUpdate, request: Request
    ) -> DemoUpdate:
        """
        更新前钩子 - 在更新记录前执行

        可以用于：
        - 权限检查
        - 数据验证
        - 记录变更历史
        """
        logger.info(f"[更新前] 准备更新记录: {instance.id}")
        return update_data

    async def perform_update_after_hook(self, instance: DemoModel, request: Request) -> DemoModel:
        """
        更新后钩子 - 在更新记录后执行

        可以用于：
        - 发送通知
        - 记录日志
        - 缓存更新
        """
        logger.info(f"[更新后] 已更新记录: {instance.id} - {instance.name}")
        return instance

    async def perform_destroy_hook(self, instance: DemoModel, request: Request) -> bool:
        """
        删除前钩子 - 在删除记录前执行

        返回 False 可以阻止删除。

        可以用于：
        - 检查关联数据
        - 软删除
        - 权限检查
        """
        # 检查是否可以删除（例如：检查关联数据）
        logger.info(f"[删除前] 准备删除记录: {instance.id}")
        return True

    async def perform_destroy_after_hook(self, instance: DemoModel, request: Request) -> None:
        """
        删除后钩子 - 在删除记录后执行

        可以用于：
        - 清理关联数据
        - 记录日志
        - 发送通知
        """
        logger.info(f"[删除后] 已删除记录: {instance.id}")


demo_hook_router = as_router(
    DemoHookViewSet,
    prefix="/demos-hook",
    tags=["Demo - 钩子函数"],
)


class DemoCompleteViewSet(ModelViewSet):
    """
    Demo ViewSet - 完整功能示例

    特性七: 组合使用

    组合使用所有 ViewSet 特性：
    - 认证和权限
    - 过滤和排序
    - 限流
    - 自定义 Action
    - 钩子函数
    """

    model = DemoModel
    serializer_class = DemoResponse
    create_serializer_class = DemoCreate
    update_serializer_class = DemoUpdate

    # 认证和权限
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # 过滤和排序
    filter_backends = [SearchFilter, OrderingFilter, FieldFilter]
    search_fields = ["name"]
    ordering_fields = ["created_at", "updated_at", "status", "name"]
    ordering = ["-created_at"]
    filter_fields = {
        "status": "exact",
        "name": "icontains",
    }

    # 限流
    throttle_classes = [UserRateThrottle(), AnonRateThrottle()]

    def get_queryset(self):
        """自定义查询集"""
        return self.model.all()

    async def perform_create_hook(self, create_data: DemoCreate, request: Request) -> DemoCreate:
        """创建前钩子 - 业务逻辑检查"""
        existing = await self.model.filter(name=create_data.name).first()
        if existing:
            raise ConflictError(message="名称已存在", data={"name": create_data.name})
        return create_data

    async def perform_create_after_hook(self, instance: DemoModel, request: Request) -> DemoModel:
        """创建后钩子 - 记录日志"""
        logger.info(f"创建 Demo: {instance.id} - {instance.name}")
        return instance

    @action(detail=False, methods=["GET"], response_model=DemoStatistics)
    async def statistics(self, request: Request):
        """
        统计信息 - 自定义 action

        访问路径: GET /demos-complete/statistics
        """
        queryset = self.get_queryset()
        # 应用过滤
        queryset = await self.filter_queryset(queryset, request)

        total = await queryset.count()
        active = await queryset.filter(status=1).count()
        inactive = total - active

        return DemoStatistics(
            total=total,
            active=active,
            inactive=inactive,
        )

    @action(detail=True, methods=["POST"])
    async def activate(self, request: Request, pk: str):
        """
        激活操作 - 自定义 action

        访问路径: POST /demos-complete/{pk}/activate
        """
        instance = await self.get_object(pk)
        if not instance:
            raise NotFoundError(message="记录不存在", data={"pk": pk})
        instance.status = 1
        await instance.save()
        return await DemoResponse.from_orm_model(instance)


demo_complete_router = as_router(
    DemoCompleteViewSet,
    prefix="/demos-complete",
    tags=["Demo - 完整功能示例"],
)
