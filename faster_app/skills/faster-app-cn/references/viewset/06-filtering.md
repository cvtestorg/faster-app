# 过滤

## 过滤集

### 基础过滤

```python
from faster_app.viewsets import ModelViewSet
from faster_app.viewsets.filters import FilterSet

class ArticleFilterSet(FilterSet):
    fields = {
        "status": ["exact", "in"],
        "author": ["exact"],
        "created_at": ["gte", "lte"],
        "title": ["contains", "icontains"],
    }

class ArticleViewSet(ModelViewSet):
    filterset_class = ArticleFilterSet
```

### 查询示例

```bash
# 精确匹配
?status=published

# 在列表中
?status__in=draft,published

# 日期范围
?created_at__gte=2024-01-01&created_at__lte=2024-12-31

# 包含
?title__contains=Python
```

## 过滤操作符

### 比较操作符

- `exact` - 精确匹配：`?field=value`
- `in` - 在列表中：`?field__in=val1,val2`
- `gt` - 大于：`?field__gt=10`
- `gte` - 大于等于：`?field__gte=10`
- `lt` - 小于：`?field__lt=10`
- `lte` - 小于等于：`?field__lte=10`

### 字符串操作符

- `contains` - 包含（区分大小写）：`?field__contains=text`
- `icontains` - 包含（不区分大小写）：`?field__icontains=text`
- `startswith` - 开始于：`?field__startswith=prefix`
- `endswith` - 结束于：`?field__endswith=suffix`

### 空值操作符

- `isnull` - 为空：`?field__isnull=true`
- `not_isnull` - 不为空：`?field__not_isnull=true`

## 自定义过滤

### 方法过滤

```python
class ArticleFilterSet(FilterSet):
    fields = {
        "status": ["exact"],
    }
    
    async def filter_author(self, queryset, value):
        """自定义作者过滤"""
        if value:
            return queryset.filter(author__name__icontains=value)
        return queryset
```

### 多字段过滤

```python
class ArticleFilterSet(FilterSet):
    async def filter_query(self, queryset, value):
        """在多个字段中搜索"""
        if value:
            return queryset.filter(
                Q(title__icontains=value) | Q(content__icontains=value)
            )
        return queryset
```

## 关系过滤

跨关系过滤：

```python
class ArticleFilterSet(FilterSet):
    fields = {
        "author__name": ["exact", "icontains"],
        "tags__name": ["in"],
        "category__slug": ["exact"],
    }

# 查询示例
# ?author__name__icontains=zhang
# ?tags__name__in=python,fastapi
# ?category__slug=tech
```

## 动态过滤

根据用户动态过滤：

```python
class ArticleViewSet(ModelViewSet):
    filterset_class = ArticleFilterSet
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 非管理员只能看到已发布的
        user = self.request.state.user
        if user.get("role") != "admin":
            queryset = queryset.filter(status="published")
        
        return queryset
```
