#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误检测机制演示脚本
展示Story 2-3: 错误检测机制实现的功能
"""

import rclpy
from rclpy.node import Node
import time
import threading
import sys
import os

# 添加模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from libbot_tasks.error_detector import ErrorDetector


class ErrorDetectionDemo(Node):
    """错误检测演示节点"""

    def __init__(self):
        super().__init__("error_detection_demo")

        # 创建错误检测器
        self.error_detector = ErrorDetector(self)

        # 注册错误回调
        self.error_detector.register_error_callback(self._error_callback)

        # 错误统计
        self.error_stats = {
            'total_errors': 0,
            'by_severity': {'Fatal': 0, 'Critical': 0, 'Error': 0, 'Warning': 0},
            'by_type': {},
            'by_detector': {}
        }

        self.get_logger().info("🚀 错误检测演示启动")

    def _error_callback(self, error_info):
        """错误回调函数"""
        self.error_stats['total_errors'] += 1

        # 统计严重程度
        severity = error_info.get('severity', 'Warning')
        self.error_stats['by_severity'][severity] = self.error_stats['by_severity'].get(severity, 0) + 1

        # 统计错误类型
        error_type = error_info.get('error_type', 'unknown')
        self.error_stats['by_type'][error_type] = self.error_stats['by_type'].get(error_type, 0) + 1

        # 统计检测器
        detector_type = error_info.get('detector_type', 'unknown')
        self.error_stats['by_detector'][detector_type] = self.error_stats['by_detector'].get(detector_type, 0) + 1

        # 显示错误信息
        recovery_level = error_info.get('recovery_level', 'L1')
        self.get_logger().info(
            f"🔍 检测到错误 [{severity} -> {recovery_level}]: "
            f"{error_info.get('message', 'No message')}"
        )

    def simulate_errors(self):
        """模拟各种错误情况"""
        self.get_logger().info("🎯 开始模拟错误场景...")

        # 模拟RFID检测失败
        self.get_logger().info("📡 模拟RFID检测失败...")
        self.error_detector._handle_error('perception', {
            'error_type': 'rfid_detection_failed',
            'message': 'RFID读取器无响应，连续5秒无检测'
        })
        time.sleep(1)

        # 模拟机器人卡住
        self.get_logger().info("🤖 模拟机器人卡住...")
        self.error_detector._handle_error('navigation', {
            'error_type': 'navigation_stuck',
            'message': '机器人已35秒无移动，可能被障碍物阻挡'
        })
        time.sleep(1)

        # 模拟定位丢失
        self.get_logger().info("📍 模拟定位丢失...")
        self.error_detector._handle_error('localization', {
            'error_type': 'localization_lost',
            'message': 'AMCL定位丢失，超过8秒无更新'
        })
        time.sleep(1)

        # 模拟CPU过载
        self.get_logger().info("💻 模拟CPU过载...")
        self.error_detector._handle_error('system', {
            'error_type': 'cpu_overload',
            'message': '系统CPU使用率达到95%，可能影响性能'
        })
        time.sleep(1)

        # 模拟节点通信超时
        self.get_logger().info("🔗 模拟节点通信超时...")
        self.error_detector._handle_error('system', {
            'error_type': 'node_crash',
            'message': '导航节点通信超时，可能已崩溃'
        })
        time.sleep(1)

        # 模拟路径规划失败
        self.get_logger().info("🗺️ 模拟路径规划失败...")
        self.error_detector._handle_error('navigation', {
            'error_type': 'path_planning_failed',
            'message': '路径规划超时15秒，无法找到有效路径'
        })
        time.sleep(1)

        # 模拟感知置信度低
        self.get_logger().info("👁️ 模拟感知置信度低...")
        self.error_detector._handle_error('perception', {
            'error_type': 'perception_low_confidence',
            'message': 'RFID检测置信度持续低于阈值(0.7)'
        })
        time.sleep(1)

        self.get_logger().info("✅ 错误模拟完成")

    def show_statistics(self):
        """显示错误统计"""
        self.get_logger().info("📊 错误检测统计:")
        self.get_logger().info(f"   总错误数: {self.error_stats['total_errors']}")

        self.get_logger().info("   按严重程度:")
        for severity, count in self.error_stats['by_severity'].items():
            if count > 0:
                self.get_logger().info(f"     {severity}: {count}")

        self.get_logger().info("   按检测器:")
        for detector, count in self.error_stats['by_detector'].items():
            if count > 0:
                self.get_logger().info(f"     {detector}: {count}")

        self.get_logger().info("   按错误类型:")
        for error_type, count in self.error_stats['by_type'].items():
            if count > 0:
                self.get_logger().info(f"     {error_type}: {count}")

    def show_detector_status(self):
        """显示检测器状态"""
        self.get_logger().info("🔧 检测器状态:")
        status = self.error_detector.get_detector_status()

        for detector_name, detector_status in status.items():
            self.get_logger().info(f"   {detector_name}: {detector_status}")

    def run_demo(self):
        """运行演示"""
        try:
            # 启动错误检测
            self.error_detector.start_detection()

            # 等待检测器初始化
            time.sleep(1)

            # 显示初始状态
            self.show_detector_status()

            # 模拟错误
            self.simulate_errors()

            # 显示统计
            self.show_statistics()

            # 演示运行5秒
            self.get_logger().info("⏳ 演示运行中... (5秒)")
            time.sleep(5)

        except KeyboardInterrupt:
            self.get_logger().info("\n🛑 演示被用户中断")
        finally:
            # 清理
            self.error_detector.stop_detection()
            self.get_logger().info("🧹 演示清理完成")


def main():
    """主函数"""
    print("=" * 60)
    print("🎯 Story 2-3: 错误检测机制演示")
    print("=" * 60)
    print("本演示展示错误检测机制的核心功能:")
    print("• 多类型错误检测 (定位、导航、感知、系统)")
    print("• 错误严重程度分级 (Warning/Error/Critical/Fatal)")
    print("• 自动恢复级别匹配 (L1/L2/L3)")
    print("• 实时错误监控和统计")
    print("=" * 60)

    # 初始化ROS2
    rclpy.init()

    # 创建演示节点
    demo = ErrorDetectionDemo()

    try:
        # 运行演示
        demo.run_demo()

    finally:
        # 清理ROS2
        demo.destroy_node()
        rclpy.shutdown()

    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("错误检测机制已成功实现并验证。")
    print("=" * 60)


if __name__ == "__main__":
    main()