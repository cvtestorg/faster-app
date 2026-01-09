# 异常处理指南

## 概述

Faster APP 提供了统一的异常处理系统,支持自定义异常类型、灵活的异常处理器管理和标准化的错误响应格式。

## 异常类型

### 内置异常类型

框架提供了常用的异常类型：

```python
from faster_app.exceptions import (
    ValidationError,      # 400 - 验证错误
    BadRequestError,      # 400 - 错误请求
    UnauthorizedError,    # 401 - 未授权
    ForbiddenError,       # 403 - 禁止访问
    NotFoundError,        # 404 - 资源未找到
    ConflictError,        # 409 - 资源冲突
    TooManyRequestsError, # 429 - 请求频率过高
    InternalServerError,  # 500 - 服务器内部错误
)
```

### 使用方式

#### 1. 使用默认消息

```python
from faster_app.exceptions import NotFoundError

# 使用默认消息
raise NotFoundError()  # "资源未找到"
```

#### 2. 自定义消息

```python
# 自定义消息
raise NotFoundError("用户不存在")
```

#### 3. 添加详细信息和数据

```python
raise ValidationError(
    message="用户名格式错误",
    error_detail="用户名必须是 3-20 个字符",
    data={"field": "username", "value": "ab"}
)
```

### 自定义异常类型

继承 `FasterAppError` 创建自定义异常：

```python
from http import HTTPStatus
from faster_app.exceptions import FasterAppError


class PaymentRequiredError(FasterAppError):
    """需要付费 (402)"""

    default_status_code = HTTPStatus.PAYMENT_REQUIRED
    default_message = "需要付费才能访问此资源"


# 使用
raise PaymentRequiredError()
raise PaymentRequiredError("您的账户余额不足")
```

## 错误响应格式

所有异常都会被转换为统一的 JSON 响应格式：

```json
{
  "success": false,
  "code": 404,
  "message": "资源未找到",
  "data": null,
  "timestamp": "2026-01-02T13:45:00.123456",
  "error_detail": "详细错误信息(仅开发环境)"
}
```

### 字段说明

- `success`: 固定为 `false`
- `code`: 业务错误码(默认与 HTTP 状态码相同)
- `message`: 错误消息
- `data`: 附加数据(可选)
- `timestamp`: 错误发生时间(ISO 8601 格式)
- `error_detail`: 详细错误信息(仅在开发环境显示)

## 异常管理器

### 基础用法

框架自动注册默认异常处理器：

```python
from fastapi import FastAPI
from faster_app.exceptions import get_manager

app = FastAPI()
get_manager().apply(app)
```

### 高级定制

使用 `ExceptionManager` 进行高级定制：

```python
from faster_app.exceptions import ExceptionManager, get_manager


# 方式 1: 使用全局管理器
manager = get_manager()

# 方式 2: 创建自定义管理器
manager = ExceptionManager()
manager.register_defaults()  # 注册默认处理器

# 注册自定义异常处理器
async def custom_handler(request, exc):
    return JSONResponse(
        content={"error": str(exc)},
        status_code=500,
    )

manager.register(CustomError, custom_handler)

# 应用到 FastAPI
manager.apply(app)
```

### 管理器 API

```python
from faster_app.exceptions import ExceptionManager

manager = ExceptionManager()

# 注册处理器
manager.register(
    exception_class=NotFoundError,
    handler=custom_handler,
    priority=10,  # 优先级(数字越小越先注册)
)

# 注册默认处理器
manager.register_defaults()

# 取消注册
manager.unregister(NotFoundError)

# 获取处理器
handler = manager.get_handler(NotFoundError)

# 列出所有处理器
handlers = manager.list_handlers()

# 应用到应用
manager.apply(app)

# 清空所有处理器
manager.clear()
```

## 在路由中使用

### 基础用法

```python
from fastapi import APIRouter
from faster_app.exceptions import NotFoundError

router = APIRouter()


@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise NotFoundError(f"用户 {user_id} 不存在")
    return user
```

### 在 ViewSet 中使用

```python
from faster_app.viewsets import ViewSet
from faster_app.exceptions import ForbiddenError


class UserViewSet(ViewSet):
    async def retrieve(self, request, pk):
        user = await self.get_object(pk)

        # 权限检查
        if user.id != request.user.id:
            raise ForbiddenError("您无权访问其他用户的信息")

        return user
```

## 开发环境 vs 生产环境

### 开发环境 (DEBUG=True)

- 显示详细错误信息 (`error_detail`)
- 显示完整的堆栈跟踪 (`traceback`)
- 显示验证错误的详细字段信息

### 生产环境 (DEBUG=False)

- 隐藏详细错误信息
- 隐藏堆栈跟踪
- 只显示用户友好的错误消息

## 最佳实践

### 1. 使用合适的异常类型

```python
# ✅ 好的做法
raise NotFoundError("用户不存在")

# ❌ 不好的做法
raise Exception("用户不存在")
```

### 2. 提供有意义的错误消息

```python
# ✅ 好的做法
raise ValidationError(
    "用户名格式错误",
    error_detail="用户名必须是 3-20 个字符,只能包含字母、数字和下划线"
)

# ❌ 不好的做法
raise ValidationError("错误")
```

### 3. 使用 error_detail 提供技术细节

```python
# ✅ 好的做法
raise InternalServerError(
    "数据库操作失败",
    error_detail=f"无法连接到数据库: {str(db_error)}"
)
```

### 4. 附加有用的数据

```python
# ✅ 好的做法
raise ValidationError(
    "字段验证失败",
    data={
        "fields": ["username", "email"],
        "errors": {
            "username": "用户名已存在",
            "email": "邮箱格式不正确"
        }
    }
)
```

### 5. 在业务逻辑层抛出异常

```python
# ✅ 好的做法 - 在服务层抛出
class UserService:
    async def get_user(self, user_id: int):
        user = await User.get_or_none(id=user_id)
        if not user:
            raise NotFoundError(f"用户 {user_id} 不存在")
        return user


# 在路由中使用
@router.get("/users/{user_id}")
async def get_user(user_id: int):
    return await UserService().get_user(user_id)
```

### 6. 自定义业务异常

```python
# 为特定业务场景创建异常
class InsufficientBalanceError(FasterAppError):
    """余额不足"""

    default_status_code = HTTPStatus.PAYMENT_REQUIRED
    default_message = "账户余额不足"


# 使用
async def purchase(user_id: int, amount: float):
    user = await get_user(user_id)
    if user.balance < amount:
        raise InsufficientBalanceError(
            f"需要 {amount} 元,当前余额 {user.balance} 元",
            data={"required": amount, "current": user.balance}
        )
```

## 完整示例

```python
from fastapi import FastAPI, APIRouter
from faster_app.exceptions import (
    NotFoundError,
    ValidationError,
    get_manager,
)

# 创建应用
app = FastAPI()
get_manager().apply(app)

# 创建路由
router = APIRouter()


@router.get("/users/{user_id}")
async def get_user(user_id: int):
    """获取用户信息"""
    if user_id < 0:
        raise ValidationError("用户 ID 必须是正整数")

    user = await User.get_or_none(id=user_id)
    if not user:
        raise NotFoundError(f"用户 {user_id} 不存在")

    return user


@router.post("/users")
async def create_user(username: str, email: str):
    """创建用户"""
    # 检查用户名是否存在
    existing = await User.get_or_none(username=username)
    if existing:
        raise ValidationError(
            "用户名已存在",
            data={"field": "username", "value": username}
        )

    # 创建用户
    user = await User.create(username=username, email=email)
    return user


app.include_router(router)
```

## 参考

- 异常基类: `faster_app/exceptions/base.py`
- 异常类型: `faster_app/exceptions/types.py`
- 异常处理器: `faster_app/exceptions/handlers.py`
- 异常管理器: `faster_app/exceptions/manager.py`
