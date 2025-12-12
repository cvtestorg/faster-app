# Server 命令参考

`faster server` 命令组用于管理开发服务器。

## faster server start

启动开发服务器。

```bash
faster server start
```

**配置参数**（通过 `.env` 设置）：

```bash
# HOST: 服务器监听地址, 0.0.0.0 表示监听所有网络接口, 127.0.0.1 仅本地访问
HOST=0.0.0.0

# PORT: 服务器监听端口, 默认 8000, 可根据需要修改
PORT=8000

# DEBUG: 调试模式开关, True 开启详细错误信息, False 生产模式
DEBUG=True

# RELOAD: 热重载开关, True 开启代码变更自动重启, False 需要手动重启
RELOAD=True
```

**启动检测逻辑**：

1. 检查项目根目录是否存在 `main.py`
2. 如果存在，优先使用用户自定义配置
3. 否则使用框架内置配置

**输出示例**：

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started reloader process [12345]
INFO:     Application startup complete.
```

**使用场景**：

- 本地开发
- 调试 API
- 查看 Swagger 文档

更多详细内容...
