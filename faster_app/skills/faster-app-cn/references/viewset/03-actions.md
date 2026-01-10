# 自定义操作

## @action 装饰器

使用 `@action` 装饰器添加自定义端点。

## 实例级操作

对单个资源的操作（detail=True）：

```python
from faster_app.viewsets import ModelViewSet, action
from fastapi import Request

class ArticleViewSet(ModelViewSet):
    @action(detail=True, methods=["POST"])
    async def publish(self, request: Request, pk: str):
        """
        发布文章
        路由：POST /articles/{pk}/publish
        """
        article = await self.get_object(pk)
        article.status = "published"
        article.published_at = datetime.now()
        await article.save()
        
        schema = self.get_schema("retrieve")
        return await schema.from_orm_model(article)
```

## 集合级操作

对资源集合的操作（detail=False）：

```python
class ArticleViewSet(ModelViewSet):
    @action(detail=False, methods=["GET"])
    async def recent(self, request: Request):
        """
        获取最近文章
        路由：GET /articles/recent
        """
        articles = await self.model.filter(
            status="published"
        ).order_by("-created_at").limit(10)
        
        schema = self.get_schema("list")
        return [await schema.from_orm_model(a) for a in articles]
```

## 多 HTTP 方法

一个操作支持多个方法：

```python
class ArticleViewSet(ModelViewSet):
    @action(detail=True, methods=["GET", "POST"])
    async def stats(self, request: Request, pk: str):
        """
        GET /articles/{pk}/stats - 查看统计
        POST /articles/{pk}/stats - 更新统计
        """
        article = await self.get_object(pk)
        
        if request.method == "GET":
            return {
                "views": article.view_count,
                "likes": article.like_count
            }
        else:  # POST
            article.view_count += 1
            await article.save()
            return {"status": "updated"}
```

## 自定义路径和名称

```python
class ArticleViewSet(ModelViewSet):
    @action(
        detail=True,
        methods=["POST"],
        url_path="make-public",
        url_name="make_public"
    )
    async def make_public(self, request: Request, pk: str):
        """
        路由：POST /articles/{pk}/make-public
        """
        article = await self.get_object(pk)
        article.is_public = True
        await article.save()
        return {"status": "public"}
```

## 操作参数

- `detail=True/False` - 实例级或集合级
- `methods=["GET", "POST"]` - HTTP 方法列表
- `url_path="custom"` - 自定义 URL 路径
- `url_name="custom_name"` - 自定义 URL 名称

## 访问请求数据

```python
class ArticleViewSet(ModelViewSet):
    @action(detail=True, methods=["POST"])
    async def rate(self, request: Request, pk: str):
        """评分"""
        data = await request.json()
        rating = data.get("rating", 0)
        
        article = await self.get_object(pk)
        article.rating = rating
        await article.save()
        
        return {"rating": rating}
```
