import os
import importlib.util
import inspect
import logging
from typing import Dict, List, Optional, Type, Any

logger = logging.getLogger(__name__)


class BaseDiscover:
    """Base class for auto-discovery of instances in the application.
    
    This class provides the core functionality for scanning directories and files,
    importing modules, and extracting instances of a specific type.
    
    Attributes:
        INSTANCE_TYPE: The type of instances to discover and extract
        TARGETS: List of directory/file configurations to scan
    """
    
    INSTANCE_TYPE: Optional[Type] = None
    TARGETS: List[Dict[str, Any]] = []

    def discover(self) -> List[Any]:
        """
        Automatically scan directories and files defined in TARGETS,
        and extract all instances of INSTANCE_TYPE.
        
        Returns:
            List of discovered instances
        """
        instances = []

        # 扫描 TARGETS 中的目录和文件
        for target in self.TARGETS:
            instances.extend(
                self.scan(
                    directory=target.get("directory"),
                    filename=target.get("filename"),
                    skip_files=target.get("skip_files"),
                    skip_dirs=target.get("skip_dirs"),
                )
            )
        return instances

    def walk(
        self,
        directory: str,
        filename: Optional[str] = None,
        skip_files: Optional[List[str]] = None,
        skip_dirs: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Recursively walk through a directory and collect Python file paths.
        
        Args:
            directory: The directory path to walk through
            filename: Optional specific filename to look for
            skip_files: List of filenames to skip (default: empty list)
            skip_dirs: List of directory names to skip (default: empty list)
            
        Returns:
            List of absolute paths to Python files
        """
        skip_files = skip_files or []
        skip_dirs = skip_dirs or []
        results = []
        
        if not os.path.exists(directory) or not os.path.isdir(directory):
            return results

        for root, dirs, files in os.walk(directory):
            # 过滤掉需要跳过的目录, 直接修改 dirs 列表来影响 os.walk 的遍历
            dirs[:] = [d for d in dirs if d not in skip_dirs]

            for file in files:
                if filename is None or file == filename:
                    if file in skip_files:
                        continue
                    # 只处理 .py 文件
                    if file.endswith(".py"):
                        results.append(os.path.join(root, file))
        return results

    def scan(
        self,
        directory: str,
        filename: Optional[str] = None,
        skip_files: Optional[List[str]] = None,
        skip_dirs: Optional[List[str]] = None,
    ) -> List[Any]:
        """
        Generic scanning method to discover instances in Python files.

        Args:
            directory: The directory path to scan
            filename: Optional specific filename to scan (None scans all .py files)
            skip_files: List of filenames to skip
            skip_dirs: List of directory names to skip
            
        Returns:
            List of discovered instances
        """
        skip_files = skip_files or []
        skip_dirs = skip_dirs or []
        instances = []

        files = self.walk(directory, filename, skip_files, skip_dirs)

        for file in files:
            instances.extend(
                self.import_and_extract_instances(file, file.split("/")[-1][:-3])
            )

        return instances

    def import_and_extract_instances(
        self, file_path: str, module_name: str
    ) -> List[Any]:
        """
        Import a module and extract instances of INSTANCE_TYPE.

        Args:
            file_path: Absolute path to the Python file
            module_name: Name to use for the module

        Returns:
            List of extracted instances
        """
        instances = []

        try:
            # 动态导入模块
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                return instances

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 查找模块中所有的类并实例化
            for _, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, self.INSTANCE_TYPE)
                    and obj != self.INSTANCE_TYPE
                    and not inspect.isabstract(obj)  # 跳过抽象类
                ):
                    try:
                        # 实例化命令类
                        instance = obj()
                        instances.append(instance)
                    except Exception as e:
                        logger.warning(f"Failed to instantiate {obj.__name__}: {e}")

        except Exception as e:
            # 静默跳过导入失败的模块, 避免阻断整个发现过程
            logger.warning(f"Failed to import instances from {module_name}: {e}")

        return instances
