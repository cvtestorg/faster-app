# 中间件配置指南

本指南介绍如何配置和使用 Faster APP 的中间件系统。

## 📢 配置系统说明

Faster APP 使用**嵌套配置模型**管理中间件配置，结构更清晰：

### 访问方式

```python
from faster_app.settings import configs

# 使用嵌套访问
origins = configs.MIDDLEWARE.cors.allow_origins
enabled = configs.MIDDLEWARE.timing.enabled
threshold = configs.MIDDLEWARE.timing.slow_threshold
```

### 环境变量配置

使用双下划线 `__` 表示嵌套层级：

```bash
MIDDLEWARE__CORS__ALLOW_ORIGINS=["https://example.com"]
MIDDLEWARE__TIMING__ENABLED=true
MIDDLEWARE__TIMING__SLOW_THRESHOLD=0.5
```

> 💡 详见 [配置系统使用指南](settings-guide.md)

## 概述

Faster APP 的中间件系统支持以下特性：

- ✅ **环境感知**：自动根据 DEBUG 配置调整安全策略
- ✅ **优先级排序**：通过 priority 字段控制中间件执行顺序
- ✅ **动态启用/禁用**：通过 enabled 字段灵活控制中间件
- ✅ **配置集中管理**：使用嵌套配置模型，结构清晰
- ✅ **自动验证**：启动时自动检查配置安全性

## 内置中间件

### 1. 请求日志中间件 (RequestLoggingMiddleware)

**功能：** 记录所有 HTTP 请求的详细信息

**配置项：**
```bash
MIDDLEWARE__REQUEST_LOGGING__ENABLED=true
MIDDLEWARE__REQUEST_LOGGING__LOG_BODY=false
MIDDLEWARE__REQUEST_LOGGING__LOG_RESPONSE=false
```

**优先级：** 1（最先执行，捕获所有请求）

### 2. 性能监控中间件 (RequestTimingMiddleware)

**功能：** 监控请求处理时间，自动识别慢请求

**配置项：**
```bash
ENABLE_TIMING_MIDDLEWARE=true    # 是否启用
SLOW_REQUEST_THRESHOLD=1.0       # 慢请求阈值（秒）
```

**优先级：** 2

**特性：**
- 自动在响应头中添加 `X-Process-Time`
- 超过阈值的请求会记录警告日志

### 3. 安全响应头中间件 (SecurityHeadersMiddleware)

**功能：** 自动添加安全相关的 HTTP 响应头

**配置项：** 无需配置，默认启用

**优先级：** 11

**添加的响应头：**
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security`（仅生产环境）

### 4. CORS 中间件 (CORSMiddleware)

**功能：** 处理跨域资源共享（CORS）

**配置项：**
```bash
CORS_ALLOW_ORIGINS=["*"]         # 允许的源（域名列表）
CORS_ALLOW_CREDENTIALS=false     # 是否允许携带凭证
CORS_ALLOW_METHODS=["*"]         # 允许的 HTTP 方法
CORS_ALLOW_HEADERS=["*"]         # 允许的请求头
CORS_EXPOSE_HEADERS=[]           # 暴露的响应头
CORS_MAX_AGE=600                 # 预检请求缓存时间（秒）
```

**优先级：** 12

**⚠️ 安全注意事项：**

❌ **禁止配置：**
```python
CORS_ALLOW_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=true      # 危险！会导致严重安全问题
```

✅ **推荐配置（生产环境）：**
```python
CORS_ALLOW_ORIGINS=["https://yourdomain.com", "https://app.yourdomain.com"]
CORS_ALLOW_CREDENTIALS=true
```

### 5. 可信主机中间件 (TrustedHostMiddleware)

**功能：** 防止 Host header 攻击

**配置项：**
```bash
TRUSTED_HOST_ENABLED=false       # 是否启用（生产环境建议启用）
TRUSTED_HOSTS=["*"]              # 允许的主机名列表
```

**优先级：** 13

**推荐配置（生产环境）：**
```bash
TRUSTED_HOST_ENABLED=true
TRUSTED_HOSTS=["yourdomain.com", "*.yourdomain.com"]
```

### 6. GZip 压缩中间件 (GZipMiddleware)

**功能：** 压缩响应内容，减少带宽占用

**配置项：**
```bash
ENABLE_GZIP=true                 # 是否启用
GZIP_MINIMUM_SIZE=1000           # 最小压缩大小（字节）
```

**优先级：** 21

## 中间件执行顺序

中间件按照优先级排序执行，数字越小越先执行：

```
请求流向：
客户端 
  → RequestLoggingMiddleware (priority: 1)
  → RequestTimingMiddleware (priority: 2)
  → SecurityHeadersMiddleware (priority: 11)
  → CORSMiddleware (priority: 12)
  → TrustedHostMiddleware (priority: 13)
  → GZipMiddleware (priority: 21)
  → 路由处理器

响应流向：
路由处理器
  → GZipMiddleware (priority: 21)
  → TrustedHostMiddleware (priority: 13)
  → CORSMiddleware (priority: 12)
  → SecurityHeadersMiddleware (priority: 11)
  → RequestTimingMiddleware (priority: 2)
  → RequestLoggingMiddleware (priority: 1)
  → 客户端
```

## 环境配置示例

### 开发环境配置

```bash
# .env 文件
DEBUG=true

# 宽松的 CORS 配置（方便开发）
CORS_ALLOW_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=false

# 禁用严格的主机名检查
TRUSTED_HOST_ENABLED=false

# 启用详细日志
ENABLE_REQUEST_LOGGING=true
LOG_REQUEST_BODY=false
SLOW_REQUEST_THRESHOLD=1.0
```

### 生产环境配置

```bash
# .env 文件
DEBUG=false

# 严格的 CORS 配置
CORS_ALLOW_ORIGINS=["https://yourdomain.com","https://app.yourdomain.com"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET","POST","PUT","DELETE","PATCH"]

# 启用主机名验证
TRUSTED_HOST_ENABLED=true
TRUSTED_HOSTS=["yourdomain.com","*.yourdomain.com"]

# 生产环境日志配置
ENABLE_REQUEST_LOGGING=true
LOG_REQUEST_BODY=false          # 避免记录敏感信息
LOG_RESPONSE_BODY=false
SLOW_REQUEST_THRESHOLD=0.5      # 生产环境使用更严格的阈值

# 启用压缩
ENABLE_GZIP=true
GZIP_MINIMUM_SIZE=1000
```

## 自定义中间件

### 添加自定义中间件

1. 在 `faster_app/middleware/builtins/custom.py` 或创建新文件
2. 继承 `BaseHTTPMiddleware`
3. 实现 `dispatch` 方法

示例：
```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # 请求前处理
        print(f"Request: {request.url}")
        
        # 调用下一个中间件/路由
        response = await call_next(request)
        
        # 响应后处理
        print(f"Response: {response.status_code}")
        
        return response
```

### 注册自定义中间件

在 `faster_app/middleware/builtins/middlewares.py` 中添加：

```python
MIDDLEWARES = [
    # ... 其他中间件
    {
        "class": "faster_app.middleware.builtins.custom.CustomMiddleware",
        "priority": 50,           # 设置优先级
        "enabled": True,          # 是否启用
        "kwargs": {               # 传递给中间件的参数
            "param1": "value1",
        },
    },
]
```

## 配置验证

系统会在启动时自动验证中间件配置：

### ✅ 安全配置检查

- **CORS 配置验证**：检查 `allow_credentials` 和 `allow_origins` 的组合
- **生产环境警告**：对不安全的配置发出警告

### 示例输出

**开发环境：**
```
🔧 [开发模式] 中间件使用宽松的安全配置
```

**生产环境（配置错误）：**
```
❌ [安全警告] 生产环境中 CORS 配置不安全: 
   allow_credentials=True 不能与 allow_origins=['*'] 同时使用！
```

**生产环境（配置正常但有改进空间）：**
```
⚠️  [安全提示] 生产环境建议启用 TrustedHostMiddleware
```

## 最佳实践

### 1. 环境隔离
- 开发环境使用宽松配置，方便调试
- 生产环境使用严格配置，确保安全

### 2. 日志管理
- 避免在生产环境记录请求体/响应体（可能包含敏感信息）
- 使用适当的日志级别

### 3. 性能优化
- 根据实际情况调整 `SLOW_REQUEST_THRESHOLD`
- 启用 GZip 压缩减少带宽占用
- 避免在中间件中执行阻塞操作

### 4. 安全加固
- 生产环境务必正确配置 CORS
- 启用 TrustedHostMiddleware
- 定期审查中间件配置

### 5. 监控告警
- 关注慢请求日志，及时优化性能瓶颈
- 监控异常中间件加载失败的日志

## 故障排查

### 中间件未生效

1. 检查 `enabled` 字段是否为 `true`
2. 查看启动日志中的中间件加载信息
3. 确认配置文件语法正确

### CORS 配置不生效

1. 检查 `CORS_ALLOW_ORIGINS` 是否包含请求来源
2. 确认中间件加载顺序正确
3. 使用浏览器开发者工具检查 CORS 响应头

### 性能问题

1. 检查是否记录了过多的请求体/响应体
2. 调整 `SLOW_REQUEST_THRESHOLD` 避免过多日志
3. 确认中间件执行顺序合理

## 参考资源

- [FastAPI 中间件文档](https://fastapi.tiangolo.com/advanced/middleware/)
- [Starlette 中间件文档](https://www.starlette.io/middleware/)
- [OWASP CORS 安全指南](https://owasp.org/www-community/attacks/CSRF)
