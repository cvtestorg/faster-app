# 配置基础和中间件

Faster APP 使用基于 Pydantic 的嵌套配置系统，支持环境变量和多环境部署。

## 配置访问

### 基本用法

```python
from faster_app.settings import configs

# 基础配置
configs.debug
configs.project_name
configs.version

# 服务器配置
configs.server.host
configs.server.port

# JWT 配置
configs.jwt.secret_key
configs.jwt.algorithm
configs.jwt.access_token_expire_minutes

# 数据库配置
configs.database.url
configs.database.models
```

## 环境变量

### .env 文件

在项目根目录创建 `.env` 文件：

```bash
# 基础配置
DEBUG=true
PROJECT_NAME=MyAPI
VERSION=1.0.0

# 服务器
HOST=0.0.0.0
PORT=8000

# 安全
SECRET_KEY=your-secret-key-change-in-production

# 数据库
DB_URL=sqlite://db.sqlite
# DB_URL=postgresql://user:pass@localhost:5432/dbname
# DB_URL=mysql://user:pass@localhost:3306/dbname
```

### 环境变量优先级

1. 操作系统环境变量（最高优先级）
2. `.env` 文件
3. 默认值（最低优先级）

```bash
# 通过环境变量覆盖
export DEBUG=false
export PORT=9000
faster server start
```

## 中间件配置

Faster APP 内置多个中间件，可通过环境变量控制。

### CORS 配置

跨域资源共享配置：

```bash
# 开发环境
CORS_ALLOW_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=false
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]

# 生产环境（推荐）
CORS_ALLOW_ORIGINS=["https://example.com","https://app.example.com"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET","POST","PUT","DELETE"]
CORS_ALLOW_HEADERS=["Content-Type","Authorization"]
```

**安全提示**：
- 生产环境**不要**使用 `["*"]`
- 如果设置 `CORS_ALLOW_CREDENTIALS=true`，必须指定具体域名

### TrustedHost 配置

防止 Host header 攻击：

```bash
# 启用
TRUSTED_HOST_ENABLED=true

# 允许的主机
TRUSTED_HOSTS=["example.com","*.example.com","localhost"]
```

### GZip 压缩

启用响应压缩：

```bash
GZIP_ENABLED=true
GZIP_MINIMUM_SIZE=1000  # 最小压缩大小（字节）
```

### 限流配置

API 速率限制：

```bash
# 限流规则（JSON 格式）
THROTTLE_RATES='{"user": "100/hour", "anon": "20/hour"}'

# 或分别设置
THROTTLE_USER_RATE=100/hour
THROTTLE_ANON_RATE=20/hour
```

## 数据库配置

### 连接 URL 格式

```bash
# SQLite（开发）
DB_URL=sqlite://db.sqlite
DB_URL=sqlite:///absolute/path/db.sqlite

# PostgreSQL
DB_URL=postgresql://user:password@localhost:5432/database
DB_URL=postgresql://user:password@localhost:5432/database?schema=public

# MySQL
DB_URL=mysql://user:password@localhost:3306/database
DB_URL=mysql://user:password@localhost:3306/database?charset=utf8mb4
```

### 连接池配置（生产环境）

```bash
DB_URL=postgresql://user:pass@localhost:5432/db?min_size=1&max_size=5
```

### 生命周期配置

```bash
# 启用数据库生命周期管理
ENABLE_DATABASE_LIFESPAN=true

# 启用应用生命周期钩子
ENABLE_APPS_LIFESPAN=false
```

## 配置结构

### 嵌套配置模型

Faster APP 使用嵌套的 Pydantic 模型组织配置：

```python
from faster_app.settings import configs

# 顶层配置
configs.debug          # bool
configs.project_name   # str
configs.version        # str

# 服务器配置
configs.server.host    # str
configs.server.port    # int
configs.server.reload  # bool

# JWT 配置
configs.jwt.secret_key                    # str
configs.jwt.algorithm                     # str
configs.jwt.access_token_expire_minutes   # int

# 数据库配置
configs.database.url     # str
configs.database.models  # list[str]

# 中间件配置
configs.middleware.cors_enabled           # bool
configs.middleware.cors_allow_origins     # list[str]
configs.middleware.trusted_host_enabled   # bool
configs.middleware.gzip_enabled           # bool

# 限流配置
configs.throttle.enabled  # bool
configs.throttle.rates    # dict

# 日志配置
configs.logging.level     # str
configs.logging.format    # str
```

## 配置验证

Pydantic 自动验证配置：

```python
# 自动类型转换
DEBUG=true          # → configs.debug = True (bool)
PORT=8000           # → configs.server.port = 8000 (int)

# 无效值会抛出异常
PORT=abc            # ValidationError: value is not a valid integer
```

## 最佳实践

### 1. 敏感信息

**不要**将敏感信息提交到版本控制：

```bash
# .gitignore
.env
.env.local
.env.*.local
```

提供示例文件：

```bash
# .env.example
DEBUG=true
SECRET_KEY=change-this-in-production
DB_URL=sqlite://db.sqlite
```

### 2. 环境分离

为不同环境创建配置文件：

```bash
.env.development
.env.staging
.env.production
```

### 3. 配置检查

启动时检查必需配置：

```python
from faster_app.settings import configs

if not configs.debug:
    # 生产环境检查
    assert configs.jwt.secret_key != "test-secret-key", "必须修改 SECRET_KEY"
    assert configs.middleware.cors_allow_origins != ["*"], "生产环境不能使用 CORS *"
```

### 4. 文档化配置

在 `.env.example` 中添加注释：

```bash
# API 服务器配置
HOST=0.0.0.0          # 监听地址，0.0.0.0 表示所有接口
PORT=8000             # 监听端口

# 安全配置
SECRET_KEY=your-secret-key  # JWT 密钥，生产环境必须修改
```

### 5. 使用配置验证

```python
from faster_app.settings.config import DefaultSettings
from pydantic import model_validator

class CustomSettings(DefaultSettings):
    @model_validator(mode="after")
    def validate_production(self):
        if not self.debug:
            if self.jwt.secret_key == "test-secret-key":
                raise ValueError("生产环境必须修改 JWT secret_key")
        return self
```

通过合理的配置管理，可以轻松地在不同环境间切换。
