#!/usr/bin/env python3
"""
配置加载器模块
提供YAML配置文件的加载和解析功能
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging


class ConfigLoader:
    """配置加载器"""

    def __init__(self, config_dir: str = None):
        """初始化配置加载器

        Args:
            config_dir: 配置文件目录，默认为模块目录下的config文件夹
        """
        if config_dir is None:
            # 默认配置文件目录
            self.config_dir = Path(__file__).parent / 'config'
        else:
            self.config_dir = Path(config_dir)

        self.logger = logging.getLogger(__name__)
        self._config_cache = {}

    def load_config(self, config_name: str) -> Dict[str, Any]:
        """加载配置文件

        Args:
            config_name: 配置文件名（不带.yaml后缀）

        Returns:
            配置字典
        """
        config_path = self.config_dir / f"{config_name}.yaml"

        # 检查缓存
        if config_name in self._config_cache:
            self.logger.debug(f"从缓存加载配置: {config_name}")
            return self._config_cache[config_name]

        try:
            if not config_path.exists():
                self.logger.warning(f"配置文件不存在: {config_path}")
                return {}

            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            # 缓存配置
            self._config_cache[config_name] = config

            self.logger.info(f"成功加载配置文件: {config_path}")
            return config

        except Exception as e:
            self.logger.error(f"加载配置文件失败 {config_path}: {str(e)}")
            return {}

    def load_rotation_config(self) -> Dict[str, Any]:
        """加载日志轮转配置

        Returns:
            轮转配置字典
        """
        return self.load_config('rotation_config')

    def reload_config(self, config_name: str) -> Dict[str, Any]:
        """重新加载配置（清除缓存）

        Args:
            config_name: 配置文件名

        Returns:
            配置字典
        """
        # 清除缓存
        if config_name in self._config_cache:
            del self._config_cache[config_name]

        return self.load_config(config_name)

    def get_nested_config(self, config: Dict[str, Any], key_path: str, default=None) -> Any:
        """获取嵌套配置值

        Args:
            config: 配置字典
            key_path: 键路径，用点号分隔，如 'log_rotation.ros2_logs.retention_days'
            default: 默认值

        Returns:
            配置值
        """
        try:
            keys = key_path.split('.')
            value = config

            for key in keys:
                value = value[key]

            return value
        except (KeyError, TypeError):
            return default

    def merge_configs(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """合并配置（递归合并）

        Args:
            base_config: 基础配置
            override_config: 覆盖配置

        Returns:
            合并后的配置
        """
        result = base_config.copy()

        for key, value in override_config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def validate_config(self, config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """验证配置是否符合schema

        Args:
            config: 配置字典
            schema: schema定义

        Returns:
            是否有效
        """
        try:
            for key, expected_type in schema.items():
                if key not in config:
                    self.logger.warning(f"配置缺少必需键: {key}")
                    return False

                if not isinstance(config[key], expected_type):
                    self.logger.warning(f"配置键 {key} 类型错误，期望 {expected_type}，实际 {type(config[key])}")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"配置验证失败: {str(e)}")
            return False


def load_logging_config(config_dir: str = None) -> Dict[str, Any]:
    """快速加载日志配置

    Args:
        config_dir: 配置文件目录

    Returns:
        日志配置字典
    """
    loader = ConfigLoader(config_dir)
    return loader.load_rotation_config()


# 默认配置schema
DEFAULT_ROTATION_SCHEMA = {
    'global': dict,
    'ros2_logs': dict,
    'sqlite_logs': dict,
    'compression': dict,
    'storage_monitoring': dict
}


def create_default_config() -> Dict[str, Any]:
    """创建默认配置

    Returns:
        默认配置字典
    """
    return {
        'global': {
            'check_interval': 3600,
            'enable_compression': True,
            'ros2_log_dir': '/var/log/ros',
            'database_path': 'library.db'
        },
        'ros2_logs': {
            'retention_days': 7,
            'max_file_size': 104857600,
            'compress_after_days': 3,
            'backup_count': 5
        },
        'sqlite_logs': {
            'retention_days': 30,
            'max_db_size': 524288000,
            'compress_after_days': 7,
            'vacuum_threshold': 0.8
        },
        'compression': {
            'enabled': True,
            'compression_level': 6,
            'async_compression': True
        },
        'storage_monitoring': {
            'enabled': True,
            'check_interval': 300,
            'warning_threshold': 80,
            'critical_threshold': 90,
            'emergency_threshold': 95,
            'auto_cleanup_enabled': True,
            'history_retention_days': 30,
            'alert_cooldown': 3600
        }
    }