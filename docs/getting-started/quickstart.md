# 快速入门

本页面将带你在 5 分钟内创建第一个 Faster APP 应用。

## 创建项目

首先，让我们创建一个新项目：

```bash
# 使用 uv 创建项目
uv init my-blog
cd my-blog

# 安装 Faster APP
uv add faster-app

# 移除默认的 main.py
rm main.py
```

## 初始化应用

使用内置命令快速搭建项目结构：

```bash
# 创建示例应用
faster app demo

# 创建配置文件
faster app config
faster app env
```

此时项目结构如下：

```
my-blog/
├── apps/
│   └── demo/
│       ├── models.py      # 数据模型
│       ├── routes.py      # API 路由
│       ├── schemas.py     # Pydantic 模型
│       ├── commands.py    # 命令行工具
│       └── tasks.py       # 异步任务
├── config/
│   └── settings.py        # 自定义配置
├── .env                   # 环境变量
└── pyproject.toml
```

## 初始化数据库

```bash
# 初始化数据库迁移
faster db init

# 创建数据库表
faster db init_db
```

## 启动服务器

```bash
faster server start
```

看到如下输出表示启动成功：

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## 访问 API

打开浏览器访问：

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

你会看到自动生成的 API 文档！

## 创建你的第一个模型

编辑 `apps/demo/models.py`：

```python
from faster_app.models.base import UUIDModel, DateTimeModel

# UUIDModel: 提供 id 字段(UUID 类型)和基础 CRUD 方法
# DateTimeModel: 提供 created_at 和 updated_at 时间戳字段
class Article(UUIDModel, DateTimeModel):
    """文章模型"""

    # Field(..., max_length=200): ... 表示必填字段, max_length 限制最大长度
    title: str = Field(..., max_length=200, description="标题")
    # Field(..., description="..."): description 用于 API 文档说明
    content: str = Field(..., description="内容")
    author: str = Field(..., max_length=50, description="作者")

    class Meta:
        # table: 指定数据库表名, 默认使用类名的小写形式
        table = "articles"
```

## 创建数据库迁移

```bash
# 生成迁移文件
faster db migrate --name="add_article_model"

# 执行迁移
faster db upgrade
```

## 创建 API 路由

编辑 `apps/demo/routes.py`：

```python
from fastapi import APIRouter
from faster_app.utils.response import success_response
from .models import Article
from .schemas import ArticleCreate, ArticleResponse

# prefix: 路由前缀, 所有路由都会添加此前缀
# tags: API 标签, 用于在 Swagger UI 中分组显示
router = APIRouter(prefix="/articles", tags=["文章"])

# response_model: 响应模型, 定义返回数据的结构
@router.post("", response_model=ArticleResponse)
async def create_article(data: ArticleCreate):
    """创建文章
    Args:
        data: ArticleCreate 对象, 包含 title, content, author 字段
    Returns:
        ArticleResponse: 创建成功的文章对象
    """
    # **data.dict(): 将 Pydantic 模型转换为字典并解包
    article = await Article.create(**data.dict())
    # success_response: 统一响应格式, data 参数为返回的数据
    return success_response(data=article)

# response_model: list[ArticleResponse] 表示返回文章列表
@router.get("", response_model=list[ArticleResponse])
async def list_articles():
    """文章列表
    Returns:
        list[ArticleResponse]: 文章列表
    """
    # Article.all(): 获取所有文章记录
    articles = await Article.all()
    return success_response(data=articles)

# {article_id}: 路径参数, 从 URL 中提取文章 ID
@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: str):
    """获取文章详情
    Args:
        article_id: 文章 ID, UUID 格式字符串
    Returns:
        ArticleResponse: 文章详情对象
    """
    # Article.get(id=article_id): 根据 ID 查询单条记录
    article = await Article.get(id=article_id)
    return success_response(data=article)
```

## 创建 Pydantic 模型

编辑 `apps/demo/schemas.py`：

```python
from pydantic import BaseModel, Field

# BaseModel: Pydantic 基础模型, 提供数据验证和序列化功能
class ArticleCreate(BaseModel):
    """创建文章请求模型"""
    # Field(..., max_length=200): ... 表示必填, max_length 限制最大长度 200 字符
    title: str = Field(..., max_length=200, description="标题")
    # Field(..., description="..."): description 用于 API 文档说明
    content: str = Field(..., description="文章内容")
    author: str = Field(..., max_length=50, description="作者名称, 最大长度 50 字符")

# 响应模型, 包含所有字段包括自动生成的 id 和时间戳
class ArticleResponse(BaseModel):
    """文章响应模型"""
    id: str              # UUID 格式的文章 ID
    title: str           # 文章标题
    content: str         # 文章内容
    author: str          # 作者名称
    created_at: datetime # 创建时间, 由 DateTimeModel 自动生成
    updated_at: datetime # 更新时间, 由 DateTimeModel 自动更新

    class Config:
        # from_attributes: 允许从 ORM 对象创建 Pydantic 模型
        from_attributes = True
```

## 测试 API

路由会自动被发现并注册，无需手动配置！刷新 [http://localhost:8000/docs](http://localhost:8000/docs)，你会看到新的 API 端点。

使用 curl 测试：

```bash
# -X POST: 指定 HTTP 方法为 POST
# -H "Content-Type: application/json": 设置请求头, 指定 JSON 格式
# -d '{...}': 请求体数据, JSON 格式
curl -X POST "http://localhost:8000/articles" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "我的第一篇文章",    # 文章标题
    "content": "这是文章内容",    # 文章内容
    "author": "张三"              # 作者名称
  }'

# GET 请求, 获取文章列表, 无需参数
curl "http://localhost:8000/articles"
```

## 创建自定义命令

编辑 `apps/demo/commands.py`：

```python
from faster_app.commands.base import BaseCommand
from .models import Article

# BaseCommand: 命令基类, 提供命令注册和参数解析功能
class ArticleCommand(BaseCommand):
    """文章管理命令"""

    # 无参数方法, 通过 faster article count 调用
    async def count(self):
        """统计文章数量"""
        # Article.all(): 获取所有文章查询集
        # .count(): 统计查询集数量, 返回整数
        count = await Article.all().count()
        print(f"总共有 {count} 篇文章")

    # 无参数方法, 通过 faster article clear 调用
    async def clear(self):
        """清空所有文章"""
        # Article.all().delete(): 删除所有文章记录, 谨慎使用
        await Article.all().delete()
        print("已清空所有文章")
```

运行命令：

```bash
# faster article count: 统计文章数量, 无参数
faster article count

# faster article clear: 清空所有文章, 无参数, 谨慎使用
faster article clear
```

## 下一步

恭喜！你已经创建了第一个 Faster APP 应用。接下来可以：

- 📖 阅读 [项目结构](structure.md) 了解目录组织
- 🔍 深入 [API 模块概览](../api/overview.md)
- 🗄️ 探索 [模型基类](../api/models.md) 的强大功能
- 🛠️ 查看 [命令行工具](../cli/app.md) 完整参考

## 示例项目

查看完整的示例项目：

- [博客系统](https://github.com/mautops/faster-app/examples/blog)
- [电商后台](https://github.com/mautops/faster-app/examples/shop)
- [Todo 应用](https://github.com/mautops/faster-app/examples/todo)
