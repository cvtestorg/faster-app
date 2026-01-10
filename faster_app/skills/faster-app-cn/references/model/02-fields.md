# 字段类型

Tortoise ORM 支持丰富的字段类型，满足各种数据建模需求。

## 字符串字段

### CharField - 短文本

用于存储固定最大长度的字符串：

```python
from tortoise import fields

class Article(UUIDModel):
    # 基础用法
    title: str = fields.CharField(max_length=200)
    
    # 唯一约束
    slug: str = fields.CharField(max_length=200, unique=True)
    
    # 可选字段
    subtitle: str = fields.CharField(max_length=200, null=True)
    
    # 带默认值
    status: str = fields.CharField(max_length=20, default="draft")
    
    # 添加索引（提高查询性能）
    author: str = fields.CharField(max_length=100, index=True)
    
    # 带描述（用于 API 文档）
    category: str = fields.CharField(
        max_length=50,
        description="文章分类"
    )
```

**注意**：超过 max_length 的值会在数据库层面被截断。

### TextField - 长文本

用于存储大量文本内容：

```python
class Article(UUIDModel):
    # 文章内容
    content: str = fields.TextField()
    
    # Markdown 格式
    markdown_content: str = fields.TextField(null=True)
    
    # 富文本 HTML
    html_content: str = fields.TextField(default="")
```

**TextField vs CharField**：
- TextField 没有长度限制
- TextField 不能设置 unique
- TextField 不建议添加索引（性能差）

## 数字字段

### IntField - 整数

```python
class Article(UUIDModel):
    # 浏览次数
    view_count: int = fields.IntField(default=0)
    
    # 点赞数
    like_count: int = fields.IntField(default=0, ge=0)  # 大于等于0
    
    # 排序值
    sort_order: int = fields.IntField(default=0, index=True)
```

### FloatField - 浮点数

```python
class Product(UUIDModel):
    # 评分（0.0-5.0）
    rating: float = fields.FloatField(default=0.0)
    
    # 重量（千克）
    weight: float = fields.FloatField(null=True)
```

### DecimalField - 精确小数

用于需要精确计算的场景（如货币）：

```python
from decimal import Decimal

class Product(UUIDModel):
    # 价格（精确到分）
    price: Decimal = fields.DecimalField(
        max_digits=10,    # 总位数
        decimal_places=2, # 小数位数
        default=Decimal("0.00")
    )
    
    # 折扣率
    discount: Decimal = fields.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("1.00")
    )
```

**为什么用 DecimalField**：
- FloatField 有精度问题：`0.1 + 0.2 != 0.3`
- DecimalField 精确计算，适合金融场景

## 布尔字段

```python
class Article(UUIDModel):
    # 是否已发布
    is_published: bool = fields.BooleanField(default=False)
    
    # 是否推荐
    is_featured: bool = fields.BooleanField(default=False, index=True)
    
    # 是否允许评论
    allow_comments: bool = fields.BooleanField(default=True)
```

## 日期时间字段

### DatetimeField - 日期时间

```python
from datetime import datetime

class Article(UUIDModel):
    # 发布时间
    published_at: datetime = fields.DatetimeField(null=True)
    
    # 自动设置当前时间
    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    
    # 每次保存时更新
    updated_at: datetime = fields.DatetimeField(auto_now=True)
```

### DateField - 日期

```python
from datetime import date

class Event(UUIDModel):
    # 活动日期
    event_date: date = fields.DateField()
    
    # 截止日期
    deadline: date = fields.DateField(null=True)
```

### TimeField - 时间

```python
from datetime import time

class Schedule(UUIDModel):
    # 开始时间
    start_time: time = fields.TimeField()
    
    # 结束时间
    end_time: time = fields.TimeField()
```

## JSON 字段

存储 JSON 数据：

```python
class Article(UUIDModel):
    # 元数据
    metadata: dict = fields.JSONField(default=dict)
    
    # 标签列表
    tags: list = fields.JSONField(default=list)
    
    # 配置信息
    settings: dict = fields.JSONField(default=lambda: {"theme": "default"})
```

**用法示例**：
```python
article = await Article.create(
    title="测试",
    metadata={"author": "张三", "category": "技术"},
    tags=["Python", "FastAPI"]
)

# 访问
print(article.metadata["author"])  # 张三
print(article.tags[0])  # Python
```

## 枚举字段

使用 IntField 配合 Python Enum：

```python
from enum import IntEnum

class ArticleStatus(IntEnum):
    DRAFT = 0
    PUBLISHED = 1
    ARCHIVED = 2

class Article(UUIDModel):
    status: int = fields.IntField(default=ArticleStatus.DRAFT)
    
    @property
    def status_name(self):
        return ArticleStatus(self.status).name
```

## 字段选项总结

### 通用选项

```python
class Article(UUIDModel):
    field = fields.CharField(
        max_length=200,
        
        # 空值
        null=True,              # 允许数据库 NULL
        default="默认值",        # 默认值
        
        # 约束
        unique=True,            # 唯一约束
        index=True,             # 创建索引
        
        # 文档
        description="字段说明",  # API 文档描述
        
        # 验证（Pydantic 层面）
        ge=0,                   # 大于等于
        le=100,                 # 小于等于
        gt=0,                   # 大于
        lt=100,                 # 小于
    )
```

### 特殊选项

```python
# 自动时间戳
created_at = fields.DatetimeField(auto_now_add=True)  # 创建时设置
updated_at = fields.DatetimeField(auto_now=True)       # 保存时更新

# 主键
id = fields.IntField(pk=True)  # 主键

# 生成的字段（计算字段）
# Tortoise ORM 不直接支持，需在应用层实现
```

## 最佳实践

1. **选择合适的字段类型**
   - 固定长度文本用 CharField
   - 长文本用 TextField
   - 金钱用 DecimalField
   - 计数用 IntField

2. **合理使用索引**
   - 频繁查询的字段添加 index=True
   - 不要过度使用（影响写入性能）

3. **NULL vs 空值 vs 默认值**
   - 可选字段：null=True
   - 布尔字段：避免 NULL，使用 default=False
   - 字符串：用 default="" 而非 NULL

4. **命名约定**
   - 使用 snake_case：`created_at` 而非 `createdAt`
   - 布尔字段用 `is_` 或 `has_` 前缀
   - 时间字段用 `_at` 或 `_date` 后缀

5. **添加描述**
   - 为重要字段添加 description
   - 便于 API 文档生成和团队协作
