"""
Base command class for CLI commands using Fire.

This module provides a base class for all CLI commands with automatic
PYTHONPATH configuration and command name generation.
"""

import os
import sys


class BaseCommand:
    """Base class for all CLI commands.

    Provides automatic PYTHONPATH configuration and command name generation
    from class names by removing common prefixes and suffixes.

    Attributes:
        _DEFAULT_PREFIXES: Default list of prefixes to strip from command names
        _DEFAULT_SUFFIXES: Default list of suffixes to strip from command names
    """

    # 默认要去掉的前缀列表(私有属性, 避免被 Fire 暴露)
    _DEFAULT_PREFIXES: list[str] = []

    # 默认要去掉的后缀列表(私有属性, 避免被 Fire 暴露)
    _DEFAULT_SUFFIXES: list[str] = [
        "Command",
        "Commands",
        "Handler",
        "Handlers",
        "Operations",
        "Operation",
    ]

    class Meta:
        """
        Metaclass configuration for command name generation.

        Attributes:
            PREFIXES: Additional prefixes to remove from command names
            SUFFIXES: Additional suffixes to remove from command names
        """

        PREFIXES: list[str] = []
        SUFFIXES: list[str] = []

    def __init__(self) -> None:
        """Initialize the command base class and configure PYTHONPATH."""
        self._setup_python_path()

    def _setup_python_path(self) -> None:
        """
        Configure Python path to ensure project modules can be imported.

        Adds the current working directory to sys.path and PYTHONPATH
        environment variable to ensure both the current process and
        subprocesses can import project modules.
        """
        # 将当前工作目录添加到 Python 路径, 确保可以导入项目模块
        current_dir = os.getcwd()
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        # 设置 PYTHONPATH 环境变量, 确保子进程也能找到项目模块
        pythonpath = os.environ.get("PYTHONPATH", "")
        if current_dir not in pythonpath:
            os.environ["PYTHONPATH"] = current_dir + ":" + pythonpath if pythonpath else current_dir

    @classmethod
    def _get_command_name(
        cls,
        class_name: str | None = None,
        prefixes: list[str] | None = None,
        suffixes: list[str] | None = None,
    ) -> str:
        """
        Generate a clean command name from a class name.

        Automatically removes common prefixes and suffixes to create
        a concise command name.

        Args:
            class_name: The class name to process (defaults to current class)
            prefixes: List of prefixes to remove (defaults to _DEFAULT_PREFIXES + Meta.PREFIXES)
            suffixes: List of suffixes to remove (defaults to _DEFAULT_SUFFIXES + Meta.SUFFIXES)

        Returns:
            Lowercase command name with prefixes and suffixes removed

        Example:
            >>> ServerCommand._get_command_name()
            'server'
            >>> AppOperations._get_command_name()
            'app'
        """
        if class_name is None:
            class_name = cls.__name__

        # 获取前缀列表, 合并默认前缀和 Meta 配置的前缀
        if prefixes is None:
            meta_prefixes = getattr(cls.Meta, "PREFIXES", []) if hasattr(cls, "Meta") else []
            prefixes = cls._DEFAULT_PREFIXES + meta_prefixes

        # 获取后缀列表, 合并默认后缀和 Meta 配置的后缀
        if suffixes is None:
            meta_suffixes = getattr(cls.Meta, "SUFFIXES", []) if hasattr(cls, "Meta") else []
            suffixes = cls._DEFAULT_SUFFIXES + meta_suffixes

        # 去除前缀
        # 按照前缀长度从长到短排序, 优先匹配较长的前缀
        sorted_prefixes = sorted(prefixes, key=len, reverse=True)
        for prefix in sorted_prefixes:
            if class_name.startswith(prefix):
                class_name = class_name[len(prefix) :]
                break

        # 去除后缀
        # 按照后缀长度从长到短排序, 优先匹配较长的后缀
        sorted_suffixes = sorted(suffixes, key=len, reverse=True)
        for suffix in sorted_suffixes:
            if class_name.endswith(suffix):
                class_name = class_name[: -len(suffix)]
                break

        # 返回小写的命令名
        return class_name.lower()
