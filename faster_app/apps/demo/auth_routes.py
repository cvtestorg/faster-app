"""
权限和认证测试路由
"""

from faster_app.apps.demo.models import DemoModel
from faster_app.apps.demo.schemas import DemoCreate, DemoResponse, DemoUpdate
from faster_app.viewsets import (
    IsAdminUser,
    IsAuthenticated,
    JWTAuthentication,
    ModelViewSet,
    as_router,
)


class AuthDemoViewSet(ModelViewSet):
    """
    需要认证的 ViewSet - 测试权限功能

    所有操作都需要 JWT 认证
    """

    model = DemoModel
    serializer_class = DemoResponse
    create_serializer_class = DemoCreate
    update_serializer_class = DemoUpdate

    # 启用 JWT 认证
    authentication_classes = [JWTAuthentication]

    # 需要认证才能访问
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """自定义查询集"""
        return self.model.all()


class AdminDemoViewSet(ModelViewSet):
    """
    需要管理员权限的 ViewSet - 测试管理员权限

    所有操作都需要管理员权限
    """

    model = DemoModel
    serializer_class = DemoResponse
    create_serializer_class = DemoCreate
    update_serializer_class = DemoUpdate

    # 启用 JWT 认证
    authentication_classes = [JWTAuthentication]

    # 需要管理员权限
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """自定义查询集"""
        return self.model.all()


# 需要认证的路由
auth_demo_router = as_router(
    AuthDemoViewSet,
    prefix="/auth-demos",
    tags=["Auth Demo"],
)

# 需要管理员权限的路由
admin_demo_router = as_router(
    AdminDemoViewSet,
    prefix="/admin-demos",
    tags=["Admin Demo"],
)
