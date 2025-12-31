"""
自动发现 apps 目录下的 models 模块
"""

import os

from tortoise import Model

from faster_app.utils import BASE_DIR
from faster_app.utils.discover import BaseDiscover


class ModelDiscover(BaseDiscover):
    """模型发现器"""

    INSTANCE_TYPE = Model

    @property
    def TARGETS(self) -> list[dict]:
        """
        动态生成扫描目标
        
        扫描优先级：
        1. 如果存在 faster_app/apps 目录，则只扫描该目录（开发环境）
        2. 如果不存在 faster_app/apps，则扫描项目根目录下的 apps 目录（使用阶段）
        3. 如果两个都存在，则只扫描 faster_app/apps 目录（优先）
        """
        # 检查 faster_app/apps 目录（框架内部，开发环境，优先级最高）
        framework_apps_dir = os.path.join(BASE_DIR, "faster_app", "apps")
        if os.path.exists(framework_apps_dir) and os.path.isdir(framework_apps_dir):
            return [
                {
                    "directory": framework_apps_dir,
                    "filename": "models.py",
                    "skip_dirs": ["__pycache__", "utils", "tests"],
                    "skip_files": [],
                }
            ]
        
        # 如果 faster_app/apps 不存在，则扫描项目根目录下的 apps 目录（用户应用）
        root_apps_dir = os.path.join(BASE_DIR, "apps")
        if os.path.exists(root_apps_dir) and os.path.isdir(root_apps_dir):
            return [
                {
                    "directory": "apps",
                    "filename": "models.py",
                    "skip_dirs": ["__pycache__", "utils", "tests"],
                    "skip_files": [],
                }
            ]
        
        # 如果两个都不存在，返回空列表
        return []

    def discover(self) -> dict[str, list[str]]:
        """
        发现模型模块路径
        返回按app分组的模块路径字典, 用于Tortoise ORM的apps配置
        """
        apps_models = {}

        # 扫描 TARGETS 中的目录和文件
        for target in self.TARGETS:
            files = self.walk(
                directory=target.get("directory"),
                filename=target.get("filename"),
                skip_files=target.get("skip_files"),
                skip_dirs=target.get("skip_dirs"),
            )

            for file_path in files:
                # 将绝对路径转换为相对于项目根目录的路径
                # 例如: /path/to/project/apps/demo/models.py -> apps/demo/models.py
                try:
                    relative_path = os.path.relpath(file_path, BASE_DIR)
                except ValueError:
                    # 如果无法计算相对路径，尝试从 file_path 中提取
                    # 查找 "apps" 目录的位置
                    if "apps" in file_path:
                        idx = file_path.index("apps")
                        relative_path = file_path[idx:]
                    else:
                        continue

                # 将文件路径转换为模块路径
                # 例如: apps/demo/models.py -> apps.demo.models
                # 例如: faster_app/apps/demo/models.py -> faster_app.apps.demo.models
                module_path = relative_path.replace(os.sep, ".").replace(".py", "")

                # 提取app名称
                # 支持两种路径格式：
                # 1. apps.demo.models -> demo
                # 2. faster_app.apps.demo.models -> demo
                path_parts = module_path.split(".")
                
                # 查找 "apps" 在路径中的位置
                if "apps" in path_parts:
                    apps_index = path_parts.index("apps")
                    if apps_index + 1 < len(path_parts):
                        app_name = path_parts[apps_index + 1]  # demo, auth, etc.

                    if app_name not in apps_models:
                        apps_models[app_name] = []
                    apps_models[app_name].append(module_path)

        return apps_models
