# Lifespan 生命周期管理指南

## 概述

Faster APP 提供了灵活的生命周期管理系统，支持数据库连接、应用初始化和用户自定义生命周期的统一管理。

## 默认行为

框架默认启用以下 lifespan：

1. **database_lifespan** - 数据库连接管理 (优先级: 10)
2. **apps_lifespan** - 应用生命周期管理 (优先级: 20)
3. **用户自定义 lifespan** - 从 `config/lifespan.py` 自动发现 (优先级: 100+)

启动顺序由优先级决定（数字越小越先执行），关闭顺序自动逆序。

## 控制 Lifespan

### 方式 1: 通过参数控制

直接在代码中控制：

```python
from faster_app.lifespan import get_lifespan
from fastapi import FastAPI

# 只启用数据库 lifespan
lifespan = get_lifespan(
    enable_database=True,
    enable_apps=False,
    enable_user=False,
)

app = FastAPI(lifespan=lifespan)
```

### 方式 2: 通过配置控制

在 `config/settings.py` 中添加配置：

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 禁用数据库 lifespan (适用于无数据库的 API 服务)
    ENABLE_DATABASE_LIFESPAN: bool = False
    
    # 禁用应用 lifespan (如果不使用应用生命周期管理)
    ENABLE_APPS_LIFESPAN: bool = False
    
    # 禁用用户自定义 lifespan
    ENABLE_USER_LIFESPANS: bool = False
```

### 方式 3: 通过环境变量控制

通过 `.env` 文件或环境变量：

```bash
ENABLE_DATABASE_LIFESPAN=false
ENABLE_APPS_LIFESPAN=true
ENABLE_USER_LIFESPANS=true
```

### 优先级

参数 > 配置 > 默认值 (True)

```python
# 参数优先级最高，会覆盖配置
lifespan = get_lifespan(enable_database=False)  # 禁用数据库，即使配置中启用
```

## 用户自定义 Lifespan

### 基础用法

在 `config/lifespan.py` 中定义：

```python
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def cache_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Redis 缓存生命周期"""
    # 启动时
    print("Connecting to Redis...")
    # redis_client = await connect_redis()
    # app.state.redis = redis_client
    
    yield
    
    # 关闭时
    print("Disconnecting from Redis...")
    # await redis_client.close()


@asynccontextmanager
async def mq_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """消息队列生命周期"""
    print("Connecting to Message Queue...")
    yield
    print("Disconnecting from Message Queue...")
```

框架会自动发现并注册这些函数。

## 高级定制

### 使用 LifespanManager

对于复杂场景，可以使用 `LifespanManager` 进行精细控制：

```python
from faster_app.lifespan import LifespanManager, database_lifespan, apps_lifespan


def create_custom_lifespan():
    """创建自定义 lifespan 配置"""
    manager = LifespanManager()
    
    # 注册内置 lifespan
    manager.register("database", database_lifespan, enabled=True, priority=10)
    manager.register("apps", apps_lifespan, enabled=True, priority=20)
    
    # 注册自定义 lifespan
    manager.register("cache", cache_lifespan, enabled=True, priority=30)
    manager.register("mq", mq_lifespan, enabled=False, priority=40)
    
    # 动态控制
    import os
    if os.getenv("ENABLE_MQ") == "true":
        manager.enable("mq")
    
    return manager.build()


# 使用自定义 lifespan
from fastapi import FastAPI

app = FastAPI(lifespan=create_custom_lifespan())
```

### Manager API

```python
from faster_app.lifespan import LifespanManager

manager = LifespanManager()

# 注册 lifespan
manager.register(
    name="cache",           # 唯一名称
    lifespan=cache_func,    # lifespan 函数
    enabled=True,           # 是否启用
    priority=30,            # 优先级（越小越先执行）
)

# 启用/禁用
manager.enable("cache")
manager.disable("cache")

# 检查状态
is_enabled = manager.is_enabled("cache")

# 列出启用的 lifespan
enabled = manager.list_enabled()  # 返回按优先级排序的名称列表

# 构建组合的 lifespan
lifespan_func = manager.build()
```

## 执行顺序

### 默认顺序

```
启动: database (10) -> apps (20) -> user_lifespans (100+)
关闭: user_lifespans -> apps -> database (自动逆序)
```

### 自定义顺序

通过 `priority` 参数控制：

```python
manager.register("service_a", func_a, priority=5)   # 最先执行
manager.register("service_b", func_b, priority=15)  # 其次
manager.register("service_c", func_c, priority=25)  # 最后
```

## 最佳实践

### 1. 明确依赖关系

确保有依赖关系的服务按正确顺序启动：

```python
# 数据库应该最先启动
manager.register("database", database_lifespan, priority=10)

# 依赖数据库的应用
manager.register("apps", apps_lifespan, priority=20)

# 依赖应用的缓存
manager.register("cache", cache_lifespan, priority=30)
```

### 2. 使用配置控制

根据环境启用不同的 lifespan：

```python
# 开发环境不需要缓存
if not settings.DEBUG:
    manager.register("cache", cache_lifespan, enabled=True)
```

### 3. 错误处理

在 lifespan 中捕获并记录错误：

```python
@asynccontextmanager
async def safe_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        await setup_service()
        yield
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        yield  # 继续运行，不中断应用
    finally:
        try:
            await cleanup_service()
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
```

### 4. 存储到 app.state

将初始化的资源存储到 `app.state` 供路由使用：

```python
@asynccontextmanager
async def redis_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    redis = await connect_redis()
    app.state.redis = redis  # 存储
    yield
    await redis.close()


# 在路由中使用
@router.get("/data")
async def get_data(request: Request):
    redis = request.app.state.redis
    return await redis.get("key")
```

## 完整示例

参见：
- `docs/examples/config_settings_lifespan.py.example` - 配置示例
- `docs/examples/custom_lifespan_advanced.py.example` - 高级定制示例
- `docs/examples/config_lifespan.py.example` - 用户自定义 lifespan 示例
