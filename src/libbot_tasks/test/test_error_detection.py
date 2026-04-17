#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误检测机制单元测试
验证Story 2-3: 错误检测机制实现
"""

import unittest
import rclpy
from rclpy.node import Node
import time
import threading
from unittest.mock import Mock, patch
import sys
import os

# 添加模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from libbot_tasks.error_detector import ErrorDetector
from libbot_tasks.detectors.localization_detector import LocalizationErrorDetector
from libbot_tasks.detectors.navigation_detector import NavigationErrorDetector
from libbot_tasks.detectors.perception_detector import PerceptionErrorDetector
from libbot_tasks.detectors.system_detector import SystemHealthDetector


class TestErrorDetector(unittest.TestCase):
    """ErrorDetector主类测试"""

    def setUp(self):
        """测试设置"""
        rclpy.init()
        self.test_node = Node("error_detector_test")

    def tearDown(self):
        """测试清理"""
        self.test_node.destroy_node()
        rclpy.shutdown()

    def test_error_detector_initialization(self):
        """测试错误检测器初始化"""
        detector = ErrorDetector(self.test_node)

        # 验证检测器初始化
        self.assertEqual(len(detector.detectors), 4)
        self.assertIn('localization', detector.detectors)
        self.assertIn('navigation', detector.detectors)
        self.assertIn('perception', detector.detectors)
        self.assertIn('system', detector.detectors)
        self.assertFalse(detector.is_running)
        self.assertEqual(len(detector.error_callbacks), 0)

    def test_error_callback_registration(self):
        """测试错误回调注册"""
        detector = ErrorDetector(self.test_node)

        # 创建模拟回调
        mock_callback = Mock()
        detector.register_error_callback(mock_callback)

        # 验证回调注册
        self.assertEqual(len(detector.error_callbacks), 1)
        self.assertEqual(detector.error_callbacks[0], mock_callback)

    def test_error_classification(self):
        """测试错误分类"""
        detector = ErrorDetector(self.test_node)

        # 测试定位错误分类
        error_info = {
            'error_type': 'localization_lost',
            'message': '定位丢失'
        }
        classified_error = detector._classify_error(error_info)

        self.assertEqual(classified_error['severity'], 'Critical')
        self.assertEqual(classified_error['recovery_level'], 'L3')

        # 测试导航错误分类
        error_info = {
            'error_type': 'navigation_stuck',
            'message': '机器人卡住'
        }
        classified_error = detector._classify_error(error_info)

        self.assertEqual(classified_error['severity'], 'Error')
        self.assertEqual(classified_error['recovery_level'], 'L2')

    def test_error_logging(self):
        """测试错误日志记录"""
        detector = ErrorDetector(self.test_node)

        # 测试不同严重程度的错误日志
        error_info = {
            'error_type': 'test_error',
            'message': '测试错误',
            'severity': 'Error',
            'error_id': 'test_001'
        }

        # 验证不会抛出异常
        try:
            detector._log_error(error_info)
        except Exception as e:
            self.fail(f"错误日志记录失败: {e}")

    def test_detector_status(self):
        """测试检测器状态获取"""
        detector = ErrorDetector(self.test_node)

        status = detector.get_detector_status()

        # 验证状态包含所有检测器
        self.assertIn('localization', status)
        self.assertIn('navigation', status)
        self.assertIn('perception', status)
        self.assertIn('system', status)

    def test_detector_reset(self):
        """测试检测器重置"""
        detector = ErrorDetector(self.test_node)

        # 重置定位检测器
        detector.reset_detector('localization')

        # 验证不会抛出异常
        self.assertTrue(True)

        # 重置不存在的检测器
        detector.reset_detector('nonexistent')
        # 应该记录警告但不会抛出异常
        self.assertTrue(True)


class TestLocalizationErrorDetector(unittest.TestCase):
    """定位错误检测器测试"""

    def setUp(self):
        rclpy.init()
        self.test_node = Node("localization_detector_test")

    def tearDown(self):
        self.test_node.destroy_node()
        rclpy.shutdown()

    def test_localization_detector_initialization(self):
        """测试定位检测器初始化"""
        detector = LocalizationErrorDetector(self.test_node)

        # 验证初始状态
        self.assertIsNone(detector.last_pose)
        self.assertIsNone(detector.last_pose_time)
        self.assertEqual(len(detector.pose_history), 0)

    def test_pose_callback(self):
        """测试位姿回调"""
        detector = LocalizationErrorDetector(self.test_node)

        # 创建模拟位姿消息
        from geometry_msgs.msg import PoseWithCovarianceStamped, Pose, Point
        msg = PoseWithCovarianceStamped()
        msg.pose.pose.position = Point(x=1.0, y=2.0, z=0.0)
        msg.pose.covariance = [0.1] * 36  # 低协方差

        # 调用回调
        detector._pose_callback(msg)

        # 验证状态更新
        self.assertIsNotNone(detector.last_pose)
        self.assertIsNotNone(detector.last_pose_time)
        self.assertEqual(len(detector.pose_history), 1)

    def test_covariance_check(self):
        """测试协方差检查"""
        detector = LocalizationErrorDetector(self.test_node)

        # 设置高协方差位姿
        detector.last_pose = {
            'covariance': [1.0] * 36,  # 高协方差
            'confidence': 0.1
        }

        errors = detector._check_covariance()

        # 验证检测到错误
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['error_type'], 'localization_high_covariance')

    def test_localization_lost_check(self):
        """测试定位丢失检查"""
        detector = LocalizationErrorDetector(self.test_node)

        # 设置旧的位姿时间
        detector.last_pose_time = time.time() - 10.0  # 10秒前

        errors = detector._check_localization_lost()

        # 验证检测到定位丢失
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['error_type'], 'localization_lost')

    def test_confidence_calculation(self):
        """测试置信度计算"""
        detector = LocalizationErrorDetector(self.test_node)

        # 测试低协方差（高置信度）
        covariance = [0.1, 0, 0, 0, 0, 0,
                     0, 0.1, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0]

        confidence = detector._calculate_confidence(covariance)
        self.assertGreater(confidence, 0.8)  # 应该高置信度

        # 测试高协方差（低置信度）
        covariance = [1.0, 0, 0, 0, 0, 0,
                     0, 1.0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0]

        confidence = detector._calculate_confidence(covariance)
        self.assertLess(confidence, 0.5)  # 应该低置信度


class TestNavigationErrorDetector(unittest.TestCase):
    """导航错误检测器测试"""

    def setUp(self):
        rclpy.init()
        self.test_node = Node("navigation_detector_test")

    def tearDown(self):
        self.test_node.destroy_node()
        rclpy.shutdown()

    def test_navigation_detector_initialization(self):
        """测试导航检测器初始化"""
        detector = NavigationErrorDetector(self.test_node)

        # 验证初始状态
        self.assertIsNone(detector.last_odom_time)
        self.assertIsNone(detector.last_position)
        self.assertIsNone(detector.last_movement_time)
        self.assertFalse(detector.is_planning)

    def test_robot_stuck_detection(self):
        """测试机器人卡住检测"""
        detector = NavigationErrorDetector(self.test_node)

        # 设置机器人长时间未移动
        from geometry_msgs.msg import Point
        detector.last_position = Point(x=1.0, y=2.0, z=0.0)
        detector.last_movement_time = time.time() - 40.0  # 40秒前
        detector.last_odom_time = time.time()

        errors = detector._check_robot_stuck()

        # 验证检测到卡住
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['error_type'], 'navigation_stuck')

    def test_planning_failure_detection(self):
        """测试路径规划失败检测"""
        detector = NavigationErrorDetector(self.test_node)

        # 设置规划超时
        detector.is_planning = True
        detector.planning_start_time = time.time() - 15.0  # 15秒前开始

        errors = detector._check_planning_failure()

        # 验证检测到规划失败
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['error_type'], 'path_planning_failed')


class TestPerceptionErrorDetector(unittest.TestCase):
    """感知错误检测器测试"""

    def setUp(self):
        rclpy.init()
        self.test_node = Node("perception_detector_test")

    def tearDown(self):
        self.test_node.destroy_node()
        rclpy.shutdown()

    def test_perception_detector_initialization(self):
        """测试感知检测器初始化"""
        detector = PerceptionErrorDetector(self.test_node)

        # 验证初始状态
        self.assertIsNone(detector.last_rfid_time)
        self.assertIsNone(detector.last_laser_time)
        self.assertIsNone(detector.last_imu_time)
        self.assertEqual(len(detector.rfid_detection_history), 0)

    def test_rfid_timeout_detection(self):
        """测试RFID超时检测"""
        detector = PerceptionErrorDetector(self.test_node)

        # 设置RFID超时
        detector.last_rfid_time = time.time() - 10.0  # 10秒前

        errors = detector._check_rfid_timeout()

        # 验证检测到RFID超时
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['error_type'], 'rfid_detection_failed')

    def test_rfid_confidence_calculation(self):
        """测试RFID置信度计算"""
        detector = PerceptionErrorDetector(self.test_node)

        # 测试有效RFID数据
        confidence = detector._calculate_rfid_confidence("VALID_RFID_TAG_123456")
        self.assertGreater(confidence, 0.8)

        # 测试无效RFID数据
        confidence = detector._calculate_rfid_confidence("no_detection")
        self.assertEqual(confidence, 0.0)

        # 测试短RFID数据
        confidence = detector._calculate_rfid_confidence("123")
        self.assertLess(confidence, 0.5)


class TestSystemHealthDetector(unittest.TestCase):
    """系统健康检测器测试"""

    def setUp(self):
        rclpy.init()
        self.test_node = Node("system_detector_test")

    def tearDown(self):
        self.test_node.destroy_node()
        rclpy.shutdown()

    def test_system_detector_initialization(self):
        """测试系统检测器初始化"""
        detector = SystemHealthDetector(self.test_node)

        # 验证初始状态
        self.assertEqual(len(detector.node_last_seen), 0)
        self.assertEqual(len(detector.parameter_events), 0)

    @patch('psutil.Process')
    def test_memory_usage_check(self, mock_process):
        """测试内存使用检查"""
        # 模拟高内存使用
        mock_process.return_value.memory_percent.return_value = 95.0

        detector = SystemHealthDetector(self.test_node)
        errors = detector._check_memory_usage()

        # 验证检测到内存使用过高
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['error_type'], 'memory_exhausted')

    @patch('psutil.Process')
    def test_cpu_usage_check(self, mock_process):
        """测试CPU使用检查"""
        # 模拟高CPU使用
        mock_process.return_value.cpu_percent.return_value = 90.0

        detector = SystemHealthDetector(self.test_node)
        errors = detector._check_cpu_usage()

        # 验证检测到CPU使用过高
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['error_type'], 'cpu_overload')

    def test_node_health_check(self):
        """测试节点健康检查"""
        detector = SystemHealthDetector(self.test_node)

        # 注册一个超时的节点
        detector.node_last_seen['test_node'] = time.time() - 20.0  # 20秒前

        errors = detector._check_node_health()

        # 验证检测到节点通信超时
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['error_type'], 'communication_timeout')


if __name__ == '__main__':
    unittest.main()