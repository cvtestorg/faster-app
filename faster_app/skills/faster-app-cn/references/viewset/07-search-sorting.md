# 搜索与排序

## 搜索

### 基础搜索

跨多个字段搜索：

```python
class ArticleViewSet(ModelViewSet):
    search_fields = ["title", "content"]
    
    # 用法：?search=python
```

### 跨关系搜索

```python
class ArticleViewSet(ModelViewSet):
    search_fields = [
        "title",
        "content",
        "author__name",
        "tags__name"
    ]
    
    # 用法：?search=张三
```

### 自定义搜索

```python
class ArticleViewSet(ModelViewSet):
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search")
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(author__name__icontains=search)
            )
        
        return queryset
```

## 排序

### 基础排序

```python
class ArticleViewSet(ModelViewSet):
    ordering_fields = ["created_at", "title", "view_count"]
    ordering = ["-created_at"]  # 默认：最新优先
```

### 查询示例

```bash
# 升序
?ordering=title

# 降序
?ordering=-created_at

# 多字段排序
?ordering=-created_at,title
```

### 跨关系排序

```python
class ArticleViewSet(ModelViewSet):
    ordering_fields = [
        "created_at",
        "title",
        "author__name",
        "view_count"
    ]
    
    # 用法：?ordering=author__name
```

## 默认排序

### 模型级别

```python
class Article(UUIDModel, DateTimeModel):
    title: str = Field(...)
    
    class Meta:
        table = "articles"
        ordering = ["-created_at", "title"]
```

### ViewSet 级别

```python
class ArticleViewSet(ModelViewSet):
    ordering = ["-is_featured", "-created_at"]
    # 先按推荐排序，再按时间排序
```

## 组合搜索和排序

```python
class ArticleViewSet(ModelViewSet):
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "view_count", "title"]
    ordering = ["-created_at"]
    
# 查询示例
# ?search=python&ordering=-view_count
```

## 搜索优化

### 添加索引

```python
class Article(UUIDModel, DateTimeModel):
    title: str = Field(..., max_length=200, index=True)
    content: str = Field(..., index=True)
```

### 限制搜索字段

```python
class ArticleViewSet(ModelViewSet):
    search_fields = ["title"]  # 只搜索标题，提高性能
```
