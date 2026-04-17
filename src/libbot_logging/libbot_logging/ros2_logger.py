#!/usr/bin/env python3
"""
ROS2系统日志处理器

负责捕获和处理ROS2系统的日志输出，提供统一的接口。
"""

import time
from typing import Dict, Optional
import rclpy
from rclpy.node import Node


class ROS2Logger:
    """ROS2系统日志处理器"""

    def __init__(self, config: Dict):
        """
        初始化ROS2日志处理器

        Args:
            config: ROS2日志配置
        """
        self.node: Optional[Node] = None
        self.config = config

        # 日志级别配置
        self.log_levels = config.get('levels', ['DEBUG', 'INFO', 'WARN', 'ERROR'])
        self.min_level = config.get('min_level', 'INFO')

        # 日志级别映射到ROS2级别
        self.ros2_level_map = {
            'DEBUG': rclpy.logging.LoggingSeverity.DEBUG,
            'INFO': rclpy.logging.LoggingSeverity.INFO,
            'WARN': rclpy.logging.LoggingSeverity.WARN,
            'ERROR': rclpy.logging.LoggingSeverity.ERROR
        }

    def set_node(self, node: Node):
        """设置ROS2节点引用"""
        self.node = node

        # 设置节点日志级别
        if hasattr(node, 'get_logger'):
            min_level = self.ros2_level_map.get(self.min_level, rclpy.logging.LoggingSeverity.INFO)
            node.get_logger().set_level(min_level)

    def log(self, level: str, message: str, component: str = None):
        """
        ROS2日志记录

        Args:
            level: 日志级别 (DEBUG/INFO/WARN/ERROR)
            message: 日志消息
            component: 组件名称
        """
        if not self.node:
            # 如果没有ROS2节点，使用Python logging作为后备
            self._fallback_log(level, message, component)
            return

        # 检查日志级别
        if not self._should_log(level):
            return

        formatted_msg = self._format_message(level, message, component)

        try:
            logger = self.node.get_logger()

            if level == "DEBUG":
                logger.debug(formatted_msg)
            elif level == "INFO":
                logger.info(formatted_msg)
            elif level == "WARN":
                logger.warn(formatted_msg)
            elif level == "ERROR":
                logger.error(formatted_msg)
            else:
                logger.info(formatted_msg)  # 默认级别

        except Exception as e:
            # ROS2日志失败时的后备方案
            self._fallback_log(level, f"ROS2_LOG_FAILED: {e} - {message}", component)

    def _should_log(self, level: str) -> bool:
        """检查是否应该记录该级别的日志"""
        level_priority = {
            'DEBUG': 0,
            'INFO': 1,
            'WARN': 2,
            'ERROR': 3
        }

        current_priority = level_priority.get(level, 1)
        min_priority = level_priority.get(self.min_level, 1)

        return current_priority >= min_priority

    def _format_message(self, level: str, message: str, component: str = None) -> str:
        """格式化日志消息"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        if component:
            return f"[{timestamp}] [{level}] [{component}] {message}"
        else:
            return f"[{timestamp}] [{level}] {message}"

    def _fallback_log(self, level: str, message: str, component: str = None):
        """后备日志记录 - 当ROS2不可用时使用Python logging"""
        import logging

        formatted_msg = self._format_message(level, message, component)

        if level == "DEBUG":
            logging.debug(formatted_msg)
        elif level == "INFO":
            logging.info(formatted_msg)
        elif level == "WARN":
            logging.warning(formatted_msg)
        elif level == "ERROR":
            logging.error(formatted_msg)
        else:
            logging.info(formatted_msg)

    def set_min_level(self, level: str):
        """设置最低日志级别"""
        if level in self.ros2_level_map:
            self.min_level = level

            # 如果已设置节点，更新节点日志级别
            if self.node and hasattr(self.node, 'get_logger'):
                ros2_level = self.ros2_level_map[level]
                self.node.get_logger().set_level(ros2_level)

    def is_enabled(self) -> bool:
        """检查ROS2日志是否可用"""
        return self.node is not None and hasattr(self.node, 'get_logger')

    def get_node_name(self) -> str:
        """获取节点名称"""
        if self.node:
            return self.node.get_name()
        return "unknown"