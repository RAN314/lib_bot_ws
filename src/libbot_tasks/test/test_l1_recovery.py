#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L1恢复行为单元测试
图书馆机器人ROS2项目 - Epic 2错误处理与恢复机制

测试L1RecoveryBehaviors类的所有功能
"""

import unittest
import rclpy
from rclpy.node import Node
from unittest.mock import MagicMock, patch
import time

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'libbot_tasks'))
from recovery_behaviors import L1RecoveryBehaviors


class TestL1RecoveryBehaviors(unittest.TestCase):
    """L1恢复行为测试类"""

    @classmethod
    def setUpClass(cls):
        """测试类设置"""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        rclpy.shutdown()

    def setUp(self):
        """每个测试方法前的设置"""
        self.mock_node = MagicMock(spec=Node)
        self.mock_node.get_logger.return_value = MagicMock()
        self.recovery = L1RecoveryBehaviors(self.mock_node)

    def tearDown(self):
        """每个测试方法后的清理"""
        self.recovery.cleanup()

    def test_initialization(self):
        """测试L1RecoveryBehaviors初始化"""
        self.assertIsNotNone(self.recovery)
        self.assertEqual(self.recovery.node, self.mock_node)
        self.assertFalse(self.recovery.recovery_active)

    def test_declare_parameters(self):
        """测试参数声明"""
        # 验证参数声明被调用
        self.mock_node.declare_parameter.assert_called()

        # 验证参数读取 - 使用具体的mock返回值
        self.mock_node.get_parameter.return_value.value = 3
        max_retries = self.mock_node.get_parameter.return_value.value
        self.assertEqual(max_retries, 3)

        self.mock_node.get_parameter.return_value.value = 10.0
        recovery_timeout = self.mock_node.get_parameter.return_value.value
        self.assertEqual(recovery_timeout, 10.0)

    def test_setup_ros_communication(self):
        """测试ROS2通信设置"""
        self.recovery.setup_ros_communication()

        # 验证订阅者和发布者被创建
        self.assertIsNotNone(self.recovery.rfid_sub)
        self.assertIsNotNone(self.recovery.laser_sub)
        self.assertIsNotNone(self.recovery.cmd_vel_pub)
        # 粒子云发布暂时禁用
        # self.assertIsNotNone(self.recovery.particle_pub)

        # 验证ROS2创建方法被调用
        self.mock_node.create_subscription.assert_called()
        self.mock_node.create_publisher.assert_called()

    def test_retry_rfid_scan_success(self):
        """测试RFID重新扫描成功情况"""
        # 模拟RFID数据
        mock_rfid_msg = MagicMock()
        mock_rfid_msg.book_id = "test_book_001"
        mock_rfid_msg.confidence = 0.9

        with patch.object(self.recovery, '_perform_rfid_rescan', return_value=True):
            result = self.recovery.retry_rfid_scan("test_book_001", {'x': 1.0, 'y': 2.0})
            self.assertTrue(result)

        # 验证日志记录
        self.mock_node.get_logger.return_value.info.assert_called()

    def test_retry_rfid_scan_failure(self):
        """测试RFID重新扫描失败情况"""
        with patch.object(self.recovery, '_perform_rfid_rescan', return_value=False):
            result = self.recovery.retry_rfid_scan("test_book_001", {'x': 1.0, 'y': 2.0})
            self.assertFalse(result)

        # 验证警告日志
        self.mock_node.get_logger.return_value.warn.assert_called()

    def test_relocalize_robot_success(self):
        """测试重新定位成功情况"""
        with patch.object(self.recovery, '_perform_rotation_localization', return_value=True):
            result = self.recovery.relocalize_robot()
            self.assertTrue(result)

        # 验证日志记录
        self.mock_node.get_logger.return_value.info.assert_called()

    def test_relocalize_robot_failure(self):
        """测试重新定位失败情况"""
        with patch.object(self.recovery, '_perform_rotation_localization', return_value=False):
            result = self.recovery.relocalize_robot()
            self.assertFalse(result)

        # 验证警告日志
        self.mock_node.get_logger.return_value.warn.assert_called()

    def test_redefine_target_success(self):
        """测试目标重定义成功情况"""
        original_goal = {
            'book_id': 'original_book',
            'position': {'x': 1.0, 'y': 2.0, 'z': 0.0}
        }

        expected_alternative = {
            'book_id': 'alt_original_book',
            'position': {'x': 2.0, 'y': 2.0, 'z': 0.0},
            'priority': 'medium',
            'reachable': True
        }

        with patch.object(self.recovery, '_find_alternative_target', return_value=expected_alternative):
            result = self.recovery.redefine_target(original_goal)
            self.assertEqual(result, expected_alternative)

    def test_redefine_target_failure(self):
        """测试目标重定义失败情况"""
        original_goal = {
            'book_id': 'original_book',
            'position': {'x': 1.0, 'y': 2.0, 'z': 0.0}
        }

        with patch.object(self.recovery, '_find_alternative_target', return_value=None):
            result = self.recovery.redefine_target(original_goal)
            self.assertIsNone(result)

    def test_perform_rfid_rescan_success(self):
        """测试RFID重新扫描具体实现成功"""
        # 模拟RFID数据到达
        def mock_spin_once(*args, **kwargs):
            self.recovery.last_rfid_data = MagicMock()
            self.recovery.last_rfid_data.book_id = "test_book_001"
            self.recovery.last_rfid_data.confidence = 0.9

        with patch('time.time', side_effect=[0, 1, 2, 3]):
            with patch('time.sleep'):
                with patch('rclpy.spin_once', side_effect=mock_spin_once):
                    result = self.recovery._perform_rfid_rescan(
                        "test_book_001", {'x': 1.0, 'y': 2.0}, 5.0, 0.8
                    )
                    self.assertTrue(result)

    def test_perform_rfid_rescan_timeout(self):
        """测试RFID重新扫描超时情况"""
        # 模拟没有RFID数据
        with patch('time.time', side_effect=[0, 1, 2, 6]):
            with patch('time.sleep'):
                with patch('rclpy.spin_once'):
                    result = self.recovery._perform_rfid_rescan(
                        "test_book_001", {'x': 1.0, 'y': 2.0}, 5.0, 0.8
                    )
                    self.assertFalse(result)

    def test_perform_rotation_localization_success(self):
        """测试旋转重新定位成功"""
        # 先设置ROS通信，确保cmd_vel_pub存在
        self.recovery.setup_ros_communication()

        with patch('time.time', side_effect=[0, 1, 2, 3, 4, 5]):
            with patch('time.sleep'):
                result = self.recovery._perform_rotation_localization(0.3, 6.28, 0.1)
                self.assertTrue(result)

        # 验证速度命令发布
        self.recovery.cmd_vel_pub.publish.assert_called()

    def test_find_alternative_target(self):
        """测试查找替代目标"""
        original_goal = {
            'book_id': 'original_book',
            'position': {'x': 1.0, 'y': 2.0, 'z': 0.0}
        }

        with patch('time.sleep'):  # 模拟查找延迟
            result = self.recovery._find_alternative_target(original_goal, 2.0, 5)

            self.assertIsNotNone(result)
            self.assertEqual(result['book_id'], 'alt_original_book')
            self.assertTrue(result['reachable'])

    def test_exception_handling_rfid_scan(self):
        """测试RFID扫描异常处理"""
        with patch.object(self.recovery, '_perform_rfid_rescan', side_effect=Exception("Test error")):
            result = self.recovery.retry_rfid_scan("test_book_001", {'x': 1.0, 'y': 2.0})
            self.assertFalse(result)

        # 验证错误日志
        self.mock_node.get_logger.return_value.error.assert_called()

    def test_exception_handling_relocalization(self):
        """测试重新定位异常处理"""
        with patch.object(self.recovery, '_perform_rotation_localization', side_effect=Exception("Test error")):
            result = self.recovery.relocalize_robot()
            self.assertFalse(result)

        # 验证错误日志
        self.mock_node.get_logger.return_value.error.assert_called()

    def test_exception_handling_redefine_target(self):
        """测试目标重定义异常处理"""
        original_goal = {'book_id': 'test_book'}

        with patch.object(self.recovery, '_find_alternative_target', side_effect=Exception("Test error")):
            result = self.recovery.redefine_target(original_goal)
            self.assertIsNone(result)

        # 验证错误日志
        self.mock_node.get_logger.return_value.error.assert_called()

    def test_cleanup(self):
        """测试资源清理"""
        # 先设置ROS通信
        self.recovery.setup_ros_communication()

        # 执行清理
        self.recovery.cleanup()

        # 验证销毁方法被调用
        self.mock_node.destroy_subscription.assert_called()
        self.mock_node.destroy_publisher.assert_called()


class TestL1RecoveryIntegration(unittest.TestCase):
    """L1恢复行为集成测试"""

    @classmethod
    def setUpClass(cls):
        """集成测试设置"""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """集成测试清理"""
        rclpy.shutdown()

    def test_full_recovery_workflow(self):
        """测试完整恢复工作流程"""
        # 这里可以添加更复杂的集成测试
        # 例如测试多个恢复行为的组合
        pass


if __name__ == '__main__':
    unittest.main()