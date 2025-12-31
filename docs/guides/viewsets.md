# ViewSet 使用指南

## 概述

ViewSet 提供了类似 Django REST Framework (DRF) 的功能，用于快速构建 RESTful API。它使用组合模式（Mixin）和策略模式，提供了灵活且强大的 API 构建能力。

## 核心概念

### ViewSet

ViewSet 是一个类，它将一组相关的 CRUD 操作组织在一起。它类似于 DRF 的 ViewSet，但针对 FastAPI 和异步操作进行了优化。

### Mixin

Mixin 类提供可组合的功能：
- `ListModelMixin` - 列表查询
- `CreateModelMixin` - 创建
- `RetrieveModelMixin` - 单个查询
- `UpdateModelMixin` - 更新
- `DestroyModelMixin` - 删除

### 预定义的 ViewSet

- `ModelViewSet` - 完整的 CRUD 操作（组合所有 Mixin）
- `ReadOnlyModelViewSet` - 只读操作（列表和单个查询）

## 快速开始

### 基础用法

```python
from faster_app.viewsets import ModelViewSet, as_router
from faster_app.apps.demo.models import DemoModel
from faster_app.apps.demo.schemas import DemoCreate, DemoUpdate, DemoResponse

class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse
    create_serializer_class = DemoCreate
    update_serializer_class = DemoUpdate

# 注册路由
router = as_router(DemoViewSet, prefix="/demos", tags=["Demo"])
# 或使用类方法
router = DemoViewSet.as_router(prefix="/demos", tags=["Demo"])
```

### 自定义查询集

```python
class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse

    def get_queryset(self):
        """只返回激活的记录"""
        return self.model.filter(status=1)
```

### 自定义操作（Action）

使用 `@action` 装饰器定义自定义操作：

```python
from faster_app.viewsets import ModelViewSet, action
from fastapi import Request

class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse

    @action(detail=True, methods=["POST"])
    async def activate(self, request: Request, pk: str):
        """激活操作 - 针对单个对象"""
        instance = await self.get_object(pk)
        if not instance:
            raise NotFoundError(message="记录不存在")
        instance.status = 1
        await instance.save()
        serializer_class = self.get_serializer_class("retrieve")
        return await serializer_class.from_tortoise_orm(instance)

    @action(detail=False, methods=["GET"])
    async def stats(self, request: Request):
        """统计操作 - 列表级别"""
        total = await self.model.all().count()
        active = await self.model.filter(status=1).count()
        return {
            "total": total,
            "active": active,
            "inactive": total - active,
        }
```

**路由生成**:
- `POST /demos/{pk}/activate` - 激活操作
- `GET /demos/stats` - 统计操作

### 自定义钩子函数

```python
class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse

    async def perform_create_hook(self, create_data, request):
        """创建前钩子"""
        # 可以修改创建数据
        create_data.name = create_data.name.upper()
        return create_data

    async def perform_create_after_hook(self, instance, request):
        """创建后钩子"""
        # 可以执行额外操作，如发送通知
        await send_notification(f"创建了 {instance.name}")
        return instance
```

## 操作控制

使用 `operations` 参数控制支持的操作：

```python
# 只支持查询
router = DemoViewSet.as_router(
    prefix="/demos",
    operations="RL"  # R=Retrieve, L=List
)

# 只支持创建和列表
router = DemoViewSet.as_router(
    prefix="/demos",
    operations="CL"  # C=Create, L=List
)
```

## 与现有 CRUD 工具的对比

### 当前方式（CRUDRouter）

```python
from faster_app.utils.crud import CRUDRouter

router = CRUDRouter(
    model=DemoModel,
    prefix="/demos",
    tags=["Demo"]
).get_router()
```

### ViewSet 方式

```python
from faster_app.viewsets import ModelViewSet, as_router

class DemoViewSet(ModelViewSet):
    model = DemoModel

router = DemoViewSet.as_router(prefix="/demos", tags=["Demo"])
```

### 优势对比

| 特性 | CRUDRouter | ViewSet |
|------|------------|---------|
| 基础 CRUD | ✅ | ✅ |
| 自定义操作 | ❌ | ✅ (@action) |
| 钩子函数 | ✅ | ✅ |
| 查询集自定义 | ❌ | ✅ |
| 权限控制 | ❌ | 🔜 (阶段二) |
| 过滤排序 | ❌ | 🔜 (阶段三) |

## 最佳实践

1. **使用 ViewSet 进行新开发**：新功能优先使用 ViewSet
2. **保持向后兼容**：现有代码继续使用 CRUDRouter，逐步迁移
3. **合理使用 Action**：将相关操作组织在同一个 ViewSet 中
4. **自定义查询集**：使用 `get_queryset()` 控制数据访问范围

## 迁移指南

### 从 CRUDRouter 迁移到 ViewSet

**之前**:
```python
demo_router = CRUDRouter(
    model=DemoModel,
    create_schema=DemoCreate,
    update_schema=DemoUpdate,
    prefix="/demos",
    tags=["Demo"]
).get_router()
```

**之后**:
```python
class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse
    create_serializer_class = DemoCreate
    update_serializer_class = DemoUpdate

router = DemoViewSet.as_router(prefix="/demos", tags=["Demo"])
```

## 权限和认证

### 权限系统

ViewSet 支持灵活的权限控制，包括操作级权限和对象级权限。

#### 内置权限类

- `AllowAny` - 允许所有请求（默认）
- `IsAuthenticated` - 需要认证
- `IsAdminUser` - 需要管理员权限
- `IsOwner` - 检查是否是对象所有者
- `IsOwnerOrReadOnly` - 所有者可以所有操作，其他用户只能读取

#### 使用权限

```python
from faster_app.viewsets import ModelViewSet, IsAuthenticated, IsOwner

class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse
    
    # 设置权限类
    permission_classes = [IsAuthenticated]
```

#### 对象级权限

```python
from faster_app.viewsets import ModelViewSet, IsOwnerOrReadOnly

class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse
    
    # 所有者可以所有操作，其他用户只能读取
    permission_classes = [IsOwnerOrReadOnly]
```

### 认证系统

ViewSet 支持多种认证方式。

#### 内置认证类

- `NoAuthentication` - 不进行认证（默认）
- `JWTAuthentication` - JWT 认证
- `TokenAuthentication` - Token 认证
- `SessionAuthentication` - Session 认证

#### 使用认证

```python
from faster_app.viewsets import ModelViewSet, JWTAuthentication, IsAuthenticated

class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse
    
    # 设置认证和权限
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
```

#### JWT 认证示例

```python
from faster_app.viewsets import ModelViewSet, JWTAuthentication, IsAuthenticated

class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # 认证后可以访问 request.state.user
        return self.model.all()
```

### 自定义权限

```python
from faster_app.viewsets import BasePermission
from fastapi import Request

class IsOwnerOrAdmin(BasePermission):
    """所有者或管理员"""
    
    async def has_permission(self, request: Request, view) -> bool:
        return hasattr(request.state, "user") and request.state.user is not None
    
    async def has_object_permission(self, request: Request, view, obj) -> bool:
        user = request.state.user
        # 检查是否是管理员
        if hasattr(user, "is_admin") and user.is_admin:
            return True
        # 检查是否是所有者
        if hasattr(obj, "owner_id"):
            return obj.owner_id == user.id
        return False
```

### 自定义认证

```python
from faster_app.viewsets import BaseAuthentication
from fastapi import Request

class CustomAuthentication(BaseAuthentication):
    """自定义认证"""
    
    async def authenticate(self, request: Request) -> tuple[Any, str] | None:
        # 实现认证逻辑
        token = request.headers.get("X-Custom-Token")
        if token:
            # 验证 token 并返回用户
            user = await verify_token(token)
            if user:
                return (user, token)
        return None
```

## 过滤和排序

### 过滤系统

ViewSet 支持灵活的查询过滤，包括搜索、排序、字段过滤等。

#### 内置过滤后端

- `SearchFilter` - 搜索过滤（多字段搜索）
- `OrderingFilter` - 排序过滤
- `FieldFilter` - 字段过滤（精确匹配、范围查询等）
- `DjangoFilterBackend` - Django Filter 风格的过滤

#### 使用过滤

```python
from faster_app.viewsets import ModelViewSet, SearchFilter, OrderingFilter, FieldFilter

class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse
    
    # 配置过滤后端
    filter_backends = [SearchFilter, OrderingFilter, FieldFilter]
    
    # 搜索字段配置
    search_fields = ["name", "description"]
    
    # 排序字段配置
    ordering_fields = ["created_at", "updated_at", "name"]
    ordering = ["-created_at"]  # 默认排序
    
    # 字段过滤配置
    filter_fields = {
        "status": "exact",  # 精确匹配
        "name": "icontains",  # 包含匹配
    }
```

#### 搜索过滤

```python
class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse
    
    filter_backends = [SearchFilter]
    search_fields = ["name", "description"]
```

**使用方式**:
- `GET /demos/?search=test` - 在 name 和 description 中搜索 "test"

**字段前缀**:
- `name` - 默认：包含匹配（不区分大小写）
- `^name` - 精确匹配
- `=name` - 相等匹配
- `@name` - 全文搜索（需要数据库支持）

#### 排序过滤

```python
class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse
    
    filter_backends = [OrderingFilter]
    ordering_fields = ["created_at", "updated_at", "name"]
    ordering = ["-created_at"]  # 默认排序
```

**使用方式**:
- `GET /demos/?ordering=created_at` - 按创建时间升序
- `GET /demos/?ordering=-created_at` - 按创建时间倒序（- 前缀表示降序）
- `GET /demos/?ordering=-created_at,name` - 多字段排序

#### 字段过滤

```python
class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse
    
    filter_backends = [FieldFilter]
    filter_fields = {
        "status": "exact",  # 精确匹配: ?status=1
        "name": "icontains",  # 包含匹配: ?name=test
        "created_at": "gte",  # 大于等于: ?created_at=2024-01-01
        "updated_at": "lte",  # 小于等于: ?updated_at=2024-12-31
        "id": "in",  # 在列表中: ?id=1,2,3
    }
```

**支持的查询类型**:
- `exact` - 精确匹配
- `icontains` - 包含匹配（不区分大小写）
- `gt` - 大于
- `gte` - 大于等于
- `lt` - 小于
- `lte` - 小于等于
- `in` - 在列表中（逗号分隔）
- `isnull` - 是否为空

#### 组合使用

```python
class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse
    
    filter_backends = [SearchFilter, OrderingFilter, FieldFilter]
    search_fields = ["name"]
    ordering_fields = ["created_at", "name"]
    filter_fields = {"status": "exact"}
```

**使用方式**:
- `GET /demos/?search=test&ordering=-created_at&status=1` - 组合使用多个过滤条件

### 自定义过滤后端

```python
from faster_app.viewsets import BaseFilterBackend
from fastapi import Request

class CustomFilter(BaseFilterBackend):
    """自定义过滤后端"""
    
    async def filter_queryset(self, request: Request, queryset, view):
        # 实现自定义过滤逻辑
        custom_param = request.query_params.get("custom")
        if custom_param:
            queryset = queryset.filter(custom_field=custom_param)
        return queryset
```

## 限流和缓存

### 限流系统

ViewSet 支持请求频率控制，防止 API 被滥用。

#### 内置限流类

- `NoThrottle` - 不限流（默认）
- `SimpleRateThrottle` - 简单速率限流
- `UserRateThrottle` - 用户限流（对已认证用户）
- `AnonRateThrottle` - 匿名用户限流（对未认证用户）
- `ScopedRateThrottle` - 作用域限流

#### 使用限流

```python
from faster_app.viewsets import ModelViewSet, UserRateThrottle, AnonRateThrottle

class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse
    
    # 配置限流类
    throttle_classes = [
        UserRateThrottle(rate="100/hour"),  # 用户：每小时 100 次
        AnonRateThrottle(rate="20/hour"),   # 匿名用户：每小时 20 次
    ]
```

#### 速率格式

速率字符串格式：`"数量/时间单位"`

支持的时间单位：
- `second` - 秒
- `minute` - 分钟
- `hour` - 小时
- `day` - 天

示例：
- `"100/hour"` - 每小时 100 次
- `"10/minute"` - 每分钟 10 次
- `"1000/day"` - 每天 1000 次

#### 用户限流

```python
class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse
    
    # 只对已认证用户限流
    throttle_classes = [UserRateThrottle(rate="100/hour")]
```

#### 匿名用户限流

```python
class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse
    
    # 只对未认证用户限流
    throttle_classes = [AnonRateThrottle(rate="20/hour")]
```

#### 组合限流

```python
class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse
    
    # 同时配置用户和匿名用户限流
    throttle_classes = [
        UserRateThrottle(rate="100/hour"),
        AnonRateThrottle(rate="20/hour"),
    ]
```

#### 作用域限流

```python
class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse
    
    # 使用作用域限流
    throttle_classes = [ScopedRateThrottle()]
    throttle_scope = "demo"  # 限流作用域
```

#### 自定义限流

```python
from faster_app.viewsets import BaseThrottle
from fastapi import Request

class CustomThrottle(BaseThrottle):
    """自定义限流"""
    
    async def allow_request(self, request: Request, view) -> bool:
        # 实现自定义限流逻辑
        # 返回 True 表示允许请求，False 表示需要限流
        return True
```

### 缓存系统

ViewSet 支持响应缓存，提高 API 性能。

#### 使用缓存装饰器

```python
from faster_app.viewsets import ModelViewSet, cache_response

class DemoViewSet(ModelViewSet):
    model = DemoModel
    serializer_class = DemoResponse
    
    @cache_response(timeout=600)  # 缓存 10 分钟
    async def list(self, request: Request, ...):
        # 响应会被缓存
        return await super().list(request, ...)
```

#### 自定义缓存键

```python
from faster_app.viewsets import cache_response

def custom_cache_key(request: Request) -> str:
    """自定义缓存键生成函数"""
    return f"demo_list_{request.query_params.get('page', '1')}"

class DemoViewSet(ModelViewSet):
    model = DemoModel
    
    @cache_response(timeout=600, key_func=custom_cache_key)
    async def list(self, request: Request, ...):
        pass
```

#### 使缓存失效

```python
from faster_app.viewsets.cache import invalidate_cache

# 清空所有缓存
invalidate_cache()

# 清空特定模式的缓存
invalidate_cache(pattern="demo_")
```

## 完整示例

```python
from faster_app.viewsets import (
    ModelViewSet,
    SearchFilter,
    OrderingFilter,
    JWTAuthentication,
    IsAuthenticated,
    UserRateThrottle,
    AnonRateThrottle,
    cache_response,
)

class CompleteDemoViewSet(ModelViewSet):
    """完整的 ViewSet 示例"""
    
    model = DemoModel
    serializer_class = DemoResponse
    
    # 认证和权限
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    # 过滤和排序
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["created_at", "name"]
    
    # 限流
    throttle_classes = [
        UserRateThrottle(rate="100/hour"),
        AnonRateThrottle(rate="20/hour"),
    ]
    
    @cache_response(timeout=300)
    async def list(self, request: Request, ...):
        return await super().list(request, ...)
```

## 总结

ViewSet 提供了完整的 RESTful API 构建能力：

- ✅ **基础 CRUD** - 完整的增删改查操作
- ✅ **权限和认证** - 灵活的权限控制和多种认证方式
- ✅ **过滤和排序** - 强大的查询能力
- ✅ **限流和缓存** - 性能优化和安全保护
- ✅ **自定义操作** - 灵活的扩展能力

## 下一步

ViewSet 功能已经完整实现，可以开始在实际项目中使用。
