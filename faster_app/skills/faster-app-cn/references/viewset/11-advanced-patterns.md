# 高级模式

## 嵌套资源

### 基础嵌套

```python
class CommentViewSet(ModelViewSet):
    model = Comment
    schema = CommentResponse
    
    def get_queryset(self):
        article_id = self.request.path_params.get("article_id")
        return self.model.filter(article_id=article_id)

# 路由：/articles/{article_id}/comments
router = CommentViewSet.as_router(
    prefix="/articles/{article_id}/comments",
    tags=["评论"]
)
```

### 创建嵌套资源

```python
class CommentViewSet(ModelViewSet):
    @action(detail=False, methods=["POST"])
    async def create_comment(self, request: Request):
        article_id = request.path_params.get("article_id")
        data = await request.json()
        
        comment = await Comment.create(
            article_id=article_id,
            **data
        )
        return await CommentResponse.from_orm_model(comment)
```

## 批量操作

### 批量创建

```python
class ArticleViewSet(ModelViewSet):
    @action(detail=False, methods=["POST"])
    async def batch_create(self, request: Request):
        """批量创建文章"""
        data = await request.json()
        articles = data.get("articles", [])
        
        created = []
        for article_data in articles:
            article = await self.model.create(**article_data)
            created.append(article)
        
        return {"created": len(created)}
```

### 批量更新

```python
class ArticleViewSet(ModelViewSet):
    @action(detail=False, methods=["POST"])
    async def batch_publish(self, request: Request):
        """批量发布"""
        data = await request.json()
        ids = data.get("ids", [])
        
        await self.model.filter(id__in=ids).update(
            status="published",
            published_at=datetime.now()
        )
        
        return {"updated": len(ids)}
```

### 批量删除

```python
class ArticleViewSet(ModelViewSet):
    @action(detail=False, methods=["DELETE"])
    async def batch_delete(self, request: Request):
        """批量删除"""
        data = await request.json()
        ids = data.get("ids", [])
        
        deleted = await self.model.filter(id__in=ids).delete()
        return {"deleted": deleted}
```

## 软删除

### 实现软删除

```python
class ArticleViewSet(ModelViewSet):
    def get_queryset(self):
        """排除软删除的项"""
        return self.model.filter(deleted_at__isnull=True)
    
    async def perform_destroy(self, instance):
        """软删除而非硬删除"""
        instance.deleted_at = datetime.now()
        await instance.save()
```

### 恢复软删除

```python
class ArticleViewSet(ModelViewSet):
    @action(detail=True, methods=["POST"])
    async def restore(self, request: Request, pk: str):
        """恢复软删除的项"""
        instance = await self.model.get(id=pk)
        instance.deleted_at = None
        await instance.save()
        return {"status": "restored"}
```

## 文件上传

### 单文件上传

```python
from fastapi import UploadFile, File

class ArticleViewSet(ModelViewSet):
    @action(detail=True, methods=["POST"])
    async def upload_image(
        self,
        request: Request,
        pk: str,
        file: UploadFile = File(...)
    ):
        """上传文章图片"""
        article = await self.get_object(pk)
        
        # 保存文件
        file_path = f"uploads/{pk}/{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        article.image_url = file_path
        await article.save()
        
        return {"image_url": file_path}
```

### 多文件上传

```python
class ArticleViewSet(ModelViewSet):
    @action(detail=True, methods=["POST"])
    async def upload_images(
        self,
        request: Request,
        pk: str,
        files: list[UploadFile] = File(...)
    ):
        """上传多张图片"""
        article = await self.get_object(pk)
        
        uploaded = []
        for file in files:
            file_path = f"uploads/{pk}/{file.filename}"
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            uploaded.append(file_path)
        
        article.images = uploaded
        await article.save()
        
        return {"images": uploaded}
```

## 版本控制

### 记录版本

```python
class ArticleViewSet(ModelViewSet):
    async def perform_update(self, instance, data):
        """更新前记录版本"""
        # 保存历史版本
        await ArticleHistory.create(
            article_id=instance.id,
            version=instance.version,
            data=instance.to_dict()
        )
        
        # 更新实例
        instance.version += 1
        for key, value in data.items():
            setattr(instance, key, value)
        await instance.save()
```

### 查看版本历史

```python
class ArticleViewSet(ModelViewSet):
    @action(detail=True, methods=["GET"])
    async def history(self, request: Request, pk: str):
        """查看版本历史"""
        history = await ArticleHistory.filter(
            article_id=pk
        ).order_by("-created_at")
        
        return [h.to_dict() for h in history]
```

## 最佳实践

1. **嵌套资源** - 保持 URL 层次清晰
2. **批量操作** - 限制数量，防止滥用
3. **软删除** - 重要数据总是软删除
4. **文件上传** - 验证文件类型和大小
5. **版本控制** - 关键数据保留历史
6. **错误处理** - 批量操作部分失败的处理
7. **事务** - 批量操作使用数据库事务
8. **异步** - 大批量操作考虑后台任务
