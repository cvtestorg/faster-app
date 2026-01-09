# 自定义中间件使用指南

## 概述

为了避免性能开销，框架默认只启用 FastAPI 内置的核心中间件：

- ✅ **CORSMiddleware** - 跨域请求处理
- ✅ **TrustedHostMiddleware** - 可信主机验证（可选）
- ✅ **GZipMiddleware** - 响应压缩

自定义中间件（如日志、性能监控）默认**不启用**，您可以根据需要选择性添加。

## 可用的自定义中间件

框架在 `faster_app/middleware/builtins/custom.py` 中提供了以下自定义中间件示例：

### 1. RequestTimingMiddleware

**功能**：性能监控中间件，记录请求处理时间

**特点**：
- ⚡ 轻量级，性能开销小
- 📊 在响应头中添加 `X-Process-Time`
- ⚠️ 对慢请求进行警告

**适用场景**：生产环境性能监控

### 2. RequestLoggingMiddleware

**功能**：请求日志中间件，记录所有请求详情

**特点**：
- 📝 记录请求方法、路径、客户端 IP
- 📋 可选记录请求体和响应体
- ⚠️ 会增加 I/O 开销

**适用场景**：开发调试、审计日志

### 3. SecurityHeadersMiddleware

**功能**：安全响应头中间件，自动添加安全 HTTP 头

**特点**：
- 🔒 添加 `X-Content-Type-Options: nosniff`
- 🔒 添加 `X-Frame-Options: DENY`
- 🔒 添加 `X-XSS-Protection: 1; mode=block`
- 🔒 生产环境自动添加 HSTS

**适用场景**：生产环境安全加固

## 如何添加自定义中间件

### 方法 1: 修改配置文件

编辑 `faster_app/middleware/builtins/middlewares.py`，在 `MIDDLEWARES` 列表中添加：

```python
MIDDLEWARES = [
    # 性能监控（推荐）
    {
        "class": "faster_app.middleware.builtins.custom.RequestTimingMiddleware",
        "priority": 1,
        "enabled": True,
        "kwargs": {
            "slow_threshold": 1.0,  # 慢请求阈值（秒）
        },
    },
    
    # 请求日志（仅开发环境）
    {
        "class": "faster_app.middleware.builtins.custom.RequestLoggingMiddleware",
        "priority": 2,
        "enabled": configs.debug,  # 仅在调试模式启用
        "kwargs": {
            "log_request_body": False,  # 不记录请求体
            "log_response_body": False,  # 不记录响应体
        },
    },
    
    # 安全响应头（生产环境推荐）
    {
        "class": "faster_app.middleware.builtins.custom.SecurityHeadersMiddleware",
        "priority": 11,
        "enabled": not configs.debug,  # 仅在生产环境启用
        "kwargs": {},
    },
    
    # ... 以下是默认的中间件
    {
        "class": "fastapi.middleware.cors.CORSMiddleware",
        "priority": 12,
        "enabled": True,
        # ...
    },
]
```

### 方法 2: 通过环境变量控制

如果自定义中间件支持环境变量配置，可以在 `.env` 文件中设置：

```bash
# 性能监控配置
TIMING_ENABLED=true
TIMING_SLOW_THRESHOLD=1.0

# 请求日志配置
REQUEST_LOGGING_ENABLED=false
REQUEST_LOGGING_LOG_BODY=false
REQUEST_LOGGING_LOG_RESPONSE=false
```

然后在 `middlewares.py` 中使用配置：

```python
{
    "class": "faster_app.middleware.builtins.custom.RequestTimingMiddleware",
    "priority": 1,
    "enabled": configs.middleware.timing.enabled,  # 从配置读取
    "kwargs": {
        "slow_threshold": configs.middleware.timing.slow_threshold,
    },
},
```

## 中间件执行顺序

中间件按 `priority` 字段排序执行，数字越小越先执行：

```
优先级范围说明：
- 1-10:   日志和监控（最外层，捕获一切）
- 11-20:  安全相关（CORS, TrustedHost, SecurityHeaders）
- 21-30:  压缩和优化（GZip）
- 31+:    其他业务中间件

执行顺序：
请求流：priority 1 → 2 → 3 → ... → 路由处理器
响应流：路由处理器 → ... → 3 → 2 → 1
```

## 最佳实践

### 生产环境推荐配置

```python
MIDDLEWARES = [
    # 性能监控（轻量级，推荐启用）
    {
        "class": "faster_app.middleware.builtins.custom.RequestTimingMiddleware",
        "priority": 1,
        "enabled": True,
        "kwargs": {"slow_threshold": 1.0},
    },
    
    # 安全响应头（生产环境必备）
    {
        "class": "faster_app.middleware.builtins.custom.SecurityHeadersMiddleware",
        "priority": 11,
        "enabled": not configs.debug,
        "kwargs": {},
    },
    
    # CORS（根据需求配置）
    {
        "class": "fastapi.middleware.cors.CORSMiddleware",
        "priority": 12,
        "enabled": True,
        "kwargs": {
            "allow_origins": ["https://yourdomain.com"],  # 明确指定域名
            "allow_credentials": False,
            # ...
        },
    },
    
    # TrustedHost（生产环境必备）
    {
        "class": "fastapi.middleware.trustedhost.TrustedHostMiddleware",
        "priority": 13,
        "enabled": True,  # 生产环境启用
        "kwargs": {
            "allowed_hosts": ["yourdomain.com", "*.yourdomain.com"],
        },
    },
    
    # GZip 压缩
    {
        "class": "fastapi.middleware.gzip.GZipMiddleware",
        "priority": 21,
        "enabled": True,
        "kwargs": {"minimum_size": 1000},
    },
]
```

### 开发环境推荐配置

```python
MIDDLEWARES = [
    # 请求日志（便于调试）
    {
        "class": "faster_app.middleware.builtins.custom.RequestLoggingMiddleware",
        "priority": 1,
        "enabled": configs.debug,
        "kwargs": {
            "log_request_body": True,   # 开发环境可以记录请求体
            "log_response_body": False,
        },
    },
    
    # 性能监控
    {
        "class": "faster_app.middleware.builtins.custom.RequestTimingMiddleware",
        "priority": 2,
        "enabled": True,
        "kwargs": {"slow_threshold": 1.0},
    },
    
    # CORS（宽松配置）
    {
        "class": "fastapi.middleware.cors.CORSMiddleware",
        "priority": 12,
        "enabled": True,
        "kwargs": {
            "allow_origins": ["*"],  # 开发环境允许所有域名
            "allow_credentials": False,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        },
    },
    
    # GZip 压缩
    {
        "class": "fastapi.middleware.gzip.GZipMiddleware",
        "priority": 21,
        "enabled": True,
        "kwargs": {"minimum_size": 1000},
    },
]
```

## 性能考虑

### 中间件性能影响对比

| 中间件 | 性能开销 | 推荐场景 |
|--------|---------|---------|
| RequestTimingMiddleware | 极低 | ✅ 生产环境 |
| SecurityHeadersMiddleware | 极低 | ✅ 生产环境 |
| CORSMiddleware | 低 | ✅ 所有环境 |
| GZipMiddleware | 中等 | ✅ 生产环境 |
| RequestLoggingMiddleware | 高（I/O） | ⚠️ 仅开发/调试 |

### 优化建议

1. **请求日志中间件**：仅在开发环境或调试时启用
2. **避免记录请求体**：会显著增加内存和 I/O 开销
3. **使用条件启用**：根据 `configs.debug` 自动切换配置
4. **控制日志级别**：生产环境使用 `INFO` 或更高级别

## 创建自定义中间件

您也可以创建自己的中间件。参考 `custom.py` 中的示例：

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class MyCustomMiddleware(BaseHTTPMiddleware):
    """自定义中间件"""
    
    def __init__(self, app, param1: str = "default"):
        super().__init__(app)
        self.param1 = param1
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # 请求前处理
        # ...
        
        # 调用下一个中间件/路由处理器
        response = await call_next(request)
        
        # 响应后处理
        # ...
        
        return response
```

然后在 `middlewares.py` 中注册：

```python
{
    "class": "your_module.MyCustomMiddleware",
    "priority": 5,
    "enabled": True,
    "kwargs": {
        "param1": "value1",
    },
}
```

## 总结

- 默认配置已优化性能，只包含必要的核心中间件
- 根据需求选择性添加自定义中间件
- 开发环境和生产环境使用不同的配置策略
- 注意中间件的执行顺序和性能影响
