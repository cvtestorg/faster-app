# CRUD 工具类改造为 DRF 风格方案

## 一、改造目标

将当前的 `CRUDBase` 和 `CRUDRouter` 改造为类似 Django REST Framework (DRF) 的功能,提供：

1. **ViewSet 模式** - 将 CRUD 操作组织在一起
2. **权限系统** - 细粒度的权限控制
3. **认证系统** - 用户认证支持
4. **过滤和排序** - 灵活的查询能力
5. **限流** - 请求频率控制
6. **Action 装饰器** - 自定义操作
7. **序列化器增强** - 更强大的数据验证和转换

## 二、架构设计

### 2.1 核心组件

```
faster_app/viewsets/
├── __init__.py
├── base.py              # ViewSet 基类
├── mixins.py            # Mixin 类(List, Create, Retrieve, Update, Destroy)
├── permissions.py        # 权限系统
├── authentication.py     # 认证系统
├── filters.py           # 过滤系统
├── pagination.py        # 分页增强
└── throttling.py        # 限流系统
```

### 2.2 设计原则

1. **向后兼容** - 保留现有 `CRUDBase` 和 `CRUDRouter`,新增 ViewSet
2. **渐进式增强** - 分阶段实现,逐步迁移
3. **约定优于配置** - 提供合理的默认值
4. **可扩展性** - 支持自定义和扩展

## 三、详细设计方案

### 3.1 ViewSet 基类

**核心概念**: ViewSet 将 CRUD 操作组织在一起,类似于 DRF 的 ViewSet

```python
class ViewSet[ModelType, CreateSchemaType, UpdateSchemaType, ResponseSchemaType]:
    """
    ViewSet 基类 - 类似 DRF 的 ViewSet

    提供标准的 CRUD 操作,支持权限、认证、过滤等
    """

    # 模型和 Schema
    model: type[ModelType]
    schema: type[ResponseSchemaType]
    create_schema: type[CreateSchemaType]
    update_schema: type[UpdateSchemaType]

    # 权限和认证
    permission_classes: list[type[BasePermission]]
    authentication_classes: list[type[BaseAuthentication]]

    # 过滤和排序
    filter_backends: list[type[BaseFilterBackend]]
    ordering_fields: list[str]
    search_fields: list[str]

    # 分页
    pagination_class: type[BasePagination] | None

    # 限流
    throttle_classes: list[type[BaseThrottle]]

    # 查询集
    queryset: QuerySet | None

    def get_queryset(self) -> QuerySet:
        """获取查询集,可被子类重写"""
        pass

    def get_schema(self, action: str) -> type:
        """根据操作获取 Schema 类"""
        pass

    def get_permissions(self) -> list[BasePermission]:
        """获取权限实例"""
        pass

    def check_permissions(self, request, action: str) -> None:
        """检查权限"""
        pass
```

### 3.2 Mixin 类

**设计模式**: 使用 Mixin 提供可组合的操作

```python
class ListModelMixin:
    """列表查询 Mixin"""
    async def list(self, request, *args, **kwargs):
        pass

class CreateModelMixin:
    """创建 Mixin"""
    async def create(self, request, *args, **kwargs):
        pass

class RetrieveModelMixin:
    """单个查询 Mixin"""
    async def retrieve(self, request, *args, **kwargs):
        pass

class UpdateModelMixin:
    """更新 Mixin"""
    async def update(self, request, *args, **kwargs):
        async def partial_update(self, request, *args, **kwargs):
            pass

class DestroyModelMixin:
    """删除 Mixin"""
    async def destroy(self, request, *args, **kwargs):
        pass
```

### 3.3 权限系统

**设计模式**: 策略模式,支持多种权限类

```python
class BasePermission(ABC):
    """权限基类"""

    @abstractmethod
    async def has_permission(self, request, view) -> bool:
        """检查是否有权限执行操作"""
        pass

    @abstractmethod
    async def has_object_permission(self, request, view, obj) -> bool:
        """检查是否有权限操作特定对象"""
        pass

class AllowAny(BasePermission):
    """允许所有请求"""
    pass

class IsAuthenticated(BasePermission):
    """需要认证"""
    pass

class IsOwner(BasePermission):
    """检查是否是对象所有者"""
    pass

class IsAdminUser(BasePermission):
    """检查是否是管理员"""
    pass
```

### 3.4 认证系统

**设计模式**: 策略模式,支持多种认证方式

```python
class BaseAuthentication(ABC):
    """认证基类"""

    @abstractmethod
    async def authenticate(self, request) -> tuple[User, str] | None:
        """认证用户,返回 (user, token) 或 None"""
        pass

class JWTAuthentication(BaseAuthentication):
    """JWT 认证"""
    pass

class SessionAuthentication(BaseAuthentication):
    """Session 认证"""
    pass

class TokenAuthentication(BaseAuthentication):
    """Token 认证"""
    pass
```

### 3.5 过滤系统

**设计模式**: 责任链模式,支持多个过滤后端

```python
class BaseFilterBackend(ABC):
    """过滤后端基类"""

    @abstractmethod
    async def filter_queryset(self, request, queryset, view) -> QuerySet:
        """过滤查询集"""
        pass

class SearchFilter(BaseFilterBackend):
    """搜索过滤"""
    search_param = "search"
    search_fields: list[str] = []

    async def filter_queryset(self, request, queryset, view):
        # 实现搜索逻辑
        pass

class OrderingFilter(BaseFilterBackend):
    """排序过滤"""
    ordering_param = "ordering"
    ordering_fields: list[str] = []

    async def filter_queryset(self, request, queryset, view):
        # 实现排序逻辑
        pass

class DjangoFilterBackend(BaseFilterBackend):
    """类似 Django Filter 的过滤"""
    # 支持复杂的过滤条件
    pass
```

### 3.6 Action 装饰器

**核心功能**: 支持自定义操作,类似 DRF 的 `@action`

```python
def action(
    methods: list[str] | None = None,
    detail: bool = False,
    url_path: str | None = None,
    url_name: str | None = None,
    permission_classes: list[type[BasePermission]] | None = None,
    authentication_classes: list[type[BaseAuthentication]] | None = None,
    throttle_classes: list[type[BaseThrottle]] | None = None,
    **kwargs
):
    """
    装饰器：定义自定义操作

    Args:
        methods: HTTP 方法列表,如 ["GET", "POST"]
        detail: 是否是针对单个对象的操作
        url_path: 自定义 URL 路径
        url_name: URL 名称
        permission_classes: 权限类列表
        authentication_classes: 认证类列表
        throttle_classes: 限流类列表
    """
    pass
```

## 四、实现方案

### 4.1 阶段一：基础 ViewSet(核心功能)

**目标**: 实现基本的 ViewSet 和 Mixin,保持向后兼容

**实现内容**:

1. 创建 `ViewSet` 基类
2. 实现 Mixin 类(List, Create, Retrieve, Update, Destroy)
3. 创建 `ModelViewSet` 组合类
4. 实现路由注册机制

**使用示例**:

```python
from faster_app.viewsets import ModelViewSet
from faster_app.apps.demo.models import DemoModel
from faster_app.apps.demo.schemas import DemoCreate, DemoUpdate, DemoResponse

class DemoViewSet(ModelViewSet):
    model = DemoModel
    schema = DemoResponse
    create_schema = DemoCreate
    update_schema = DemoUpdate

    # 自定义查询集
    def get_queryset(self):
        return self.model.filter(status=1)

    # 自定义操作
    @action(detail=True, methods=["POST"])
    async def activate(self, request, pk):
        """激活操作"""
        instance = await self.get_object()
        instance.status = 1
        await instance.save()
        return await self.get_serializer(instance)

# 注册路由
router = DemoViewSet.as_router(prefix="/demos", tags=["Demo"])
```

### 4.2 阶段二：权限和认证

**目标**: 添加权限和认证支持

**实现内容**:

1. 实现权限基类和常用权限类
2. 实现认证基类和常用认证类
3. 在 ViewSet 中集成权限和认证检查

**使用示例**:

```python
from faster_app.viewsets import ModelViewSet
from faster_app.viewsets.permissions import IsAuthenticated, IsOwner
from faster_app.viewsets.authentication import JWTAuthentication

class DemoViewSet(ModelViewSet):
    model = DemoModel
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    # 对象级权限
    def get_object_permission_classes(self):
        return [IsOwner]
```

### 4.3 阶段三：过滤和排序

**目标**: 添加灵活的过滤和排序能力

**实现内容**:

1. 实现过滤后端基类
2. 实现搜索、排序、字段过滤等后端
3. 在 ViewSet 中集成过滤

**使用示例**:

```python
from faster_app.viewsets import ModelViewSet
from faster_app.viewsets.filters import SearchFilter, OrderingFilter

class DemoViewSet(ModelViewSet):
    model = DemoModel
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]  # 默认排序
```

### 4.4 阶段四：限流和缓存

**目标**: 添加限流和缓存支持

**实现内容**:

1. 实现限流基类和常用限流类
2. 实现缓存装饰器
3. 在 ViewSet 中集成限流

**使用示例**:

```python
from faster_app.viewsets import ModelViewSet
from faster_app.viewsets.throttling import UserRateThrottle, AnonRateThrottle

class DemoViewSet(ModelViewSet):
    model = DemoModel
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    throttle_scope = "demo"  # 限流作用域
```

## 五、迁移策略

### 5.1 向后兼容

1. **保留现有 API**: `CRUDBase` 和 `CRUDRouter` 继续可用
2. **渐进式迁移**: 新功能使用 ViewSet,旧代码逐步迁移
3. **适配器模式**: 提供适配器让 ViewSet 兼容现有代码

### 5.2 迁移步骤

1. **第一步**: 实现基础 ViewSet,不影响现有代码
2. **第二步**: 在新功能中使用 ViewSet
3. **第三步**: 逐步迁移现有代码到 ViewSet
4. **第四步**: 标记旧 API 为 deprecated,提供迁移指南

## 六、技术细节

### 6.1 查询集增强

```python
class QuerySet:
    """增强的查询集,支持链式调用"""

    def filter(self, **kwargs):
        """过滤"""
        pass

    def exclude(self, **kwargs):
        """排除"""
        pass

    def order_by(self, *fields):
        """排序"""
        pass

    def select_related(self, *fields):
        """关联查询"""
        pass

    def prefetch_related(self, *fields):
        """预加载关联"""
        pass

    def annotate(self, **kwargs):
        """注解"""
        pass

    def aggregate(self, **kwargs):
        """聚合"""
        pass
```

### 6.2 序列化器增强

```python
class Serializer(BaseModel):
    """增强的序列化器基类"""

    @classmethod
    def from_orm(cls, obj):
        """从 ORM 对象创建"""
        pass

    def to_representation(self):
        """转换为表示形式"""
        pass

    def validate(self, attrs):
        """验证数据"""
        pass

    def create(self, validated_data):
        """创建实例"""
        pass

    def update(self, instance, validated_data):
        """更新实例"""
        pass
```

### 6.3 路由注册

```python
class ViewSet:
    @classmethod
    def as_router(
        cls,
        prefix: str = "",
        tags: list[str] | None = None,
        operations: str = "CRUDL",
    ) -> APIRouter:
        """
        将 ViewSet 转换为 Router

        Args:
            prefix: 路由前缀
            tags: OpenAPI 标签
            operations: 支持的操作 (CRUDL)
        """
        pass
```

## 七、优势分析

### 7.1 相比当前实现的优势

1. **更灵活**: ViewSet 模式更灵活,支持自定义操作
2. **更安全**: 内置权限和认证系统
3. **更强大**: 过滤、排序、限流等高级功能
4. **更标准**: 符合 RESTful API 最佳实践
5. **更易维护**: 代码组织更清晰,职责分离

### 7.2 相比 DRF 的优势

1. **异步支持**: 原生支持异步操作
2. **类型安全**: 完整的类型提示
3. **性能更好**: FastAPI 的高性能
4. **现代化**: 使用 Pydantic v2 等现代库

## 八、实施建议

### 8.1 优先级

1. **P0 (必须)**: 基础 ViewSet 和 Mixin
2. **P1 (重要)**: 权限和认证系统
3. **P2 (有用)**: 过滤和排序
4. **P3 (可选)**: 限流和缓存

### 8.2 开发顺序

1. 先实现基础 ViewSet,验证可行性
2. 添加权限和认证,确保安全性
3. 实现过滤和排序,提升查询能力
4. 最后添加限流和缓存,优化性能

### 8.3 测试策略

1. **单元测试**: 每个组件独立测试
2. **集成测试**: ViewSet 整体功能测试
3. **兼容性测试**: 确保向后兼容
4. **性能测试**: 对比新旧实现的性能

## 九、参考资源

- Django REST Framework 文档: https://www.django-rest-framework.org/
- FastAPI 最佳实践: https://fastapi.tiangolo.com/
- RESTful API 设计指南: https://restfulapi.net/
