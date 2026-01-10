# 模型关系

Tortoise ORM 支持三种关系类型：ForeignKey（多对一）、ManyToMany（多对多）、OneToOne（一对一）。

## ForeignKey - 多对一关系

ForeignKey 用于建立多对一（Many-to-One）关系。

### 基础定义

```python
from tortoise import fields

class Author(UUIDModel):
    name: str = fields.CharField(max_length=100)

class Article(UUIDModel):
    title: str = fields.CharField(max_length=200)
    author: fields.ForeignKeyField = fields.ForeignKeyField(
        "models.Author",
        related_name="articles",
        on_delete=fields.CASCADE
    )
```

### 创建和查询

```python
# 创建
author = await Author.create(name="张三")
article = await Article.create(title="文章", author=author)

# 正向查询
article = await Article.get(id=id).prefetch_related("author")
print(article.author.name)

# 反向查询
author = await Author.get(id=id).prefetch_related("articles")
for article in author.articles:
    print(article.title)

# 跨关系查询
articles = await Article.filter(author__name="张三")
```

### on_delete 选项

- **CASCADE** - 级联删除
- **SET_NULL** - 设为 NULL（需要 null=True）
- **RESTRICT** - 限制删除
- **SET_DEFAULT** - 设为默认值

### 避免 N+1 查询

```python
# ❌ 错误：N+1 查询
articles = await Article.all()
for article in articles:
    print(article.author.name)  # 每次循环查询一次

# ✅ 正确：使用 prefetch_related
articles = await Article.all().prefetch_related("author")
for article in articles:
    print(article.author.name)  # 无额外查询
```

## ManyToMany - 多对多关系

ManyToMany 用于建立多对多关系，如文章和标签。

### 基础定义

```python
class Tag(UUIDModel):
    name: str = fields.CharField(max_length=50, unique=True)

class Article(UUIDModel):
    title: str = fields.CharField(max_length=200)
    tags: fields.ManyToManyField = fields.ManyToManyField(
        "models.Tag",
        related_name="articles",
        through="article_tags"
    )
```

### 添加和移除关系

```python
# 添加
article = await Article.create(title="Python 教程")
tag = await Tag.create(name="Python")
await article.tags.add(tag)

# 添加多个
tags = await Tag.filter(name__in=["Python", "FastAPI"])
await article.tags.add(*tags)

# 移除
await article.tags.remove(tag)

# 清空
await article.tags.clear()
```

### 查询

```python
# 正向查询
article = await Article.get(id=id).prefetch_related("tags")
for tag in article.tags:
    print(tag.name)

# 反向查询
tag = await Tag.get(name="Python").prefetch_related("articles")
for article in tag.articles:
    print(article.title)

# 跨关系查询
articles = await Article.filter(tags__name="Python")
```

### 自定义中间表

```python
class ArticleTag(UUIDModel):
    article: fields.ForeignKeyField = fields.ForeignKeyField("models.Article")
    tag: fields.ForeignKeyField = fields.ForeignKeyField("models.Tag")
    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "article_tags"
        unique_together = (("article", "tag"),)

# 访问中间表
article_tags = await ArticleTag.filter(article_id=article.id)
```

## OneToOne - 一对一关系

OneToOne 用于建立一对一关系，每个对象只能关联一个另一个对象。

### 基础定义

```python
class User(UUIDModel):
    username: str = fields.CharField(max_length=50, unique=True)

class Profile(UUIDModel):
    user: fields.OneToOneField = fields.OneToOneField(
        "models.User",
        related_name="profile",
        on_delete=fields.CASCADE
    )
    bio: str = fields.TextField(null=True)
```

### 创建和访问

```python
# 创建
user = await User.create(username="zhangsan")
profile = await Profile.create(user=user, bio="工程师")

# 正向访问
profile = await Profile.get(id=id).prefetch_related("user")
print(profile.user.username)

# 反向访问
user = await User.get(id=id).prefetch_related("profile")
print(user.profile.bio)
```

### 使用场景

1. **用户和个人资料** - 核心数据和扩展资料分离
2. **文章和详细内容** - 列表页只加载摘要，详情页加载完整内容
3. **产品和规格** - 基础信息和详细规格分离
4. **设置和配置** - 主对象和配置分离

### OneToOne vs ForeignKey

- **OneToOne**：双向唯一，用于数据分离、扩展
- **ForeignKey**：多对一，用于层级、分类关系

## 关系查询最佳实践

### 1. 总是使用 prefetch_related

```python
# 避免 N+1 查询
articles = await Article.all().prefetch_related(
    "author",
    "category",
    "tags"
)
```

### 2. 只查询需要的字段

```python
# 使用 values() 减少数据传输
articles = await Article.all().values(
    "id",
    "title",
    "author__name"
)
```

### 3. 批量操作

```python
# 批量添加关系
article = await Article.get(id=id)
tags = await Tag.filter(name__in=["tag1", "tag2"])
await article.tags.add(*tags)
```

### 4. 聚合统计

```python
from tortoise.functions import Count

# 统计每个作者的文章数
authors = await Author.annotate(
    article_count=Count("articles")
).values("name", "article_count")
```

### 5. 去重查询

```python
# 跨关系查询时去重
authors = await Author.filter(
    articles__status="published"
).distinct()
```

## 性能优化

### 问题：N+1 查询

```python
# ❌ 每次循环都查询数据库
articles = await Article.all()
for article in articles:
    print(article.author.name)      # 查询1次
    for tag in article.tags:         # 查询N次
        print(tag.name)
```

### 解决：预取关系

```python
# ✅ 只查询3次（articles + authors + tags）
articles = await Article.all().prefetch_related(
    "author",
    "tags"
)
for article in articles:
    print(article.author.name)       # 无查询
    for tag in article.tags:          # 无查询
        print(tag.name)
```

### 复杂预取

```python
# 预取嵌套关系
articles = await Article.all().prefetch_related(
    "author",
    "author__organization",
    "comments__user"
)
```

## 常见错误

### 1. 忘记 prefetch

```python
# ❌ N+1 问题
articles = await Article.all()

# ✅ 正确
articles = await Article.all().prefetch_related("author")
```

### 2. 在循环中查询

```python
# ❌ 错误
for id in article_ids:
    article = await Article.get(id=id)

# ✅ 正确
articles = await Article.filter(id__in=article_ids)
```

### 3. 不使用 distinct

```python
# ❌ 可能返回重复记录
authors = await Author.filter(articles__status="published")

# ✅ 正确
authors = await Author.filter(articles__status="published").distinct()
```

掌握这三种关系类型和最佳实践，可以高效地构建复杂的数据模型。
