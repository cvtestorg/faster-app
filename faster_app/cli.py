"""
Faster-App CLI entry point.

Main command-line interface for the Faster-App framework. Automatically
discovers and registers all CLI commands from the application.
"""

import os
import sys
from typing import Any

import fire

from faster_app.commands.discover import CommandDiscover


def main() -> None:
    """
    Faster-App command-line tool main entry point.

    Configures Python path, discovers available commands, and launches
    the Fire CLI interface.

    Note:
        Commands are automatically discovered from apps/*/commands.py files
        and registered with Fire for CLI access.
    """
    # 将当前工作目录添加到 Python 路径, 确保可以导入项目模块
    current_dir = os.getcwd()
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    # 设置 PYTHONPATH 环境变量, 确保子进程也能找到项目模块
    pythonpath = os.environ.get("PYTHONPATH", "")
    if current_dir not in pythonpath:
        os.environ["PYTHONPATH"] = (
            current_dir + ":" + pythonpath if pythonpath else current_dir
        )

    # 禁用 Fire 的分页器, 避免在 AI Agent 中挂起
    # 设置 PAGER=cat 使输出直接显示而不需要交互
    if "PAGER" not in os.environ:
        os.environ["PAGER"] = "cat"

    # 收集命令
    commands: dict[str, Any] = CommandDiscover().collect()
    fire.Fire(commands)


if __name__ == "__main__":
    main()
