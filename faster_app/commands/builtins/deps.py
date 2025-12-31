"""
依赖分析命令

提供依赖关系分析和循环依赖检测功能。
"""

from collections import defaultdict

from rich.console import Console
from rich.panel import Panel

from faster_app.commands.base import BaseCommand
from faster_app.utils.dependency import DependencyAnalyzer

console = Console()


class DepsCommand(BaseCommand):
    """依赖分析命令"""

    def analyze(self, apps_dir: str = "apps", output: str | None = None) -> None:
        """
        分析应用依赖关系

        Args:
            apps_dir: 应用目录路径, 默认为 "apps"
            output: 输出文件路径, 如果不指定则输出到控制台
        """
        analyzer = DependencyAnalyzer(apps_dir=apps_dir)
        analysis = analyzer.analyze()

        if output:
            # 保存到文件时使用纯文本格式
            output_str = analyzer.format_text_output()
            with open(output, "w", encoding="utf-8") as f:
                f.write(output_str)
            console.print(f"[bold green]✅ 结果已保存到: {output}[/bold green]")
        else:
            # 控制台输出使用图形化展示
            self._print_graph_analysis(analysis)

    def _print_graph_analysis(self, analysis: dict) -> None:
        """使用图形化方式打印依赖关系"""
        # 绘制依赖图
        console.print()
        graph_text = self._draw_dependency_graph(analysis)
        console.print(Panel(graph_text, border_style="blue", padding=(1, 2)))
        console.print()

        # 循环依赖
        if analysis["cycles"]:
            cycles_panel = Panel(
                self._format_cycles(analysis["cycles"]),
                title="[bold red]⚠️  检测到循环依赖[/bold red]",
                border_style="red",
            )
            console.print(cycles_panel)
        else:
            console.print(
                Panel(
                    "[bold green]✅ 未检测到循环依赖[/bold green]",
                    border_style="green",
                )
            )
        console.print()

    def _draw_dependency_graph(self, analysis: dict) -> str:
        """绘制依赖关系图"""
        apps = sorted(analysis["apps"])
        dependencies = analysis["dependencies"]

        if not apps:
            return "[dim]未发现应用[/dim]"

        # 构建反向依赖图 (用于确定哪些应用被依赖)
        reverse_deps: dict[str, set[str]] = defaultdict(set)
        for app, deps in dependencies.items():
            for dep in deps:
                reverse_deps[dep].add(app)

        # 找出根节点 (没有被其他应用依赖的节点)
        root_nodes = [app for app in apps if app not in reverse_deps]

        # 如果没有根节点, 说明存在循环, 选择第一个应用作为起点
        if not root_nodes:
            root_nodes = [apps[0]]

        lines = []
        visited = set()

        def draw_node(app: str, prefix: str = "", is_last: bool = True) -> None:
            """递归绘制节点"""
            if app in visited:
                return

            visited.add(app)

            # 绘制当前节点
            connector = "└── " if is_last else "├── "
            node_style = "[bold cyan]" if app in root_nodes else "[green]"
            lines.append(f"{prefix}{connector}{node_style}{app}[/]")

            # 更新前缀
            new_prefix = prefix + ("    " if is_last else "│   ")

            # 获取依赖
            deps = sorted(dependencies.get(app, set()))
            if deps:
                for i, dep in enumerate(deps):
                    is_last_dep = i == len(deps) - 1
                    draw_node(dep, new_prefix, is_last_dep)

        # 绘制所有根节点
        for i, root in enumerate(root_nodes):
            is_last_root = i == len(root_nodes) - 1
            draw_node(root, "", is_last_root)

        # 如果有未访问的节点 (可能是循环的一部分), 单独显示
        unvisited = [app for app in apps if app not in visited]
        if unvisited:
            lines.append("")
            lines.append("[yellow]其他节点 (可能存在循环):[/]")
            for app in unvisited:
                lines.append(f"  • [yellow]{app}[/]")
                deps = sorted(dependencies.get(app, set()))
                if deps:
                    for dep in deps:
                        lines.append(f"    └─→ [dim]{dep}[/]")

        return "\n".join(lines)

    def _format_cycles(self, cycles: list[list[str]]) -> str:
        """格式化循环依赖文本"""
        lines = []
        for i, cycle in enumerate(cycles, 1):
            cycle_str = " → ".join(cycle) + " → " + cycle[0]
            lines.append(f"循环 {i}: {cycle_str}")
        return "\n".join(lines)
