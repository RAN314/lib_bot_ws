#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误检测机制集成测试
验证错误检测与L1/L2恢复的集成
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
from libbot_tasks.recovery_behaviors import L1RecoveryBehaviors
from libbot_tasks.l2_recovery_behaviors import L2RecoveryBehaviors


class TestErrorDetectionIntegration(unittest.TestCase):
    """错误检测与恢复集成测试"""

    def setUp(self):
        """测试设置"""
        rclpy.init()
        self.test_node = Node("error_integration_test")

    def tearDown(self):
        """测试清理"""
        self.test_node.destroy_node()
        rclpy.shutdown()

    def test_error_to_l1_recovery_integration(self):
        """测试错误检测触发L1恢复"""
        # 创建错误检测器和L1恢复
        error_detector = ErrorDetector(self.test_node)
        l1_recovery = L1RecoveryBehaviors(self.test_node)

        # 模拟L1恢复方法
        l1_recovery.retry_rfid_scan = Mock(return_value=True)
        l1_recovery.relocalize_robot = Mock(return_value=True)
        l1_recovery.redefine_target = Mock(return_value={'book_id': 'alt_book'})

        # 存储触发的恢复
        triggered_recoveries = []

        def error_callback(error_info):
            """错误回调，触发相应的恢复"""
            if error_info.get('recovery_level') == 'L1':
                triggered_recoveries.append(error_info)

                # 根据错误类型触发相应的L1恢复
                if error_info['error_type'] == 'rfid_detection_failed':
                    l1_recovery.retry_rfid_scan('test_book', {'x': 1.0, 'y': 2.0})
                elif error_info['error_type'] == 'localization_lost':
                    l1_recovery.relocalize_robot()
                elif error_info['error_type'] == 'goal_unreachable':
                    l1_recovery.redefine_target({'book_id': 'test_book'})

        # 注册错误回调
        error_detector.register_error_callback(error_callback)

        # 模拟检测到RFID错误
        error_detector._handle_error('perception', {
            'error_type': 'rfid_detection_failed',
            'message': 'RFID检测失败'
        })

        # 验证L1恢复被触发
        self.assertEqual(len(triggered_recoveries), 1)
        self.assertEqual(triggered_recoveries[0]['error_type'], 'rfid_detection_failed')
        l1_recovery.retry_rfid_scan.assert_called_once()

    def test_error_to_l2_recovery_integration(self):
        """测试错误检测触发L2恢复"""
        # 创建错误检测器和L2恢复
        error_detector = ErrorDetector(self.test_node)
        l2_recovery = L2RecoveryBehaviors(self.test_node)

        # 模拟L2恢复方法
        l2_recovery.clear_costmaps_and_replan = Mock(return_value=True)
        l2_recovery.reset_task_state = Mock(return_value=True)
        l2_recovery.restart_system_components = Mock(return_value=True)

        # 存储触发的恢复
        triggered_recoveries = []

        def error_callback(error_info):
            """错误回调，触发相应的恢复"""
            if error_info.get('recovery_level') == 'L2':
                triggered_recoveries.append(error_info)

                # 根据错误类型触发相应的L2恢复
                if error_info['error_type'] == 'navigation_stuck':
                    l2_recovery.clear_costmaps_and_replan({'x': 5.0, 'y': 3.0})
                elif error_info['error_type'] == 'task_corrupted':
                    l2_recovery.reset_task_state({'task_id': 'test_task'})
                elif error_info['error_type'] == 'sensor_timeout':
                    l2_recovery.restart_system_components(['rfid_processor'])

        # 注册错误回调
        error_detector.register_error_callback(error_callback)

        # 模拟检测到导航错误
        error_detector._handle_error('navigation', {
            'error_type': 'navigation_stuck',
            'message': '机器人卡住'
        })

        # 验证L2恢复被触发
        self.assertEqual(len(triggered_recoveries), 1)
        self.assertEqual(triggered_recoveries[0]['error_type'], 'navigation_stuck')
        l2_recovery.clear_costmaps_and_replan.assert_called_once()

    def test_error_to_l3_escalation(self):
        """测试错误升级到L3恢复"""
        # 创建错误检测器
        error_detector = ErrorDetector(self.test_node)

        # 存储升级事件
        escalated_errors = []

        def error_callback(error_info):
            """错误回调，处理L3升级"""
            if error_info.get('recovery_level') == 'L3':
                escalated_errors.append(error_info)

        # 注册错误回调
        error_detector.register_error_callback(error_callback)

        # 模拟检测到严重错误（应该升级到L3）
        error_detector._handle_error('localization', {
            'error_type': 'localization_lost',
            'message': '定位完全丢失'
        })

        # 模拟检测到系统级错误
        error_detector._handle_error('system', {
            'error_type': 'node_crash',
            'message': '关键节点崩溃'
        })

        # 验证L3升级
        self.assertEqual(len(escalated_errors), 2)
        self.assertEqual(escalated_errors[0]['recovery_level'], 'L3')
        self.assertEqual(escalated_errors[1]['recovery_level'], 'L3')

    def test_error_classification_accuracy(self):
        """测试错误分类准确性"""
        error_detector = ErrorDetector(self.test_node)

        # 测试用例：错误类型 -> 期望的严重程度和恢复级别
        test_cases = [
            ('localization_lost', 'Critical', 'L3'),
            ('localization_drift', 'Error', 'L2'),
            ('navigation_stuck', 'Error', 'L2'),
            ('rfid_detection_failed', 'Warning', 'L1'),
            ('node_crash', 'Fatal', 'L3'),
            ('memory_exhausted', 'Critical', 'L3'),
            ('unknown_error', 'Warning', 'L1')  # 默认分类
        ]

        for error_type, expected_severity, expected_recovery in test_cases:
            with self.subTest(error_type=error_type):
                error_info = {
                    'error_type': error_type,
                    'message': f'测试错误: {error_type}'
                }

                classified_error = error_detector._classify_error(error_info)

                self.assertEqual(classified_error['severity'], expected_severity,
                               f"{error_type} 严重程度分类错误")
                self.assertEqual(classified_error['recovery_level'], expected_recovery,
                               f"{error_type} 恢复级别分类错误")

    def test_multiple_error_handling(self):
        """测试多错误同时处理"""
        error_detector = ErrorDetector(self.test_node)

        # 存储所有处理的错误
        processed_errors = []

        def error_callback(error_info):
            processed_errors.append(error_info)

        error_detector.register_error_callback(error_callback)

        # 同时触发多个不同类型的错误
        errors_to_test = [
            ('perception', {'error_type': 'rfid_detection_failed', 'message': 'RFID失败'}),
            ('localization', {'error_type': 'localization_drift', 'message': '定位漂移'}),
            ('navigation', {'error_type': 'navigation_stuck', 'message': '机器人卡住'}),
            ('system', {'error_type': 'cpu_overload', 'message': 'CPU过载'})
        ]

        for detector_type, error_info in errors_to_test:
            error_detector._handle_error(detector_type, error_info)

        # 验证所有错误都被处理
        self.assertEqual(len(processed_errors), 4)

        # 验证错误分类正确
        severities = [error['severity'] for error in processed_errors]
        self.assertIn('Warning', severities)
        self.assertIn('Error', severities)

    def test_error_callback_exception_handling(self):
        """测试错误回调异常处理"""
        error_detector = ErrorDetector(self.test_node)

        # 创建会抛出异常的回调
        def faulty_callback(error_info):
            raise Exception("回调函数错误")

        def good_callback(error_info):
            pass  # 正常回调

        # 注册两个回调，其中一个会失败
        error_detector.register_error_callback(faulty_callback)
        error_detector.register_error_callback(good_callback)

        # 模拟错误处理
        try:
            error_detector._handle_error('test', {
                'error_type': 'test_error',
                'message': '测试错误'
            })
            # 不应该抛出异常
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"错误处理不应该抛出异常: {e}")

    def test_detector_coordination(self):
        """测试检测器协调工作"""
        error_detector = ErrorDetector(self.test_node)

        # 启动检测
        error_detector.start_detection()

        # 等待一段时间让检测器运行
        time.sleep(0.5)

        # 获取检测器状态
        status = error_detector.get_detector_status()

        # 验证所有检测器都正常工作
        self.assertIn('localization', status)
        self.assertIn('navigation', status)
        self.assertIn('perception', status)
        self.assertIn('system', status)

        # 停止检测
        error_detector.stop_detection()

        # 验证检测已停止
        self.assertFalse(error_detector.is_running)


if __name__ == '__main__':
    unittest.main()