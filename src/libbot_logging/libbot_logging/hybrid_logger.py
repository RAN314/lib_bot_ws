#!/usr/bin/env python3
"""
混合日志管理器 - HybridLogger

统一管理ROS2系统日志和SQLite业务日志，提供统一的日志接口。
"""

import time
import threading
import json
from typing import Dict, List, Optional
from datetime import datetime
import logging

from .ros2_logger import ROS2Logger
from .sqlite_logger import SQLiteLogger
from .log_buffer import LogBuffer
from .config_loader import ConfigLoader, load_logging_config


class HybridLogger:
    """混合日志管理器 - 统一管理ROS2和SQLite日志"""

    def __init__(self, config: Dict = None, config_file: str = None):
        """
        初始化混合日志管理器

        Args:
            config: 配置字典，包含ros2、sqlite、buffer等配置
            config_file: 配置文件名（不带.yaml后缀），如果提供则从文件加载配置
        """
        # 加载配置
        if config_file:
            loaded_config = load_logging_config()
            # 合并配置，参数配置优先于文件配置
            if config:
                from .config_loader import ConfigLoader
                loader = ConfigLoader()
                self.config = loader.merge_configs(loaded_config, config)
            else:
                self.config = loaded_config
        else:
            self.config = config or {}

        # 初始化各组件
        self.ros2_logger = ROS2Logger(self.config.get('ros2', {}))
        self.sqlite_logger = SQLiteLogger(self.config.get('sqlite', {}))
        self.log_buffer = LogBuffer(self.config.get('buffer', {}))
        self._lock = threading.RLock()

        # 日志级别映射
        self.level_priority = {
            'DEBUG': 0,
            'INFO': 1,
            'WARN': 2,
            'ERROR': 3
        }

        # 启动日志轮转
        self._start_log_rotation()

    def set_ros2_node(self, node):
        """设置ROS2节点引用"""
        self.ros2_logger.set_node(node)

    def log_system(self, level: str, message: str, component: str = None,
                   timestamp: float = None):
        """
        系统日志记录

        Args:
            level: 日志级别 (DEBUG/INFO/WARN/ERROR)
            message: 日志消息
            component: 组件名称
            timestamp: 时间戳，默认为当前时间
        """
        with self._lock:
            timestamp = timestamp or time.time()

            # ROS2日志输出
            self.ros2_logger.log(level, message, component)

            # 缓冲区记录
            self.log_buffer.add_log(
                log_type='system',
                level=level,
                message=message,
                component=component,
                timestamp=timestamp
            )

    def log_business(self, operation: str, details: dict, result: str = "success",
                    component: str = None):
        """
        业务日志记录

        Args:
            operation: 操作类型
            details: 操作详情
            result: 操作结果 (success/failed/warning)
            component: 组件名称
        """
        with self._lock:
            # SQLite日志存储
            self.sqlite_logger.log_operation(operation, details, result, component)

            # 缓冲区记录
            self.log_buffer.add_log(
                log_type='business',
                level='INFO' if result == 'success' else 'ERROR',
                message=f"Operation: {operation}, Result: {result}",
                component=component or operation
            )

    def query_logs(self, log_type: str = None, level: str = None,
                  component: str = None, start_time: float = None,
                  end_time: float = None, limit: int = 100) -> List[dict]:
        """
        查询日志

        Args:
            log_type: 日志类型 (system/business)
            level: 日志级别
            component: 组件名称
            start_time: 开始时间戳
            end_time: 结束时间戳
            limit: 返回结果数量限制

        Returns:
            日志条目列表
        """
        filters = {
            'log_type': log_type,
            'level': level,
            'component': component,
            'start_time': start_time,
            'end_time': end_time,
            'limit': limit
        }

        # 优先从缓冲区查询实时日志
        if not start_time or start_time > (time.time() - 300):  # 5分钟内的日志
            buffer_logs = self.log_buffer.query_logs(filters)
            if len(buffer_logs) >= limit:
                return buffer_logs[:limit]

        # 从SQLite查询历史日志
        return self.sqlite_logger.query_logs(filters)

    def flush_buffer(self):
        """刷新缓冲区到持久化存储"""
        with self._lock:
            self.log_buffer.flush_to_sqlite(self.sqlite_logger)

    def get_statistics(self) -> Dict:
        """获取日志统计信息"""
        return {
            'buffer_stats': self.log_buffer.get_statistics(),
            'sqlite_stats': self.sqlite_logger.get_statistics()
        }

    def set_min_level(self, level: str):
        """设置最低日志级别"""
        self.ros2_logger.set_min_level(level)

    def emergency_log(self, message: str, component: str = "EMERGENCY"):
        """紧急日志记录 - 同步写入，不经过缓冲"""
        timestamp = time.time()

        # 直接写入SQLite
        self.sqlite_logger._insert_log_direct({
            'timestamp': timestamp,
            'log_type': 'emergency',
            'level': 'ERROR',
            'message': message,
            'component': component
        })

        # ROS2输出
        if self.ros2_logger.node:
            self.ros2_logger.node.get_logger().error(f"[EMERGENCY] {message}")

    def _start_log_rotation(self):
        """启动日志轮转"""
        try:
            # 检查是否启用日志轮转
            if self.config.get('enable_log_rotation', True):
                # 启动SQLite日志轮转
                if hasattr(self.sqlite_logger, 'start_log_rotation'):
                    self.sqlite_logger.start_log_rotation()
                    logging.getLogger(__name__).info("日志轮转已启动")
        except Exception as e:
            logging.getLogger(__name__).warning(f"启动日志轮转失败: {str(e)}")

    def rotate_logs(self, log_type: str = 'all'):
        """手动触发日志轮转

        Args:
            log_type: 日志类型 (sqlite_logs/ros2_logs/all)
        """
        try:
            if hasattr(self.sqlite_logger, 'manual_rotate_logs'):
                self.sqlite_logger.manual_rotate_logs(log_type)
        except Exception as e:
            logging.getLogger(__name__).error(f"手动轮转失败: {str(e)}")

    def cleanup_logs(self, log_type: str = 'all'):
        """手动触发日志清理

        Args:
            log_type: 日志类型 (sqlite_logs/ros2_logs/all)
        """
        try:
            if hasattr(self.sqlite_logger, 'manual_cleanup_logs'):
                self.sqlite_logger.manual_cleanup_logs(log_type)
        except Exception as e:
            logging.getLogger(__name__).error(f"手动清理失败: {str(e)}")

    def get_storage_info(self) -> Dict:
        """获取存储信息"""
        try:
            if hasattr(self.sqlite_logger, 'get_storage_info'):
                return self.sqlite_logger.get_storage_info()
        except Exception as e:
            logging.getLogger(__name__).error(f"获取存储信息失败: {str(e)}")
        return {}

    def close(self):
        """关闭日志管理器"""
        try:
            # 刷新缓冲区
            self.flush_buffer()

            # 停止日志轮转
            if hasattr(self.sqlite_logger, 'stop_log_rotation'):
                self.sqlite_logger.stop_log_rotation()

            # 关闭SQLite日志
            self.sqlite_logger.close()

            logging.getLogger(__name__).info("混合日志管理器已关闭")
        except Exception as e:
            logging.getLogger(__name__).error(f"关闭日志管理器失败: {str(e)}")