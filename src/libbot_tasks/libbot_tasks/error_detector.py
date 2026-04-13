#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误检测机制主类 - 统一管理和协调各类错误检测
实现Story 2-3: 错误检测机制实现
"""

import rclpy
from rclpy.node import Node
from typing import Dict, List, Optional, Callable
import time
import threading
import os
import sys

# 添加detectors模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'detectors'))

class ErrorDetector:
    """错误检测机制主类 - 统一管理和协调各类错误检测"""

    def __init__(self, node: Node):
        """初始化错误检测器

        Args:
            node: ROS2节点实例
        """
        self.node = node
        self.detectors = {}
        self.error_callbacks = []
        self.is_running = False
        self.detection_thread = None

        # 从参数服务器加载配置
        self._load_parameters()

        # 初始化各类检测器
        self._init_detectors()

    def _load_parameters(self):
        """从ROS2参数服务器加载配置"""
        try:
            # 检测频率
            self.detection_frequency = self.node.declare_parameter(
                'detection.detection_frequency', 10.0
            ).value

            self.node.get_logger().info(f"错误检测器配置加载完成，检测频率: {self.detection_frequency}Hz")

        except Exception as e:
            self.node.get_logger().warn(f"参数加载失败，使用默认值: {str(e)}")
            self.detection_frequency = 10.0

    def _init_detectors(self):
        """初始化所有错误检测器"""
        try:
            from .detectors.localization_detector import LocalizationErrorDetector
            from .detectors.navigation_detector import NavigationErrorDetector
            from .detectors.perception_detector import PerceptionErrorDetector
            from .detectors.system_detector import SystemHealthDetector

            self.detectors = {
                'localization': LocalizationErrorDetector(self.node),
                'navigation': NavigationErrorDetector(self.node),
                'perception': PerceptionErrorDetector(self.node),
                'system': SystemHealthDetector(self.node)
            }

            self.node.get_logger().info("所有错误检测器初始化完成")

        except ImportError as e:
            self.node.get_logger().error(f"检测器模块导入失败: {str(e)}")
            # 创建模拟检测器以避免崩溃
            self._init_mock_detectors()

    def _init_mock_detectors(self):
        """初始化模拟检测器（用于测试）"""
        class MockDetector:
            def detect(self): return []
            def get_status(self): return {'status': 'mock'}
            def reset(self): pass

        self.detectors = {
            'localization': MockDetector(),
            'navigation': MockDetector(),
            'perception': MockDetector(),
            'system': MockDetector()
        }

    def register_error_callback(self, callback: Callable[[Dict], None]):
        """注册错误回调函数

        Args:
            callback: 回调函数，接收错误信息字典
        """
        self.error_callbacks.append(callback)
        self.node.get_logger().info(f"注册错误回调函数，当前回调数: {len(self.error_callbacks)}")

    def start_detection(self):
        """启动错误检测"""
        if self.is_running:
            self.node.get_logger().warn("错误检测器已在运行中")
            return

        self.is_running = True
        self.detection_thread = threading.Thread(
            target=self._detection_loop,
            daemon=True
        )
        self.detection_thread.start()

        self.node.get_logger().info("错误检测器启动")

    def stop_detection(self):
        """停止错误检测"""
        self.is_running = False
        if self.detection_thread:
            self.detection_thread.join(timeout=2.0)
        self.node.get_logger().info("错误检测器停止")

    def _detection_loop(self):
        """检测主循环"""
        detection_interval = 1.0 / self.detection_frequency

        while self.is_running and rclpy.ok():
            try:
                start_time = time.time()
                self._run_all_detections()

                # 控制检测频率
                elapsed_time = time.time() - start_time
                sleep_time = max(0, detection_interval - elapsed_time)
                time.sleep(sleep_time)

            except Exception as e:
                self.node.get_logger().error(f"检测循环错误: {str(e)}")
                time.sleep(0.1)  # 错误时短暂休眠

    def _run_all_detections(self):
        """运行所有检测器"""
        for detector_name, detector in self.detectors.items():
            try:
                errors = detector.detect()
                for error in errors:
                    self._handle_error(detector_name, error)
            except Exception as e:
                self.node.get_logger().error(
                    f"检测器 {detector_name} 运行错误: {str(e)}"
                )

    def _handle_error(self, detector_type: str, error_info: Dict):
        """处理检测到的错误

        Args:
            detector_type: 检测器类型
            error_info: 错误信息
        """
        # 完善错误信息
        error_info['detector_type'] = detector_type
        error_info['timestamp'] = time.time()
        error_info['error_id'] = f"{detector_type}_{int(time.time() * 1000)}"

        # 错误分类和严重程度分级
        error_info = self._classify_error(error_info)

        # 记录错误日志
        self._log_error(error_info)

        # 调用所有注册的回调函数
        for callback in self.error_callbacks:
            try:
                callback(error_info)
            except Exception as e:
                self.node.get_logger().error(
                    f"错误回调执行失败: {str(e)}"
                )

    def _classify_error(self, error_info: Dict) -> Dict:
        """错误分类和严重程度分级

        错误严重程度分级：
        - Fatal: 系统级故障，需要立即停机
        - Critical: 关键功能故障，需要L3恢复
        - Error: 功能错误，需要L2恢复
        - Warning: 轻微问题，需要L1恢复

        Args:
            error_info: 错误信息

        Returns:
            完善后的错误信息
        """
        error_type = error_info.get('error_type', 'unknown')

        # 根据错误类型分类
        severity_mapping = {
            # 定位相关错误
            'localization_lost': 'Critical',
            'localization_drift': 'Error',
            'low_localization_confidence': 'Warning',
            'localization_high_covariance': 'Error',

            # 导航相关错误
            'navigation_stuck': 'Error',
            'path_planning_failed': 'Error',
            'collision_imminent': 'Critical',
            'goal_unreachable': 'Error',

            # 感知相关错误
            'rfid_detection_failed': 'Warning',
            'sensor_timeout': 'Error',
            'perception_low_confidence': 'Warning',

            # 系统相关错误
            'node_crash': 'Fatal',
            'memory_exhausted': 'Critical',
            'cpu_overload': 'Error',
            'communication_timeout': 'Error'
        }

        error_info['severity'] = severity_mapping.get(error_type, 'Warning')
        error_info['recovery_level'] = self._get_recovery_level(error_info['severity'])

        return error_info

    def _get_recovery_level(self, severity: str) -> str:
        """根据严重程度确定恢复级别"""
        recovery_mapping = {
            'Fatal': 'L3',
            'Critical': 'L3',
            'Error': 'L2',
            'Warning': 'L1'
        }
        return recovery_mapping.get(severity, 'L1')

    def _log_error(self, error_info: Dict):
        """记录错误日志"""
        severity = error_info.get('severity', 'Warning')
        error_type = error_info.get('error_type', 'unknown')
        message = error_info.get('message', 'No message')

        log_message = (
            f"错误检测 [{severity}] {error_type}: {message} "
            f"(ID: {error_info.get('error_id', 'unknown')})"
        )

        if severity == 'Fatal':
            self.node.get_logger().fatal(log_message)
        elif severity == 'Critical':
            self.node.get_logger().error(log_message)
        elif severity == 'Error':
            self.node.get_logger().warn(log_message)
        else:
            self.node.get_logger().info(log_message)

    def get_detector_status(self) -> Dict:
        """获取所有检测器状态"""
        status = {}
        for name, detector in self.detectors.items():
            try:
                status[name] = detector.get_status()
            except Exception as e:
                status[name] = {'error': str(e)}
        return status

    def reset_detector(self, detector_name: str):
        """重置指定检测器"""
        if detector_name in self.detectors:
            try:
                self.detectors[detector_name].reset()
                self.node.get_logger().info(f"检测器 {detector_name} 已重置")
            except Exception as e:
                self.node.get_logger().error(f"重置检测器 {detector_name} 失败: {str(e)}")
        else:
            self.node.get_logger().warn(f"未知检测器: {detector_name}")


def main():
    """测试函数"""
    import rclpy

    rclpy.init()

    # 创建测试节点
    test_node = Node("error_detector_test")

    # 创建错误检测器实例
    error_detector = ErrorDetector(test_node)

    # 注册错误回调
    def error_callback(error_info):
        print(f"🔍 检测到错误: {error_info}")

    error_detector.register_error_callback(error_callback)

    # 启动检测
    error_detector.start_detection()

    try:
        # 运行测试10秒
        print("🧪 开始错误检测测试 (10秒)")
        rclpy.spin_once(test_node, timeout_sec=10.0)

    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
    finally:
        # 清理
        error_detector.stop_detection()
        test_node.destroy_node()
        rclpy.shutdown()

    print("✅ 错误检测测试完成")


if __name__ == "__main__":
    main()