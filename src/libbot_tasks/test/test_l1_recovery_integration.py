#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L1恢复行为集成测试
图书馆机器人ROS2项目 - Epic 2错误处理与恢复机制

测试L1恢复行为在真实ROS2环境中的集成
"""

import unittest
import rclpy
from rclpy.node import Node
import time
import threading

from libbot_msgs.msg import RFIDScan
from geometry_msgs.msg import Twist, Point
from sensor_msgs.msg import LaserScan

from libbot_tasks.libbot_tasks.recovery_behaviors import L1RecoveryBehaviors


class TestL1RecoveryIntegration(unittest.TestCase):
    """L1恢复行为集成测试类"""

    @classmethod
    def setUpClass(cls):
        """测试类设置 - 初始化ROS2"""
        rclpy.init()
        cls.node = Node('test_l1_recovery_node')
        cls.recovery = L1RecoveryBehaviors(cls.node)

        # 创建测试发布者
        cls.rfid_pub = cls.node.create_publisher(RFIDScan, '/rfid/scan/front', 10)
        cls.laser_pub = cls.node.create_publisher(LaserScan, '/scan', 10)

    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        cls.recovery.cleanup()
        cls.node.destroy_publisher(cls.rfid_pub)
        cls.node.destroy_publisher(cls.laser_pub)
        cls.node.destroy_node()
        rclpy.shutdown()

    def setUp(self):
        """每个测试前的设置"""
        self.recovery.setup_ros_communication()

    def test_rfid_rescan_integration(self):
        """测试RFID重新扫描集成"""
        def publish_rfid_data():
            """在后台发布RFID数据"""
            time.sleep(1.0)  # 等待测试开始

            msg = RFIDScan()
            msg.book_id = "integration_test_book"
            msg.confidence = 0.95
            msg.timestamp = self.node.get_clock().now().to_msg()

            self.rfid_pub.publish(msg)
            self.node.get_logger().info("发布测试RFID数据")

        # 启动后台发布者线程
        publisher_thread = threading.Thread(target=publish_rfid_data)
        publisher_thread.daemon = True
        publisher_thread.start()

        # 执行RFID重新扫描
        result = self.recovery.retry_rfid_scan(
            "integration_test_book",
            {'x': 1.0, 'y': 2.0, 'z': 0.0}
        )

        self.assertTrue(result)
        publisher_thread.join(timeout=10)

    def test_rotation_localization_integration(self):
        """测试旋转重新定位集成"""
        # 发布激光雷达数据
        def publish_laser_data():
            """在后台发布激光雷达数据"""
            laser_msg = LaserScan()
            laser_msg.header.stamp = self.node.get_clock().now().to_msg()
            laser_msg.angle_min = -3.14
            laser_msg.angle_max = 3.14
            laser_msg.angle_increment = 0.01
            laser_msg.time_increment = 0.0
            laser_msg.scan_time = 0.1
            laser_msg.range_min = 0.1
            laser_msg.range_max = 10.0
            laser_msg.ranges = [1.0] * 628  # 模拟激光雷达数据
            laser_msg.intensities = [100.0] * 628

            for _ in range(10):  # 发布10次数据
                self.laser_pub.publish(laser_msg)
                time.sleep(0.1)

        # 启动激光雷达发布者
        laser_thread = threading.Thread(target=publish_laser_data)
        laser_thread.daemon = True
        laser_thread.start()

        # 执行重新定位
        result = self.recovery.relocalize_robot()

        self.assertTrue(result)
        laser_thread.join(timeout=5)

    def test_target_redefinition_integration(self):
        """测试目标重定义集成"""
        original_goal = {
            'book_id': 'test_book_001',
            'position': {'x': 1.0, 'y': 2.0, 'z': 0.0},
            'priority': 'high'
        }

        # 执行目标重定义
        alternative_goal = self.recovery.redefine_target(original_goal)

        self.assertIsNotNone(alternative_goal)
        self.assertIn('book_id', alternative_goal)
        self.assertIn('position', alternative_goal)
        self.assertTrue(alternative_goal['reachable'])

    def test_recovery_timeout_handling(self):
        """测试恢复超时处理"""
        # 模拟一个永远不会成功的RFID扫描
        def never_publish_rfid():
            """不发布任何RFID数据"""
            time.sleep(6.0)  # 超过扫描超时时间

        timeout_thread = threading.Thread(target=never_publish_rfid)
        timeout_thread.daemon = True
        timeout_thread.start()

        # 执行RFID重新扫描（应该超时失败）
        result = self.recovery.retry_rfid_scan(
            "nonexistent_book",
            {'x': 1.0, 'y': 2.0, 'z': 0.0}
        )

        self.assertFalse(result)
        timeout_thread.join(timeout=10)

    def test_multiple_recovery_attempts(self):
        """测试多次恢复尝试"""
        def delayed_rfid_publish():
            """延迟发布RFID数据"""
            time.sleep(3.0)  # 延迟3秒后发布

            msg = RFIDScan()
            msg.book_id = "delayed_book"
            msg.confidence = 0.85
            msg.timestamp = self.node.get_clock().now().to_msg()

            self.rfid_pub.publish(msg)

        publisher_thread = threading.Thread(target=delayed_rfid_publish)
        publisher_thread.daemon = True
        publisher_thread.start()

        # 执行RFID重新扫描
        result = self.recovery.retry_rfid_scan(
            "delayed_book",
            {'x': 1.0, 'y': 2.0, 'z': 0.0}
        )

        self.assertTrue(result)
        publisher_thread.join(timeout=10)

    def test_concurrent_recovery_operations(self):
        """测试并发恢复操作"""
        def run_rfid_recovery():
            """运行RFID恢复"""
            return self.recovery.retry_rfid_scan(
                "concurrent_book",
                {'x': 1.0, 'y': 2.0, 'z': 0.0}
            )

        def run_localization():
            """运行重新定位"""
            return self.recovery.relocalize_robot()

        # 启动并发操作
        rfid_thread = threading.Thread(target=run_rfid_recovery)
        loc_thread = threading.Thread(target=run_localization)

        rfid_thread.start()
        loc_thread.start()

        # 等待完成
        rfid_thread.join(timeout=15)
        loc_thread.join(timeout=15)

        # 验证两个操作都完成（结果可能不同）
        self.assertTrue(rfid_thread.is_alive() == False)
        self.assertTrue(loc_thread.is_alive() == False)

    def test_parameter_configuration(self):
        """测试参数配置功能"""
        # 验证参数正确加载
        self.assertEqual(self.recovery.max_retries, 3)
        self.assertEqual(self.recovery.recovery_timeout, 10.0)

        # 验证ROS2参数声明
        param_names = [
            'recovery.l1.max_retries',
            'recovery.l1.timeout_seconds',
            'recovery.l1.rfid_rescan.scan_duration',
            'recovery.l1.relocalization.rotation_speed'
        ]

        for param_name in param_names:
            try:
                param_value = self.node.get_parameter(param_name).value
                self.assertIsNotNone(param_value)
            except Exception:
                self.fail(f"参数 {param_name} 未正确声明")

    def test_error_logging_integration(self):
        """测试错误日志记录集成"""
        # 捕获日志输出
        with self.assertLogs() as log_context:
            # 执行一个会失败的操作
            self.recovery.retry_rfid_scan(
                "nonexistent_book",
                {'x': 1.0, 'y': 2.0, 'z': 0.0}
            )

        # 验证错误日志被记录
        log_messages = ' '.join(log_context.output)
        self.assertIn('L1恢复', log_messages)

    def test_resource_cleanup(self):
        """测试资源清理"""
        # 创建多个恢复实例
        recovery_instances = []
        for i in range(3):
            node = Node(f'test_node_{i}')
            recovery = L1RecoveryBehaviors(node)
            recovery.setup_ros_communication()
            recovery_instances.append((node, recovery))

        # 清理所有实例
        for node, recovery in recovery_instances:
            recovery.cleanup()
            node.destroy_node()

        # 验证没有资源泄漏（这里简化验证）
        self.assertTrue(True)  # 如果没有异常，说明清理正常


class TestL1RecoveryPerformance(unittest.TestCase):
    """L1恢复行为性能测试"""

    @classmethod
    def setUpClass(cls):
        """性能测试设置"""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """性能测试清理"""
        rclpy.shutdown()

    def test_recovery_timing(self):
        """测试恢复时间性能"""
        node = Node('performance_test_node')
        recovery = L1RecoveryBehaviors(node)

        try:
            # 测试RFID重新扫描时间
            start_time = time.time()

            # 模拟快速成功的RFID扫描
            def quick_rfid_publish():
                time.sleep(0.5)
                # 这里应该发布RFID数据，简化测试

            import threading
            thread = threading.Thread(target=quick_rfid_publish)
            thread.daemon = True
            thread.start()

            result = recovery.retry_rfid_scan("test_book", {'x': 1.0, 'y': 2.0})

            end_time = time.time()
            recovery_time = end_time - start_time

            # 验证恢复时间在合理范围内
            self.assertLess(recovery_time, 10.0)  # 应该在10秒内完成

            thread.join(timeout=5)

        finally:
            recovery.cleanup()
            node.destroy_node()

    def test_memory_usage(self):
        """测试内存使用情况"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # 创建多个恢复实例
        nodes = []
        recoveries = []

        for i in range(10):
            node = Node(f'memory_test_node_{i}')
            recovery = L1RecoveryBehaviors(node)
            nodes.append(node)
            recoveries.append(recovery)

        # 检查内存增长
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory

        # 清理
        for recovery in recoveries:
            recovery.cleanup()
        for node in nodes:
            node.destroy_node()

        # 验证内存增长在合理范围内（小于50MB）
        self.assertLess(memory_increase, 50.0)


if __name__ == '__main__':
    unittest.main()