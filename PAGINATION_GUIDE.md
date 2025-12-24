# 统一分页功能使用指南

Faster APP 提供了基于 `fastapi-pagination` 的统一分页方案，让开发者能够轻松实现 API 分页功能。

## 🎯 设计目标

- **遵循 FastAPI 最佳实践**: 使用成熟的 `fastapi-pagination` 库
- **开发者友好**: 简单易用，学习成本低
- **最小化改动**: 不过度设计，保持代码简洁

## 📦 快速开始

### 1. 导入分页组件

```python
from fastapi import APIRouter, Depends
from faster_app.utils.pagination import Page, Params, paginate
```

或者从 utils 直接导入:

```python
from faster_app.utils import Page, Params, paginate
```

### 2. 基本用法 - 列表分页

对内存中的列表进行分页:

```python
from faster_app.utils.pagination import Page, Params, paginate
from fastapi import Depends

router = APIRouter()

@router.get("/items", response_model=Page[dict])
async def list_items(params: Params = Depends()):
    """简单的列表分页"""
    items = [{"id": i, "name": f"Item {i}"} for i in range(100)]
    return paginate(items, params)
```

### 3. 数据库查询分页

对 Tortoise ORM 查询进行分页（最常用）:

```python
from faster_app.utils.pagination import Page, Params, paginate
from faster_app.apps.demo.models import DemoModel
from fastapi import Depends

@router.get("/demos", response_model=Page[DemoSchema])
async def list_demos(params: Params = Depends()):
    """数据库查询分页"""
    query = DemoModel.all().order_by("-created_at")
    return await paginate(query, params)
```

### 4. 带过滤和排序的分页

```python
@router.get("/demos", response_model=Page[DemoSchema])
async def list_demos(
    params: Params = Depends(),
    status: int | None = None,
):
    """支持过滤的分页查询"""
    query = DemoModel.all()
    
    # 添加过滤条件
    if status is not None:
        query = query.filter(status=status)
    
    # 添加排序
    query = query.order_by("-created_at")
    
    # 分页
    return await paginate(query, params)
```

## 🔧 高级用法

### 自定义分页参数

使用 `CustomParams` 自定义默认分页大小:

```python
from faster_app.utils.pagination import Page, CustomParams, paginate
from fastapi import Depends

@router.get("/items", response_model=Page[dict])
async def list_items(params: CustomParams = Depends()):
    """使用自定义参数（默认每页 20 条，最多 100 条）"""
    items = [{"id": i} for i in range(200)]
    return paginate(items, params)
```

`CustomParams` 的默认配置:
- 默认每页: 20 条
- 最大每页: 100 条
- 最小每页: 1 条

### 在 CRUD 路由中使用

`CRUDRouter` 已经自动集成了分页功能:

```python
from faster_app.utils.crud import CRUDRouter
from faster_app.apps.demo.models import DemoModel

# 自动生成的列表接口已支持分页
router = CRUDRouter(
    model=DemoModel,
    prefix="/demos",
    tags=["Demo"],
).get_router()

# GET /demos/ 会自动支持 ?page=1&size=10 参数
```

## 📝 分页响应格式

所有分页接口都会返回统一的响应格式:

```json
{
  "items": [
    {"id": 1, "name": "Item 1"},
    {"id": 2, "name": "Item 2"}
  ],
  "total": 100,
  "page": 1,
  "size": 10,
  "pages": 10
}
```

响应字段说明:
- `items`: 当前页的数据列表
- `total`: 总记录数
- `page`: 当前页码（从 1 开始）
- `size`: 每页大小
- `pages`: 总页数

## 🌐 API 调用示例

### 基本分页请求

```bash
# 获取第一页，每页 10 条
GET /api/demos?page=1&size=10

# 获取第二页，每页 20 条
GET /api/demos?page=2&size=20
```

### 结合过滤和排序

```bash
# 获取状态为 1 的记录，第一页
GET /api/demos?page=1&size=10&status=1
```

## 💡 最佳实践

### 1. 始终指定 response_model

使用 `Page[YourModel]` 作为响应模型，以便 OpenAPI 文档正确生成:

```python
@router.get("/items", response_model=Page[ItemSchema])
async def list_items(params: Params = Depends()):
    ...
```

### 2. 对大数据集使用数据库分页

避免在内存中加载所有数据再分页，应该在数据库层面进行分页:

```python
# ✅ 推荐：数据库层面分页
query = Model.all()
return await paginate(query, params)

# ❌ 不推荐：内存分页（数据量大时性能差）
all_items = await Model.all()
return paginate(all_items, params)
```

### 3. 设置合理的分页大小限制

使用 `CustomParams` 来限制最大分页大小，防止滥用:

```python
from faster_app.utils.pagination import CustomParams

# 限制最多每页 50 条
class LimitedParams(Params):
    size: int = Query(20, ge=1, le=50, description="每页数量")
```

### 4. 在查询中添加排序

确保分页结果的一致性，建议总是指定排序:

```python
# 按创建时间倒序
query = Model.all().order_by("-created_at")
return await paginate(query, params)
```

## 🔍 完整示例

查看 `faster_app/apps/demo/routes.py` 中的分页演示:

- `pagination_demo_router`: 包含简单列表分页和数据库查询分页的完整示例
- `demo_quick_router`: CRUD 路由自动集成分页的示例
- `demo_balanced_router`: 自定义路由中使用分页的示例

## 🚀 运行示例

```bash
# 启动服务器
faster server start

# 访问 Swagger 文档
open http://localhost:8000/docs

# 查看分页演示接口
# - GET /pagination-demo/simple-list
# - GET /pagination-demo/database-query
# - GET /demos-quick/
```

## 📚 参考资源

- [fastapi-pagination 官方文档](https://github.com/uriyyo/fastapi-pagination)
- [FastAPI 依赖注入](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Tortoise ORM 查询](https://tortoise.github.io/query.html)

## ❓ 常见问题

### Q: 如何修改默认的分页大小？

A: 使用 `CustomParams` 或创建自己的参数类:

```python
class MyParams(Params):
    size: int = Query(50, ge=1, le=200, description="每页数量")
```

### Q: 如何在分页时排除某些字段？

A: 在 Pydantic Schema 中控制字段的输出:

```python
class ItemSchema(BaseModel):
    id: int
    name: str
    # 不包含敏感字段
    
    class Config:
        from_attributes = True
```

### Q: 分页是否支持游标分页（cursor pagination）？

A: `fastapi-pagination` 支持多种分页策略。本框架默认使用 offset 分页（page/size），这是最常见和易用的方式。如需游标分页，可以参考 `fastapi-pagination` 的官方文档。

### Q: 如何在分页响应中添加额外的元数据？

A: 可以自定义响应格式或在查询后处理结果:

```python
result = await paginate(query, params)
return {
    "pagination": result,
    "extra_info": {"timestamp": datetime.now()}
}
```
