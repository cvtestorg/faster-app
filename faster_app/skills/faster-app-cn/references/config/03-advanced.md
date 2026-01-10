# 高级配置

多环境配置、自定义配置扩展和高级用法。

## 多环境配置

### 环境文件

为不同环境创建独立的配置文件：

```bash
# 项目结构
.
├── .env                  # 默认（开发）
├── .env.development      # 开发环境
├── .env.staging          # 预发布环境
├── .env.production       # 生产环境
└── .env.example          # 示例文件（提交到 git）
```

### 加载特定环境

**方式1：通过环境变量**

```bash
# 指定环境文件
export ENV_FILE=.env.production
faster server start

# 或一行命令
ENV_FILE=.env.production faster server start
```

**方式2：通过符号链接**

```bash
# 开发环境
ln -sf .env.development .env

# 生产环境
ln -sf .env.production .env
```

### 环境配置示例

**`.env.development`**：

```bash
DEBUG=true
HOST=0.0.0.0
PORT=8000
SECRET_KEY=dev-secret-key
DB_URL=sqlite://db.sqlite
CORS_ALLOW_ORIGINS=["*"]
LOG_LEVEL=DEBUG
```

**`.env.staging`**：

```bash
DEBUG=false
HOST=0.0.0.0
PORT=8000
SECRET_KEY=${STAGING_SECRET_KEY}
DB_URL=postgresql://user:pass@staging-db:5432/app
CORS_ALLOW_ORIGINS=["https://staging.example.com"]
LOG_LEVEL=INFO
```

**`.env.production`**：

```bash
DEBUG=false
HOST=0.0.0.0
PORT=8000
SECRET_KEY=${PRODUCTION_SECRET_KEY}
DB_URL=postgresql://user:pass@prod-db:5432/app
CORS_ALLOW_ORIGINS=["https://example.com"]
TRUSTED_HOST_ENABLED=true
TRUSTED_HOSTS=["example.com"]
LOG_LEVEL=WARNING
LOG_FORMAT=JSON
LOG_TO_FILE=true
```

## Docker 多环境

**docker-compose.yml**：

```yaml
version: '3.8'

services:
  app:
    build: .
    env_file:
      - .env.${ENVIRONMENT:-development}
    ports:
      - "${PORT:-8000}:8000"
```

**使用**：

```bash
# 开发环境
docker-compose up

# 生产环境
ENVIRONMENT=production docker-compose up
```

## Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: faster-app-config
data:
  DEBUG: "false"
  HOST: "0.0.0.0"
  PORT: "8000"
  DB_URL: "postgresql://user:pass@db:5432/app"
---
apiVersion: v1
kind: Secret
metadata:
  name: faster-app-secrets
type: Opaque
stringData:
  SECRET_KEY: "your-secret-key"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: faster-app
spec:
  template:
    spec:
      containers:
      - name: app
        image: faster-app:latest
        envFrom:
        - configMapRef:
            name: faster-app-config
        - secretRef:
            name: faster-app-secrets
```

## 自定义配置

### 扩展配置类

```python
# config/settings.py
from faster_app.settings.config import DefaultSettings
from pydantic import Field

class CustomSettings(DefaultSettings):
    """自定义配置"""
    
    # 添加新配置项
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="REDIS_URL"
    )
    
    cache_ttl: int = Field(
        default=300,
        validation_alias="CACHE_TTL"
    )
    
    feature_flags: dict = Field(
        default_factory=dict,
        validation_alias="FEATURE_FLAGS"
    )

# 使用自定义配置
from config.settings import CustomSettings
configs = CustomSettings()
```

### 嵌套配置

```python
from pydantic import BaseModel, Field

class EmailConfig(BaseModel):
    """邮件配置"""
    smtp_host: str = Field(validation_alias="SMTP_HOST")
    smtp_port: int = Field(default=587, validation_alias="SMTP_PORT")
    smtp_user: str = Field(validation_alias="SMTP_USER")
    smtp_password: str = Field(validation_alias="SMTP_PASSWORD")
    from_email: str = Field(validation_alias="FROM_EMAIL")

class CustomSettings(DefaultSettings):
    # 嵌套配置
    email: EmailConfig = Field(default_factory=EmailConfig)

# 环境变量
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=user@example.com
# SMTP_PASSWORD=password
# FROM_EMAIL=noreply@example.com

# 访问
configs.email.smtp_host
configs.email.smtp_port
```

### 配置验证

```python
from pydantic import model_validator

class CustomSettings(DefaultSettings):
    redis_url: str = Field(validation_alias="REDIS_URL")
    
    @model_validator(mode="after")
    def validate_redis(self):
        """验证 Redis 配置"""
        if not self.debug:
            # 生产环境检查 Redis
            if "localhost" in self.redis_url:
                raise ValueError("生产环境不能使用 localhost Redis")
        return self
    
    @model_validator(mode="after")
    def validate_production(self):
        """生产环境验证"""
        if not self.debug:
            # 检查必需配置
            assert self.jwt.secret_key != "test-secret-key"
            assert self.middleware.cors_allow_origins != ["*"]
            assert self.middleware.trusted_host_enabled
        return self
```

## 密钥管理

### 环境变量注入

```bash
# 从密钥管理系统读取
export SECRET_KEY=$(vault kv get -field=secret_key secret/faster-app)
export DB_PASSWORD=$(vault kv get -field=password secret/faster-app)

# 启动应用
faster server start
```

### Docker Secrets

```yaml
version: '3.8'

services:
  app:
    image: faster-app:latest
    secrets:
      - secret_key
      - db_password
    environment:
      - SECRET_KEY_FILE=/run/secrets/secret_key
      - DB_PASSWORD_FILE=/run/secrets/db_password

secrets:
  secret_key:
    external: true
  db_password:
    external: true
```

### AWS Secrets Manager

```python
import boto3
import json

def get_secrets():
    """从 AWS Secrets Manager 读取密钥"""
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='faster-app/prod')
    return json.loads(response['SecretString'])

# 在应用启动时加载
secrets = get_secrets()
os.environ['SECRET_KEY'] = secrets['secret_key']
os.environ['DB_PASSWORD'] = secrets['db_password']
```

## 动态配置

### 运行时修改

```python
from faster_app.settings import configs

# 读取
current_level = configs.logging.level

# 运行时修改（谨慎使用）
configs.logging.level = "DEBUG"
```

### 配置热更新

```python
import signal

def reload_config(signum, frame):
    """重新加载配置"""
    global configs
    configs = CustomSettings()
    logger.info("配置已重新加载")

# 注册信号处理
signal.signal(signal.SIGHUP, reload_config)
```

## 配置文件格式

### YAML 配置（可选）

```python
import yaml

class YAMLSettings(DefaultSettings):
    @classmethod
    def from_yaml(cls, file_path: str):
        """从 YAML 文件加载"""
        with open(file_path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

# config.yaml
# debug: false
# server:
#   host: 0.0.0.0
#   port: 8000

configs = YAMLSettings.from_yaml('config.yaml')
```

### JSON 配置（可选）

```python
import json

class JSONSettings(DefaultSettings):
    @classmethod
    def from_json(cls, file_path: str):
        """从 JSON 文件加载"""
        with open(file_path) as f:
            data = json.load(f)
        return cls(**data)
```

## 最佳实践

### 1. 环境隔离

- 开发/预发布/生产环境完全隔离
- 使用不同的数据库和服务

### 2. 密钥安全

- 不要将密钥提交到 Git
- 使用密钥管理服务
- 定期轮换密钥

### 3. 配置验证

- 启动时验证所有必需配置
- 生产环境强制检查

### 4. 文档化

- 在 `.env.example` 中注释所有配置项
- 维护配置文档

### 5. 版本控制

- `.env` 加入 `.gitignore`
- `.env.example` 提交到 Git
- 配置模板版本化

通过合理的多环境配置和自定义扩展，可以灵活地管理不同场景下的应用配置。
