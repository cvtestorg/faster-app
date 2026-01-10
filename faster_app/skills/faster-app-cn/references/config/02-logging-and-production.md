# 日志和生产环境

配置日志系统和准备生产环境部署。

## 日志配置

### 基础配置

```bash
# 日志级别
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# 日志格式
LOG_FORMAT=STRING  # STRING 或 JSON

# 文件日志
LOG_TO_FILE=false
LOG_FILE_PATH=logs/app.log
LOG_FILE_MAX_BYTES=10485760  # 10MB
LOG_FILE_BACKUP_COUNT=10
```

### 日志级别说明

- **DEBUG** - 详细的调试信息（开发环境）
- **INFO** - 一般信息（默认，适合生产环境）
- **WARNING** - 警告信息
- **ERROR** - 错误信息
- **CRITICAL** - 严重错误

### 日志格式

**STRING 格式**（易读）：

```
2024-01-09 10:30:45 - INFO - faster_app.routes.discover - 发现路由: /api/users
```

**JSON 格式**（结构化，适合日志分析）：

```json
{
  "timestamp": "2024-01-09T10:30:45.123Z",
  "level": "INFO",
  "logger": "faster_app.routes.discover",
  "message": "发现路由: /api/users"
}
```

### 代码中使用日志

```python
from faster_app.utils.logger import logger

# 不同级别的日志
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")

# 带异常信息
try:
    result = await some_operation()
except Exception as e:
    logger.error(f"操作失败: {e}", exc_info=True)
```

### 文件日志配置

```bash
# 启用文件日志
LOG_TO_FILE=true
LOG_FILE_PATH=logs/app.log

# 日志轮转
LOG_FILE_MAX_BYTES=10485760      # 10MB
LOG_FILE_BACKUP_COUNT=10         # 保留 10 个备份

# 结果：
# logs/app.log
# logs/app.log.1
# logs/app.log.2
# ...
```

### 生产环境日志建议

```bash
# 生产环境配置
LOG_LEVEL=WARNING    # 只记录警告和错误
LOG_FORMAT=JSON      # 结构化日志
LOG_TO_FILE=true     # 启用文件日志
LOG_FILE_PATH=/var/log/faster-app/app.log
```

## 生产环境检查清单

### 1. 安全配置

```bash
# ✅ 必须修改
SECRET_KEY=使用强随机密钥  # 至少 32 字符

# ✅ 关闭调试模式
DEBUG=false

# ✅ 配置具体的 CORS 域名
CORS_ALLOW_ORIGINS=["https://example.com"]
CORS_ALLOW_CREDENTIALS=true

# ✅ 启用 TrustedHost
TRUSTED_HOST_ENABLED=true
TRUSTED_HOSTS=["example.com","*.example.com"]

# ✅ 使用 HTTPS
# 在反向代理（Nginx/Traefik）配置 SSL
```

### 2. 数据库配置

```bash
# ✅ 使用生产数据库
DB_URL=postgresql://user:pass@db-server:5432/production_db

# ✅ 配置连接池
DB_URL=postgresql://user:pass@db-server:5432/production_db?min_size=2&max_size=10

# ✅ 定期备份数据库
# 使用 pg_dump / mysqldump 等工具
```

### 3. 日志配置

```bash
# ✅ 合适的日志级别
LOG_LEVEL=WARNING  # 或 INFO

# ✅ 结构化日志
LOG_FORMAT=JSON

# ✅ 文件日志
LOG_TO_FILE=true
LOG_FILE_PATH=/var/log/faster-app/app.log

# ✅ 日志轮转
LOG_FILE_MAX_BYTES=10485760
LOG_FILE_BACKUP_COUNT=10
```

### 4. 性能配置

```bash
# ✅ 启用 GZip
GZIP_ENABLED=true

# ✅ 配置限流
THROTTLE_RATES='{"user":"1000/hour","anon":"100/hour"}'

# ✅ 使用生产级 ASGI 服务器
# Uvicorn with workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# 或 Gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### 5. 监控配置

```bash
# ✅ 健康检查端点
# 访问 /health 检查应用状态

# ✅ 配置监控工具
# - Prometheus + Grafana
# - Sentry（错误追踪）
# - NewRelic / DataDog
```

## 部署方式

### Docker 部署

**Dockerfile**：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY pyproject.toml ./
RUN pip install .

# 复制代码
COPY . .

# 设置环境变量
ENV DEBUG=false
ENV HOST=0.0.0.0
ENV PORT=8000

# 启动应用
CMD ["faster", "server", "start"]
```

**docker-compose.yml**：

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - SECRET_KEY=${SECRET_KEY}
      - DB_URL=postgresql://user:pass@db:5432/app
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=app
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Systemd 服务

**`/etc/systemd/system/faster-app.service`**：

```ini
[Unit]
Description=Faster APP Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/faster-app
Environment="PATH=/opt/faster-app/.venv/bin"
EnvironmentFile=/opt/faster-app/.env
ExecStart=/opt/faster-app/.venv/bin/faster server start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Nginx 反向代理

```nginx
server {
    listen 80;
    server_name example.com;
    
    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com;
    
    # SSL 配置
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # 反向代理
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 静态文件（如果有）
    location /static {
        alias /opt/faster-app/static;
        expires 30d;
    }
}
```

## 监控和告警

### 健康检查

```python
# Faster APP 自动提供健康检查端点
# GET /health
{
    "status": "healthy",
    "database": "connected",
    "timestamp": "2024-01-09T10:30:45Z"
}
```

### 错误追踪（Sentry）

```bash
# 安装
uv add sentry-sdk

# 配置
export SENTRY_DSN=https://xxx@sentry.io/xxx
```

```python
# config/settings.py
import sentry_sdk

if not configs.debug and configs.sentry_dsn:
    sentry_sdk.init(
        dsn=configs.sentry_dsn,
        environment="production"
    )
```

### 性能监控

```bash
# 使用 Prometheus
uv add prometheus-fastapi-instrumentator

# 访问指标端点
# GET /metrics
```

## 备份策略

### 数据库备份

```bash
# PostgreSQL
pg_dump -U user -d database > backup_$(date +%Y%m%d).sql

# MySQL
mysqldump -u user -p database > backup_$(date +%Y%m%d).sql

# 定时备份（crontab）
0 2 * * * /path/to/backup.sh
```

### 配置备份

```bash
# 备份 .env 文件
cp .env .env.backup

# 版本控制配置模板
git add .env.example
```

## 性能优化

### 1. 数据库优化

- 添加索引
- 使用连接池
- 优化查询（避免 N+1）

### 2. 缓存

- Redis 缓存查询结果
- CDN 缓存静态资源

### 3. 负载均衡

```bash
# 多个 worker
uvicorn main:app --workers 4

# Nginx 负载均衡
upstream faster_app {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

通过合理的日志配置和生产环境优化，确保应用稳定运行。
