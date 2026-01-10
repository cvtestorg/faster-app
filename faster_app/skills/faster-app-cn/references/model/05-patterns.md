# 自定义方法和常见模式

为模型添加自定义方法，封装业务逻辑，并使用常见设计模式。

## 自定义方法

### 实例方法

操作单个对象的方法：

```python
class Article(UUIDModel, DateTimeModel):
    title: str = fields.CharField(max_length=200)
    status: str = fields.CharField(max_length=20, default="draft")
    view_count: int = fields.IntField(default=0)
    
    async def publish(self):
        """发布文章"""
        self.status = "published"
        self.published_at = datetime.now()
        await self.save()
    
    async def increment_views(self):
        """增加浏览量"""
        self.view_count += 1
        await self.save(update_fields=["view_count"])
    
    async def can_edit_by(self, user_id: str) -> bool:
        """检查用户是否可以编辑"""
        if self.author_id == user_id:
            return True
        user = await User.get(id=user_id)
        return user.role == "admin"
```

### 类方法

操作整个模型类：

```python
class Article(UUIDModel, DateTimeModel):
    @classmethod
    async def get_published(cls):
        """获取所有已发布文章"""
        return await cls.filter(status="published").order_by("-published_at")
    
    @classmethod
    async def get_trending(cls, days: int = 7, limit: int = 10):
        """获取热门文章"""
        date_from = datetime.now() - timedelta(days=days)
        return await cls.filter(
            created_at__gte=date_from,
            status="published"
        ).order_by("-view_count").limit(limit)
    
    @classmethod
    async def search(cls, keyword: str):
        """搜索文章"""
        return await cls.filter(
            Q(title__icontains=keyword) | Q(content__icontains=keyword)
        ).filter(status="published")
```

### 属性方法

提供计算字段：

```python
class Article(UUIDModel, DateTimeModel):
    content: str = fields.TextField()
    status: str = fields.CharField(max_length=20)
    published_at: datetime = fields.DatetimeField(null=True)
    
    @property
    def is_published(self) -> bool:
        """是否已发布"""
        return self.status == "published"
    
    @property
    def word_count(self) -> int:
        """字数统计"""
        return len(self.content)
    
    @property
    def read_time(self) -> int:
        """阅读时间（分钟）"""
        words = len(self.content.split())
        return max(1, words // 200)
```

### 生命周期钩子

在保存/删除前后执行自定义逻辑：

```python
class Article(UUIDModel, DateTimeModel):
    title: str = fields.CharField(max_length=200)
    slug: str = fields.CharField(max_length=200, unique=True)
    
    async def save(self, *args, **kwargs):
        """保存前自动处理"""
        # 生成 slug
        if not self.slug:
            from slugify import slugify
            self.slug = slugify(self.title)
        
        # 调用父类 save
        await super().save(*args, **kwargs)
        
        # 保存后的操作
        await self.update_search_index()
    
    async def delete(self, *args, **kwargs):
        """删除前清理"""
        await self.cleanup_related_data()
        await super().delete(*args, **kwargs)
        await self.remove_from_search_index()
```

## 常见模式

### 软删除模式

不物理删除数据，标记为已删除：

```python
class Article(UUIDModel, DateTimeModel):
    title: str = fields.CharField(max_length=200)
    deleted_at: datetime = fields.DatetimeField(null=True)
    
    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
    
    async def soft_delete(self):
        """软删除"""
        self.deleted_at = datetime.now()
        await self.save(update_fields=["deleted_at"])
    
    async def restore(self):
        """恢复"""
        self.deleted_at = None
        await self.save(update_fields=["deleted_at"])
    
    @classmethod
    async def get_active(cls):
        """获取未删除的记录"""
        return await cls.filter(deleted_at__isnull=True)
```

### 版本控制模式

记录数据变更历史：

```python
class Article(UUIDModel, DateTimeModel):
    title: str = fields.CharField(max_length=200)
    version: int = fields.IntField(default=1)
    
    async def save(self, *args, **kwargs):
        """保存时自动增加版本号"""
        if self.id:  # 更新时
            self.version += 1
        await super().save(*args, **kwargs)

class ArticleHistory(UUIDModel):
    """历史记录"""
    article: fields.ForeignKeyField = fields.ForeignKeyField("models.Article")
    version: int = fields.IntField()
    title: str = fields.CharField(max_length=200)
    content: str = fields.TextField()
    changed_at: datetime = fields.DatetimeField(auto_now_add=True)
    changed_by: str = fields.CharField(max_length=100)
```

### 审计追踪模式

记录谁创建、谁修改：

```python
class AuditModel(UUIDModel):
    """审计基类"""
    created_by: str = fields.CharField(max_length=100)
    updated_by: str = fields.CharField(max_length=100)
    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    updated_at: datetime = fields.DatetimeField(auto_now=True)
    
    class Meta:
        abstract = True
    
    async def save(self, user_id: str = None, *args, **kwargs):
        """保存时记录操作者"""
        user_id = user_id or get_current_user_id()
        if not self.id:
            self.created_by = user_id
        self.updated_by = user_id
        await super().save(*args, **kwargs)

class Article(AuditModel):
    title: str = fields.CharField(max_length=200)
```

### 状态机模式

管理对象的状态转换：

```python
from enum import IntEnum

class ArticleStatus(IntEnum):
    DRAFT = 0
    UNDER_REVIEW = 1
    PUBLISHED = 2
    ARCHIVED = 3

class Article(UUIDModel, DateTimeModel):
    title: str = fields.CharField(max_length=200)
    status: int = fields.IntField(default=ArticleStatus.DRAFT)
    
    @property
    def status_name(self) -> str:
        return ArticleStatus(self.status).name
    
    async def submit_for_review(self, user_id: str):
        """提交审核"""
        if self.status != ArticleStatus.DRAFT:
            raise ValueError("只能提交草稿")
        self.status = ArticleStatus.UNDER_REVIEW
        await self.save()
        await self.notify_reviewers()
    
    async def publish(self, user_id: str):
        """发布"""
        if self.status != ArticleStatus.UNDER_REVIEW:
            raise ValueError("只能发布审核通过的文章")
        self.status = ArticleStatus.PUBLISHED
        self.published_at = datetime.now()
        await self.save()
    
    def can_transition_to(self, new_status: ArticleStatus) -> bool:
        """检查是否可以转换到新状态"""
        transitions = {
            ArticleStatus.DRAFT: [ArticleStatus.UNDER_REVIEW],
            ArticleStatus.UNDER_REVIEW: [ArticleStatus.PUBLISHED, ArticleStatus.DRAFT],
            ArticleStatus.PUBLISHED: [ArticleStatus.ARCHIVED],
            ArticleStatus.ARCHIVED: [],
        }
        return new_status in transitions.get(ArticleStatus(self.status), [])
```

### 树形结构模式

实现分类、评论等树形结构：

```python
class Category(UUIDModel):
    name: str = fields.CharField(max_length=100)
    parent: fields.ForeignKeyField = fields.ForeignKeyField(
        "models.Category",
        related_name="children",
        null=True,
        on_delete=fields.CASCADE
    )
    
    async def get_ancestors(self):
        """获取所有祖先"""
        ancestors = []
        current = self
        while current.parent_id:
            await current.fetch_related("parent")
            current = current.parent
            ancestors.append(current)
        return ancestors
    
    async def get_descendants(self):
        """获取所有后代"""
        descendants = []
        children = await self.children.all()
        for child in children:
            descendants.append(child)
            descendants.extend(await child.get_descendants())
        return descendants
```

### 计数器缓存模式

缓存统计数据：

```python
class Author(UUIDModel):
    name: str = fields.CharField(max_length=100)
    article_count: int = fields.IntField(default=0)
    total_views: int = fields.IntField(default=0)
    
    async def update_counters(self):
        """更新计数器"""
        self.article_count = await Article.filter(author_id=self.id).count()
        result = await Article.filter(author_id=self.id).annotate(
            total=Sum("view_count")
        ).values("total")
        self.total_views = result[0]["total"] if result else 0
        await self.save(update_fields=["article_count", "total_views"])

class Article(UUIDModel):
    async def save(self, *args, **kwargs):
        """保存时更新作者计数器"""
        is_new = self.id is None
        await super().save(*args, **kwargs)
        if is_new:
            author = await Author.get(id=self.author_id)
            author.article_count += 1
            await author.save(update_fields=["article_count"])
```

## 最佳实践

### 1. 方法命名

- 实例方法：动词开头（publish、archive）
- 类方法：get_ 开头（get_published、get_trending）
- 属性方法：名词或 is_/has_ 开头

### 2. 异步方法

- 涉及数据库操作的用 async
- 纯计算用同步方法

### 3. 错误处理

```python
async def publish(self):
    if self.status != "draft":
        raise ValueError("只能发布草稿状态的文章")
    # ...
```

### 4. 性能考虑

- 避免在属性中查询数据库
- 复杂计算考虑缓存
- 使用 update_fields 只更新变化的字段

### 5. 单一职责

- 每个方法只做一件事
- 复杂逻辑拆分为多个方法

通过自定义方法和设计模式，可以构建清晰、可维护的业务逻辑。
