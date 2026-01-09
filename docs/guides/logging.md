# 统一日志格式指南

## 概述

为了便于问题排查和日志分析,项目采用了统一的日志格式规范。所有日志消息都遵循 `[操作类型] 资源=值 状态=值 详情=值` 的格式。

## 日志格式规范

### 标准格式

```
[操作类型] 资源=资源标识 状态=状态值 键=值 ...
```

### 格式说明

- **操作类型**: 用方括号 `[]` 包裹,描述当前操作(如：`[应用启动]`, `[创建记录]`, `[异常处理]`)
- **资源**: 使用 `资源=值` 格式,标识操作的资源(如：`应用=demo`, `Demo=123`)
- **状态**: 使用 `状态=值` 格式,描述操作状态(如：`状态=成功`, `状态=失败`)
- **详情**: 使用 `键=值` 格式,提供额外信息(如：`错误=xxx`, `数量=5`)

## 使用示例

### 基础用法

```python
from faster_app.settings import logger

# 简单操作
logger.info("[应用启动] 应用=demo 状态=成功")

# 带详情
logger.info("[创建记录] Demo=123 状态=成功 name=test")

# 错误日志
logger.error("[应用启动] 应用=demo 状态=失败 错误=连接超时", exc_info=True)
```

### 使用统一日志工具(推荐)

```python
from faster_app.utils.logger import log_info, log_error, log_warning

# 使用统一格式工具
log_info(
    action="启动应用",
    resource="应用",
    resource_id="demo",
    status="成功"
)
# 输出: [启动应用] 应用=demo 状态=成功

log_error(
    action="创建记录",
    resource="Demo",
    resource_id="123",
    status="失败",
    details={"error": "名称已存在"},
    exc_info=True
)
# 输出: [创建记录] Demo=123 状态=失败 error=名称已存在
```

## 常见操作类型

- `[应用启动]` - 应用启动相关
- `[应用关闭]` - 应用关闭相关
- `[生命周期]` - 生命周期管理
- `[异常处理]` - 异常处理
- `[请求验证]` - 请求验证
- `[HTTP异常]` - HTTP 异常
- `[应用初始化]` - 应用初始化
- `[创建记录]` - 创建操作
- `[更新记录]` - 更新操作
- `[删除记录]` - 删除操作

## 日志级别使用

- **DEBUG**: 详细的调试信息
- **INFO**: 一般信息,记录正常流程
- **WARNING**: 警告信息,不影响功能但需要注意
- **ERROR**: 错误信息,需要关注和修复

## 日志配置

日志格式支持两种模式：

1. **STRING 模式**(默认): 人类可读的文本格式

   ```
   2025-01-XX 10:30:45 [INFO] [faster_app.apps.registry:115] startup_all: [应用启动] 应用=demo 状态=成功
   ```

2. **JSON 模式**: 结构化 JSON 格式,便于日志分析工具处理

   ```json
   {
     "timestamp": "2025-01-XXT10:30:45.123456+00:00",
     "level": "INFO",
     "logger": "faster_app.apps.registry",
     "module": "registry",
     "function": "startup_all",
     "line": 115,
     "message": "[应用启动] 应用=demo 状态=成功",
     "pathname": "/path/to/file.py",
     "process_id": 12345,
     "thread_id": 67890,
     "event": "应用启动",
     "resource_type": "应用",
     "resource_id": "demo",
     "status": "成功"
   }
   ```

   **注意**: JSON 格式中,结构化字段(event, resource_type, resource_id, status 等)会作为顶级字段,
   可以直接查询,无需解析 message 字符串。这是日志最佳实践。

通过环境变量可以配置日志：

- `LOG_FORMAT=JSON` - 切换到 JSON 格式
- `LOG_TO_FILE=true` - 启用文件日志输出
- `LOG_FILE_PATH=logs/app.log` - 日志文件路径(相对项目根目录或绝对路径)
- `LOG_FILE_MAX_BYTES=10485760` - 单个日志文件最大大小(字节,默认 10MB)
- `LOG_FILE_BACKUP_COUNT=5` - 保留的备份文件数量(默认 5 个)

### 日志滚动配置

当启用文件日志时,会自动配置日志滚动(TimedRotatingFileHandler)：

- **滚动策略**: 按天归档,每天午夜自动滚动
- **备份文件**: 默认保留 10 天的日志文件
- **文件命名**: `app.log`, `app.log.2025-01-XX`, `app.log.2025-01-YY` 等(按日期后缀)
- **文件编码**: UTF-8

**示例配置**(`.env` 文件):

```env
# 启用文件日志
LOG_TO_FILE=true

# 日志文件路径(相对于项目根目录或绝对路径)
LOG_FILE_PATH=logs/app.log

# 保留 10 天的日志文件(默认)
LOG_FILE_BACKUP_COUNT=10

# 使用 JSON 格式
LOG_FORMAT=JSON
```

**日志文件示例**:

```
logs/
├── app.log                    # 当前日志文件
├── app.log.2025-01-20        # 2025-01-20 的日志
├── app.log.2025-01-19        # 2025-01-19 的日志
└── ...
```

每天午夜(00:00)会自动创建新的日志文件,旧文件会按日期重命名。

## 最佳实践

1. **统一格式**: 所有日志消息都使用统一的格式,便于搜索和分析
2. **包含上下文**: 日志消息应包含足够的上下文信息(资源、状态、错误等)
3. **结构化数据**: 使用键值对格式,便于日志分析工具解析
4. **错误详情**: 错误日志应包含 `exc_info=True` 以记录完整的堆栈信息
5. **避免敏感信息**: 不要在日志中记录密码、token 等敏感信息

## 问题排查

使用统一格式后,可以通过以下方式快速定位问题：

```bash
# 查找特定应用的启动日志
grep "\[应用启动\] 应用=demo" logs/app.log

# 查找所有错误
grep "状态=失败" logs/app.log

# 查找特定操作
grep "\[创建记录\]" logs/app.log
```

对于 JSON 格式,可以使用 `jq` 等工具进行查询：

```bash
# 查找所有错误
cat logs/app.log | jq 'select(.level == "ERROR")'

# 查找特定应用的日志(使用结构化字段,更高效)
cat logs/app.log | jq 'select(.resource_id == "demo")'

# 查找特定事件类型
cat logs/app.log | jq 'select(.event == "应用启动")'

# 查找失败的操作
cat logs/app.log | jq 'select(.status == "失败")'

# 组合查询：查找特定应用的所有失败操作
cat logs/app.log | jq 'select(.resource_id == "demo" and .status == "失败")'
```

**优势**: JSON 格式中,结构化字段作为顶级字段,查询效率远高于字符串匹配。
