# 实战示例

## 完整博客系统

### 1. 定义模型

```python
# apps/blog/models.py
from faster_app.models.base import UUIDModel, DateTimeModel

class Author(UUIDModel):
    name: str = fields.CharField(max_length=100)
    email: str = fields.CharField(max_length=200, unique=True)

class Tag(UUIDModel):
    name: str = fields.CharField(max_length=50, unique=True)

class Post(UUIDModel, DateTimeModel):
    title: str = fields.CharField(max_length=200)
    content: str = fields.TextField()
    status: str = fields.CharField(max_length=20, default="draft")
    author: fields.ForeignKeyField = fields.ForeignKeyField(
        "models.Author", related_name="posts"
    )
    tags: fields.ManyToManyField = fields.ManyToManyField(
        "models.Tag", related_name="posts"
    )
```

### 2. 创建 Schema

```python
# apps/blog/schemas.py
from pydantic import BaseModel

class PostCreate(BaseModel):
    title: str
    content: str
    author_id: str
    tag_ids: list[str]

class PostResponse(BaseModel):
    id: str
    title: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### 3. 实现 ViewSet

```python
# apps/blog/routes.py
class PostViewSet(ModelViewSet):
    model = Post
    schema = PostResponse
    create_schema = PostCreate
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=["POST"])
    async def publish(self, request, pk):
        post = await self.get_object(pk)
        post.status = "published"
        await post.save()
        return {"status": "published"}

router = PostViewSet.as_router(prefix="/posts")
```

### 4. 数据库迁移

```bash
faster db migrate --name="create_blog"
faster db upgrade
```

完整项目已可用，访问 `/docs` 查看 API。
