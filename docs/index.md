---
title: Faster APP
description: FastAPI 最佳实践框架 - 约定优于配置
hide:
  - navigation
  - toc
---

<div class="home-page"></div>

<div class="home-hero">
  <div class="hero-content">
    <h1>🚀 Faster APP</h1>
    <p class="hero-subtitle">FastAPI 最佳实践框架 - 约定优于配置</p>
    <p class="hero-description">为 FastAPI 带来 Django 风格的项目结构和开发体验</p>
    <div class="hero-cta">
      <a class="btn btn-primary" href="getting-started/installation/">快速开始</a>
      <a class="btn btn-secondary" href="cli/app.md">命令行参考</a>
      <a class="btn btn-outline" href="api/overview.md">API 参考</a>
    </div>
  </div>
</div>

<div class="why-section">
  <h2>🎯 为什么选择 Faster APP?</h2>
  <div class="why-content">
    <p class="why-intro">FastAPI 非常灵活, 但这种灵活性也带来了问题: 项目结构混乱、重复造轮子、配置复杂、缺乏约定.</p>
    <div class="why-solution">
      <strong>Faster APP 的解决方案</strong>: 借鉴 Django 的成功经验, 为 FastAPI 制定一套标准化的项目结构和开发约定, 实现 <strong>约定优于配置</strong>.
    </div>
  </div>
</div>

## ✨ 核心特性

<div class="home-grid">
  <article class="card">
    <div class="card-icon">🏗️</div>
    <h3>标准化项目结构</h3>
    <p>Django 风格的应用模块组织, 清晰统一的目录结构, 提升团队协作效率.</p>
    <a href="getting-started/structure.md">查看结构 →</a>
  </article>
  
  <article class="card">
    <div class="card-icon">🔍</div>
    <h3>智能自动发现</h3>
    <p>自动发现路由、模型、命令、中间件, 实现项目 0 配置启动.</p>
    <a href="api/overview.md">了解详情 →</a>
  </article>
  
  <article class="card">
    <div class="card-icon">🗄️</div>
    <h3>企业级模型基类</h3>
    <p>UUIDModel、DateTimeModel、StatusModel、ScopeModel, 覆盖 90% 业务场景.</p>
    <a href="api/models.md">查看模型 →</a>
  </article>
  
  <article class="card">
    <div class="card-icon">🛠️</div>
    <h3>Django 风格命令行</h3>
    <p>完整的 CLI 工具集, 支持应用管理、数据库迁移、服务器启动等操作.</p>
    <a href="cli/app.md">命令参考 →</a>
  </article>
  
  <article class="card">
    <div class="card-icon">🛣️</div>
    <h3>路由自动管理</h3>
    <p>自动发现和注册路由, 支持 CRUD Router, 简化 API 开发流程.</p>
    <a href="api/routes.md">路由管理 →</a>
  </article>
  
  <article class="card">
    <div class="card-icon">⚙️</div>
    <h3>配置自动发现</h3>
    <p>自动合并多个配置类, 从 .env 读取配置, 简化配置管理.</p>
    <a href="api/app.md">应用核心 →</a>
  </article>
</div>

## 🚀 快速开始

<div class="quick-start">
  <div class="quick-start-step">
    <div class="step-number">1</div>
    <h4>安装</h4>
    <pre><code>uv add faster-app
# 或
pip install faster-app</code></pre>
  </div>
  
  <div class="quick-start-step">
    <div class="step-number">2</div>
    <h4>创建项目</h4>
    <pre><code>uv init my-project && cd my-project
faster app demo</code></pre>
  </div>
  
  <div class="quick-start-step">
    <div class="step-number">3</div>
    <h4>启动服务器</h4>
    <pre><code>faster server start</code></pre>
  </div>
</div>

<div class="success-message">
  ✅ <strong>完成!</strong> 访问 <a href="http://localhost:8000" target="_blank">http://localhost:8000</a> 查看你的 FastAPI 应用
</div>

## 🎓 学习路径

<div class="learning-paths">
  <div class="path-card">
    <h4>👋 我是新用户</h4>
    <p>刚开始使用 Faster APP? 从这里开始:</p>
    <ol>
      <li><a href="getting-started/installation.md">安装 Faster APP</a></li>
      <li><a href="getting-started/quickstart.md">5 分钟快速入门</a></li>
      <li><a href="getting-started/structure.md">了解项目结构</a></li>
      <li><a href="api/overview.md">学习 API 模块</a></li>
    </ol>
  </div>
  
  <div class="path-card">
    <h4>👨‍💻 我是开发者</h4>
    <p>想要深入了解框架功能? 查看这些文档:</p>
    <ol>
      <li><a href="cli/app.md">命令行工具参考</a></li>
      <li><a href="api/models.md">模型基类详解</a></li>
      <li><a href="api/routes.md">路由管理指南</a></li>
      <li><a href="api/overview.md">API 参考文档</a></li>
    </ol>
  </div>
  
  <div class="path-card">
    <h4>❓ 遇到问题</h4>
    <p>需要帮助? 查看这些资源:</p>
    <ol>
      <li><a href="https://github.com/mautops/faster-app/issues">GitHub Issues</a></li>
      <li><a href="https://github.com/mautops/faster-app/discussions">GitHub Discussions</a></li>
      <li><a href="getting-started/index.md">快速开始指南</a></li>
      <li><a href="cli/app.md">命令行参考</a></li>
    </ol>
  </div>
</div>
