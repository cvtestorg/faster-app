# 自定义命令

本页面介绍如何创建和使用自定义命令。

## 创建自定义命令

```python
# apps/users/commands.py
from faster_app.commands.base import BaseCommand
from .models import User

# BaseCommand: 命令基类, 提供命令注册和参数解析功能
class UserCommand(BaseCommand):
    """用户管理命令"""

    # username: 用户名参数, 字符串类型, 通过命令行 --username=xxx 传入
    # email: 邮箱参数, 字符串类型, 通过命令行 --email=xxx 传入
    async def create_admin(self, username: str, email: str):
        """创建管理员账号
        Args:
            username: 管理员用户名
            email: 管理员邮箱地址
        """
        # User.create(): 创建用户记录, is_staff=True 设置为管理员
        user = await User.create(
            username=username,  # 用户名
            email=email,        # 邮箱
            is_staff=True       # 管理员标识
        )
        print(f"✅ 管理员 {username} 创建成功")

    # 无参数方法, 直接通过 faster user count 调用
    async def count(self):
        """统计用户数量"""
        # User.all(): 获取所有用户查询集
        # .count(): 统计查询集数量
        count = await User.all().count()
        print(f"总用户数: {count}")
```

## 使用自定义命令

```bash
# --username=admin: 指定用户名参数为 admin
# --email=admin@example.com: 指定邮箱参数为 admin@example.com
faster user create_admin --username=admin --email=admin@example.com

# 无参数命令, 直接执行统计功能
faster user count
```

## 命名规则

类名自动转换为命令组名：

| 类名                 | 命令组         |
| -------------------- | -------------- |
| `UserCommand`        | `user`         |
| `ArticleCommand`     | `article`      |
| `UserProfileCommand` | `user_profile` |

更多详细内容...
