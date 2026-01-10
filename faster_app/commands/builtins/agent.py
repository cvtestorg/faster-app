import os
import shutil

from rich.console import Console

from faster_app.commands.base import BaseCommand
from faster_app.utils import BASE_DIR

console = Console()


class AgentCommand(BaseCommand):
    """🛠️ 智能体管理命令 - 快速创建和配置智能体组件"""

    def skill(self, system: bool = True, lan: str = "cn"):
        """🔧 安装技能 - 复制 skill 目录中的文件到 ~/.claude/skills/ 目录"""
        # 确保目标目录存在
        target_dir = "~/.claude/skills" if system else ".claude/skills"
        target_dir = os.path.expanduser(target_dir)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
        # 复制技能文件
        skill_name = f"faster-app-{lan}"
        target_skill_dir = os.path.join(target_dir, skill_name)
        shutil.copytree(f"{BASE_DIR}/skills/{skill_name}", target_skill_dir, dirs_exist_ok=True)
        console.print(
            f"[bold green]✅ {skill_name} 技能安装成功[/bold green], 安装位置: {target_dir}/{skill_name}"
        )

        # 指导用户如何使用 skills
        console.print(
            "[bold green]⚠️ 请使用 [bold]bash('openskills sync')[/bold] 加载技能[/bold green]"
        )
