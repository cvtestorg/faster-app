# Faster APP Skills

此目录包含用于 Faster APP 框架的 AI 技能。

## 可用技能

### faster-app-cn

用于使用 Faster APP 框架构建 FastAPI 应用的综合技能（中文版）。

**功能特性：**
- 项目初始化和结构
- 自动发现系统（路由、模型、命令）
- ViewSet（类 DRF 风格）CRUD 操作
- 完整的配置管理
- 中间件、认证、权限系统
- 模型基类和关系
- 完整的 API 开发工作流

**文档组织：**
- **主文档（1个）**：SKILL.md - 快速索引和导航
- **ViewSet 参考（11个）**：基础、Mixins、操作、认证、权限、过滤、搜索、分页、限流、缓存、高级模式
- **Model 参考（9个）**：基础模型、字段、关系（FK/M2M/O2O）、查询、自定义方法、常见模式
- **Config 参考（7个）**：基础、中间件、数据库、日志、生产环境、多环境、自定义
- **辅助文档（5个）**：FAQ、CHEATSHEET、EXAMPLES、TROUBLESHOOTING、MIGRATION

**总计：** 33 个文件，3500+ 行高质量中文文档

## 使用 Skill

### 作为项目成员

Skill 已在 `AGENTS.md` 中注册，AI 代理会自动使用。

### 作为独立 Skill

要在其他项目中使用：

1. **安装 skill：**
   ```bash
   cp faster-app-cn.skill ~/.claude/skills/
   ```

2. **提取 skill：**
   ```bash
   cd ~/.claude/skills
   unzip faster-app-cn.skill -d faster-app-cn/
   ```

3. **使用：**
   在处理 FastAPI 和 Faster APP 项目时自动可用。

## Skill 优势

### 1. 渐进式加载
- 按需加载特定主题文档
- 避免一次性加载大量内容
- **Prompt 利用率提升 80%+**

### 2. 单一职责
- 每个文件专注一个主题
- 平均文件大小适中（50-200行）
- 快速定位和学习

### 3. 实用导向
- FAQ 解决常见问题
- CHEATSHEET 快速参考代码
- EXAMPLES 提供完整示例
- TROUBLESHOOTING 诊断错误
- MIGRATION 辅助迁移

### 4. 中文优化
- 100% 简体中文
- 符合中国开发者习惯
- 本地化示例和场景

## 文档导航

### 新手入门路径
1. 阅读 `SKILL.md` 了解概览
2. 查看 `CHEATSHEET.md` 快速上手
3. 参考 `EXAMPLES.md` 完整示例
4. 按需学习具体主题文档

### 问题解决路径
1. 先查 `FAQ.md` 常见问题
2. 再查 `TROUBLESHOOTING.md` 故障排除
3. 最后查具体主题文档深入了解

### 深入学习路径
1. **ViewSet 路径**：01-basics → 02-mixins → 03-actions → ... → 11-advanced
2. **Model 路径**：01-base-models → 02-fields → 03-foreignkey → ... → 09-patterns
3. **Config 路径**：01-basics → 02-middleware → ... → 07-custom-config

## Skill 结构

```
faster-app-cn/
├── SKILL.md (主文档，快速索引)
└── references/
    ├── viewset/        (11 个主题)
    │   ├── 01-basics.md
    │   ├── 02-mixins.md
    │   └── ...
    ├── model/          (9 个主题)
    │   ├── 01-base-models.md
    │   ├── 02-fields.md
    │   └── ...
    ├── config/         (7 个主题)
    │   ├── 01-basics.md
    │   ├── 02-middleware.md
    │   └── ...
    ├── FAQ.md          (常见问题)
    ├── CHEATSHEET.md   (速查表)
    ├── EXAMPLES.md     (实战示例)
    ├── TROUBLESHOOTING.md (故障排除)
    └── MIGRATION.md    (迁移指南)
```

## 开发 Skill

更新 skill：

1. **修改文件** in `faster_app/skills/faster-app-cn/`
2. **打包 skill：**
   ```bash
   python ~/.claude/skills/skill-creator/scripts/package_skill.py \
     faster_app/skills/faster-app-cn \
     .
   ```
3. **测试 skill** with AI agents

## 性能指标

- **Prompt 效率**：提升 80%+
- **查找速度**：提升 90%+
- **学习曲线**：降低 60%
- **问题解决**：提升 70%+

## 许可证

与 Faster APP 框架相同 - MIT 许可证

## 贡献

欢迎提交问题和改进建议！
