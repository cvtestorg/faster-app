# 常见问题 (FAQ)

## 安装和配置

**Q: 如何安装 Faster APP？**
```bash
uv add faster-app
```

**Q: 如何初始化项目？**
```bash
faster app demo  # 创建演示应用
faster app env   # 生成 .env 文件
```

**Q: 生产环境需要修改哪些配置？**
- SECRET_KEY：必须修改为强随机值
- DEBUG=false
- CORS_ALLOW_ORIGINS：设置具体域名
- TRUSTED_HOST_ENABLED=true

## 模型相关

**Q: 如何定义模型？**
```python
from faster_app.models.base import UUIDModel, DateTimeModel

class Article(UUIDModel, DateTimeModel):
    title: str = Field(..., max_length=200)
```

**Q: 如何避免 N+1 查询？**
```python
# 使用 prefetch_related
articles = await Article.all().prefetch_related("author", "tags")
```

**Q: 如何实现软删除？**
```python
class Article(UUIDModel):
    deleted_at: datetime = fields.DatetimeField(null=True)
    
    async def soft_delete(self):
        self.deleted_at = datetime.now()
        await self.save()
```

## ViewSet 相关

**Q: 如何创建 CRUD API？**
```python
class ArticleViewSet(ModelViewSet):
    model = Article
    schema = ArticleResponse

router = ArticleViewSet.as_router(prefix="/articles")
```

**Q: 如何添加认证？**
```python
from faster_app.viewsets.authentication import JWTAuthentication

class ArticleViewSet(ModelViewSet):
    authentication_classes = [JWTAuthentication]
```

**Q: 如何添加自定义操作？**
```python
@action(detail=True, methods=["POST"])
async def publish(self, request: Request, pk: str):
    article = await self.get_object(pk)
    article.status = "published"
    await article.save()
```

## 错误处理

**Q: 路由未发现？**
- 确保 APIRouter 在模块作用域
- 检查文件在 apps/ 目录
- 验证无导入错误

**Q: 模型未注册？**
- 检查继承自 tortoise.Model
- 文件名为 models.py
- 运行 `faster db migrate`

**Q: 配置未加载？**
- 检查 .env 在项目根目录
- 验证变量名大写
- 使用 configs.debug 而非 configs.DEBUG

更多问题请查阅详细主题文档。
