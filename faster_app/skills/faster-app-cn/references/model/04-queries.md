# 数据查询

Tortoise ORM 提供丰富的查询 API，支持基础查询、高级过滤、聚合统计等操作。

## 基础查询方法

### all() - 获取所有记录

```python
articles = await Article.all()
articles = await Article.all().order_by("-created_at").limit(10)
```

### get() - 获取单条记录

```python
# 按 ID
article = await Article.get(id=article_id)

# 按其他字段
article = await Article.get(slug="python-tutorial")

# 不存在会抛出异常
try:
    article = await Article.get(id="不存在")
except Article.DoesNotExist:
    print("未找到")
```

### get_or_none() - 安全获取

```python
article = await Article.get_or_none(slug="python-tutorial")
if article:
    print(article.title)
```

### filter() - 过滤

```python
# 单条件
articles = await Article.filter(status="published")

# 多条件（AND）
articles = await Article.filter(status="published", author="张三")

# 链式过滤
articles = await Article.filter(status="published").filter(view_count__gt=100)
```

### exclude() - 排除

```python
articles = await Article.exclude(status="draft")
articles = await Article.exclude(status="draft").exclude(is_deleted=True)
```

### first() / count() / exists()

```python
# 第一条
article = await Article.filter(status="published").first()

# 计数
count = await Article.filter(status="published").count()

# 检查存在
has_articles = await Article.filter(author="张三").exists()
```

## 比较操作符

```python
# 精确匹配
articles = await Article.filter(status="published")

# 大于 / 大于等于
articles = await Article.filter(view_count__gt=100)
articles = await Article.filter(view_count__gte=100)

# 小于 / 小于等于
articles = await Article.filter(view_count__lt=100)
articles = await Article.filter(view_count__lte=100)

# 不等于
articles = await Article.filter(status__not="draft")

# 范围
from datetime import datetime, timedelta
start = datetime.now() - timedelta(days=7)
articles = await Article.filter(created_at__range=(start, datetime.now()))
```

## 字符串操作符

```python
# 包含（区分大小写）
articles = await Article.filter(title__contains="Python")

# 包含（不区分大小写）
articles = await Article.filter(title__icontains="python")

# 开始于
articles = await Article.filter(title__startswith="如何")

# 结束于
articles = await Article.filter(title__endswith="指南")
```

## 列表操作符

```python
# 在列表中
articles = await Article.filter(status__in=["published", "featured"])

# 不在列表中
articles = await Article.filter(status__not_in=["draft", "archived"])
```

## 空值检查

```python
# 为空
articles = await Article.filter(published_at__isnull=True)

# 不为空
articles = await Article.filter(published_at__isnull=False)
```

## 排序

```python
# 升序
articles = await Article.all().order_by("created_at")

# 降序
articles = await Article.all().order_by("-created_at")

# 多字段排序
articles = await Article.all().order_by("-is_featured", "-created_at")
```

## 限制和偏移

```python
# 限制数量
articles = await Article.all().limit(10)

# 偏移
articles = await Article.all().offset(20).limit(10)

# 切片
articles = await Article.all()[10:20]
```

## 值查询

### values() - 字典列表

```python
# 返回字典列表
articles = await Article.all().values("id", "title", "status")
# [{"id": "...", "title": "...", "status": "..."}, ...]

# 跨关系查询
articles = await Article.all().values("title", "author__name")
```

### values_list() - 元组列表

```python
# 返回元组列表
titles = await Article.all().values_list("title", flat=False)
# [("标题1",), ("标题2",), ...]

# flat=True 返回扁平列表
titles = await Article.all().values_list("title", flat=True)
# ["标题1", "标题2", ...]
```

## 去重

```python
# 去除重复
authors = await Article.all().distinct().values_list("author", flat=True)
```

## Q 对象 - 复杂查询

### OR 查询

```python
from tortoise.expressions import Q

# 状态为 published 或 featured
articles = await Article.filter(
    Q(status="published") | Q(status="featured")
)
```

### AND 查询

```python
# 等同于多个 filter
articles = await Article.filter(
    Q(status="published") & Q(view_count__gt=100)
)
```

### 复杂组合

```python
# (A AND B) OR C
articles = await Article.filter(
    (Q(status="published") & Q(view_count__gt=100)) |
    Q(is_featured=True)
)

# NOT 查询
articles = await Article.filter(~Q(status="draft"))
```

## 聚合查询

```python
from tortoise.functions import Count, Sum, Avg, Max, Min

# 计数
authors = await Author.annotate(
    article_count=Count("articles")
).values("name", "article_count")

# 求和
result = await Article.all().annotate(
    total_views=Sum("view_count")
).values("total_views")

# 平均值
result = await Article.filter(status="published").annotate(
    avg_rating=Avg("rating")
).values("avg_rating")

# 最大/最小值
result = await Article.all().annotate(
    max_views=Max("view_count"),
    min_views=Min("view_count")
).values("max_views", "min_views")
```

## 分组查询

```python
# 按状态分组统计
results = await Article.group_by("status").annotate(
    count=Count("id")
).values("status", "count")

# 多字段分组
results = await Article.group_by("author", "status").annotate(
    count=Count("id"),
    total_views=Sum("view_count")
).values("author", "status", "count", "total_views")
```

## 批量操作

### bulk_create() - 批量创建

```python
articles = [
    Article(title=f"文章{i}", content=f"内容{i}")
    for i in range(100)
]
await Article.bulk_create(articles)
```

### update() - 批量更新

```python
# 更新符合条件的记录
count = await Article.filter(status="draft").update(
    status="published",
    published_at=datetime.now()
)
```

### delete() - 批量删除

```python
deleted_count = await Article.filter(status="archived").delete()
```

## 原始 SQL

```python
from tortoise import Tortoise

# 获取连接
conn = Tortoise.get_connection("default")

# 执行查询
results = await conn.execute_query_dict(
    "SELECT author, COUNT(*) as count FROM articles GROUP BY author"
)

# 带参数（防止 SQL 注入）
results = await conn.execute_query_dict(
    "SELECT * FROM articles WHERE status = ? AND view_count > ?",
    ["published", 100]
)
```

## 事务

```python
from tortoise.transactions import in_transaction

# 自动事务
async with in_transaction():
    article = await Article.create(title="测试")
    await article.tags.add(tag1, tag2)
    # 如果出错，自动回滚
```

## 性能优化技巧

### 1. 只查询需要的字段

```python
# ❌ 查询所有字段
articles = await Article.all()

# ✅ 只查询需要的字段
articles = await Article.all().values("id", "title")
```

### 2. 使用 count() 而非 len()

```python
# ❌ 加载所有数据再计数
count = len(await Article.all())

# ✅ 数据库层面计数
count = await Article.all().count()
```

### 3. 使用 exists() 检查存在

```python
# ❌ 查询再判断
articles = await Article.filter(author="张三")
if articles:
    ...

# ✅ 直接检查存在
if await Article.filter(author="张三").exists():
    ...
```

### 4. 批量查询

```python
# ❌ 循环查询
articles = []
for id in ids:
    article = await Article.get(id=id)
    articles.append(article)

# ✅ 一次查询
articles = await Article.filter(id__in=ids)
```

### 5. 使用 prefetch_related

```python
# ❌ N+1 查询
articles = await Article.all()
for article in articles:
    print(article.author.name)  # 每次查询

# ✅ 预取关系
articles = await Article.all().prefetch_related("author")
for article in articles:
    print(article.author.name)  # 无查询
```

## 查询链式组合

```python
# 组合多个条件
articles = (
    await Article.filter(status="published")
    .exclude(is_deleted=True)
    .filter(view_count__gte=100)
    .prefetch_related("author", "tags")
    .order_by("-created_at")
    .limit(10)
)
```

## 调试查询

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 会打印执行的 SQL
articles = await Article.filter(status="published")
```

掌握这些查询方法，可以高效地操作数据库。
