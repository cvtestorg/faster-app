# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2026-01-02

### 🎉 首个主要版本发布

这是 Faster APP 框架的第一个主要版本，包含重大重构、性能优化和多项改进。

### ⚠️ 重大变更 (Breaking Changes)

#### Exceptions 模块

- **移除**: `register_exception_handlers()` 函数
- **替代**: 使用 `get_manager().apply(app)` 注册异常处理器
- **原因**: 保持代码干净现代，避免冗余的向后兼容代码

```python
# ❌ 旧方式（已移除）
from faster_app.exceptions import register_exception_handlers
register_exception_handlers(app)

# ✅ 新方式
from faster_app.exceptions import get_manager
get_manager().apply(app)
```

### ✨ 新增功能

#### Exceptions 模块

- 引入 `ExceptionManager` 类，提供灵活的异常处理器管理
- 异常类型定义大幅简化（使用类属性替代 `__init__` 方法）
- 添加 `__repr__()` 方法，改进调试体验
- 统一异常处理逻辑，提取公共函数 `_create_error_response()`
- 改进类型注解，提供更好的 IDE 支持

#### Lifespan 模块

- 引入 `LifespanManager` 类，提供统一的生命周期管理
- 支持通过配置控制 lifespan 启用/禁用
- 支持通过参数动态控制 lifespan
- 使用 `@lru_cache` 优化用户 lifespan 发现性能
- 简化 `LifespanDiscover` 的函数检查逻辑

#### Apps 模块

- 添加 `AppRegistry.has_apps()` 方法
- 添加 `AppRegistry.app_count` 属性
- 优化 `list_apps()` 方法，支持在启动前返回应用列表
- 简化 `register()` 方法，移除冗余的依赖验证
- 优化 `shutdown_all()` 方法，添加空列表检查

### 🔧 优化改进

#### 代码简化

- **Exceptions**: 异常类型代码量减少 70%
- **Exceptions**: 异常处理器代码量减少 50%
- **Lifespan**: 移除冗余注释和文档字符串
- **Apps**: 简化注册和关闭逻辑

#### 性能优化

- 使用 `@lru_cache` 缓存用户 lifespan 发现结果
- 优化中间件缓存机制
- 改进错误处理和日志记录

#### 代码质量

- 完善类型注解
- 统一代码风格
- 提取公共逻辑，减少重复
- 改进错误消息和日志输出

### 📚 文档更新

- 新增 `docs/guides/exceptions.md` - 异常处理完整指南
- 新增 `docs/guides/lifespan.md` - Lifespan 生命周期管理指南
- 新增配置示例和高级定制示例
- 更新 `OPTIMIZATION_REPORT.md` 优化报告

### 🐛 Bug 修复

#### 导入路径修复

- **修复模块导入错误**: 将 `apps.demo.*` 导入路径更正为 `faster_app.apps.demo.*`，解决 `ModuleNotFoundError` 问题
- **影响文件**: `faster_app/apps/demo/routes.py`, `faster_app/apps/demo/auth_routes.py`

#### 跨平台兼容性

- **Windows 路径支持**: 修复 `models/discover.py` 中硬编码路径分隔符问题，使用 `os.sep` 实现跨平台兼容
- **影响**: 现在可以在 Windows、macOS 和 Linux 上正确工作

### ✅ 测试

- ✅ 异常模块完整测试
- ✅ Lifespan 模块完整测试
- ✅ Apps 模块完整测试
- ✅ 完整应用集成测试

---

## [Unreleased]

### 计划中的功能

- 更多性能优化
- 扩展的文档和示例
- 社区反馈的改进

---

## 升级指南

### 从旧版本升级

#### 1. 更新异常处理器注册

```python
# 旧代码
from faster_app.exceptions import register_exception_handlers
register_exception_handlers(app)

# 新代码
from faster_app.exceptions import get_manager
get_manager().apply(app)
```

#### 2. 异常类型使用方式不变

```python
# 使用方式完全相同
from faster_app.exceptions import NotFoundError

raise NotFoundError()
raise NotFoundError("用户不存在")
raise NotFoundError("用户不存在", error_detail="详细信息")
```

#### 3. Lifespan 使用方式不变

默认行为完全相同，无需修改现有代码。

如需自定义，参考 `docs/guides/lifespan.md`。

---

## 贡献者

- 优化和重构: AI Assistant
- 测试和验证: 项目团队
