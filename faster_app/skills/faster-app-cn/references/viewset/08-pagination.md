# 分页

## 自动分页

列表操作自动分页：

```python
class ArticleViewSet(ModelViewSet):
    model = Article
    schema = ArticleResponse
    
    # 列表端点自动分页
```

## 响应格式

```json
{
  "items": [
    {"id": "1", "title": "文章1"},
    {"id": "2", "title": "文章2"}
  ],
  "total": 100,
  "page": 1,
  "size": 50,
  "pages": 2
}
```

## 查询参数

```bash
# 获取第一页，每页 20 条
?page=1&size=20

# 获取第二页，每页 50 条
?page=2&size=50
```

## 默认配置

框架使用 `fastapi-pagination` 提供分页：

- **默认每页大小**：50
- **最大每页大小**：100
- **页码从 1 开始**

## 自定义分页大小

### 请求时指定

```bash
?page=1&size=10
```

### ViewSet 级别配置

```python
from fastapi_pagination import Page

class ArticleViewSet(ModelViewSet):
    # 使用自定义分页配置
    pagination_class = Page
```

## 禁用分页

某些操作可能不需要分页：

```python
from faster_app.viewsets import action

class ArticleViewSet(ModelViewSet):
    @action(detail=False, methods=["GET"])
    async def all(self, request: Request):
        """获取所有文章（不分页）"""
        articles = await self.model.all()
        return articles
```

## 分页与过滤组合

```bash
# 过滤已发布的文章，第一页，每页 20 条
?status=published&page=1&size=20
```

## 分页与排序组合

```bash
# 按时间降序，第二页，每页 10 条
?ordering=-created_at&page=2&size=10
```

## 最佳实践

1. **合理的页面大小**：通常 20-50 条
2. **限制最大值**：避免一次查询过多数据
3. **总是排序**：确保分页结果一致
4. **使用索引**：为排序字段添加数据库索引
5. **缓存总数**：对于大数据集，可以缓存 total 值
