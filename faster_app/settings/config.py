"""
配置实例模块

提供全局配置实例, 避免循环导入
"""

from .discover import SettingsDiscover

# 创建默认配置实例
configs = SettingsDiscover().merge()
