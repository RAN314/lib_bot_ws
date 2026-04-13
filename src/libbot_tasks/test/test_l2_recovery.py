#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L2恢复行为单元测试
测试L2恢复功能的各个方面
"""

import unittest
import time
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# 添加模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from libbot_tasks.l2_recovery_behaviors import L2RecoveryBehaviors


class TestL2RecoveryBehaviors(unittest.TestCase):
    """L2恢复行为测试类"""

    def setUp(self):
        """测试设置"""
        # 创建模拟ROS2节点
        self.mock_node = Mock()
        self.mock_node.get_logger = Mock()
        self.mock_node.get_logger.return_value = Mock()
        self.mock_node.declare_parameter = Mock()
        self.mock_node.create_client = Mock()
        self.mock_node.get_clock = Mock()
        self.mock_node.get_clock.return_value.now.return_value.to_msg.return_value = Mock()

        # 模拟参数声明
        self.mock_node.declare_parameter.side_effect = self._mock_declare_parameter

        # 模拟服务客户端
        self.mock_global_costmap_client = Mock()
        self.mock_local_costmap_client = Mock()
        self.mock_node.create_client.side_effect = [
            self.mock_global_costmap_client,
            self.mock_local_costmap_client
        ]

        # 创建L2恢复实例
        self.l2_recovery = L2RecoveryBehaviors(self.mock_node)

    def _mock_declare_parameter(self, name, default_value):
        """模拟参数声明"""
        mock_param = Mock()
        mock_param.value = default_value
        return mock_param

    def test_initialization(self):
        """测试L2恢复初始化"""
        self.assertIsNotNone(self.l2_recovery)
        self.assertEqual(self.l2_recovery.node, self.mock_node)
        self.assertEqual(self.l2_recovery.recovery_timeout, 40.0)

    def test_parameter_loading(self):
        """测试参数加载"""
        # 验证参数是否正确设置
        self.assertEqual(self.l2_recovery.max_consecutive_failures, 2)
        self.assertEqual(self.l2_recovery.global_costmap_timeout, 15.0)
        self.assertEqual(self.l2_recovery.local_costmap_timeout, 10.0)
        self.assertEqual(self.l2_recovery.replan_timeout, 15.0)

    def test_clear_costmaps_and_replan_success(self):
        """测试代价地图清除和重新规划成功情况"""
        # 模拟服务调用成功
        mock_future = Mock()
        mock_future.done.return_value = True
        mock_future.result.return_value = Mock()

        self.mock_global_costmap_client.wait_for_service.return_value = True
        self.mock_global_costmap_client.call_async.return_value = mock_future
        self.mock_local_costmap_client.wait_for_service.return_value = True
        self.mock_local_costmap_client.call_async.return_value = mock_future

        # 模拟导航Action客户端
        with patch.object(self.l2_recovery, '_replan_path', return_value=True):
            result = self.l2_recovery.clear_costmaps_and_replan({'x': 5.0, 'y': 3.0})

        self.assertTrue(result)

    def test_clear_costmaps_and_replan_failure(self):
        """测试代价地图清除失败情况"""
        # 模拟服务不可用
        self.mock_global_costmap_client.wait_for_service.return_value = False

        result = self.l2_recovery.clear_costmaps_and_replan({'x': 5.0, 'y': 3.0})
        self.assertFalse(result)

    def test_reset_task_state_success(self):
        """测试任务状态重置成功情况"""
        task_info = {
            'task_id': 'test_task_001',
            'progress': 50,
            'books_detected': ['book_001'],
            'navigation_attempts': 2,
            'scan_attempts': 3
        }

        # 模拟所有私有方法成功
        with patch.multiple(
            self.l2_recovery,
            _save_task_context=Mock(return_value=task_info),
            _reset_task_execution=Mock(return_value=True),
            _restore_task_context=Mock(return_value=True),
            _restart_task=Mock(return_value=True)
        ):
            result = self.l2_recovery.reset_task_state(task_info)

        self.assertTrue(result)

    def test_reset_task_state_failure(self):
        """测试任务状态重置失败情况"""
        task_info = {'task_id': 'test_task_001'}

        # 模拟上下文保存失败
        with patch.object(self.l2_recovery, '_save_task_context', return_value=None):
            result = self.l2_recovery.reset_task_state(task_info)

        self.assertFalse(result)

    def test_restart_system_components_all_success(self):
        """测试系统组件重启全部成功"""
        components = ['rfid_processor', 'perception_manager']

        # 模拟所有组件重启成功
        with patch.object(self.l2_recovery, '_restart_single_component', return_value=True):
            result = self.l2_recovery.restart_system_components(components)

        self.assertTrue(result)

    def test_restart_system_components_partial_success(self):
        """测试系统组件重启部分成功"""
        components = ['rfid_processor', 'perception_manager', 'sensor_fusion']

        # 模拟部分成功
        def mock_restart(component):
            return component != 'sensor_fusion'  # 最后一个失败

        with patch.object(self.l2_recovery, '_restart_single_component', side_effect=mock_restart):
            result = self.l2_recovery.restart_system_components(components)

        self.assertTrue(result)  # 部分成功也算成功

    def test_restart_system_components_all_failure(self):
        """测试系统组件重启全部失败"""
        components = ['rfid_processor', 'perception_manager']

        # 模拟所有组件重启失败
        with patch.object(self.l2_recovery, '_restart_single_component', return_value=False):
            result = self.l2_recovery.restart_system_components(components)

        self.assertFalse(result)

    def test_return_to_home_and_reset_success(self):
        """测试返回Home并重置成功"""
        # 模拟所有步骤成功
        with patch.multiple(
            self.l2_recovery,
            _navigate_to_home=Mock(return_value=True),
            _reinitialize_system=Mock(return_value=True),
            _update_system_status=Mock(return_value=True)
        ):
            result = self.l2_recovery.return_to_home_and_reset()

        self.assertTrue(result)

    def test_return_to_home_and_reset_navigation_failure(self):
        """测试返回Home导航失败"""
        # 模拟导航失败
        with patch.object(self.l2_recovery, '_navigate_to_home', return_value=False):
            result = self.l2_recovery.return_to_home_and_reset()

        self.assertFalse(result)

    def test_save_task_context(self):
        """测试任务上下文保存"""
        task_info = {
            'task_id': 'test_task_001',
            'start_time': time.time(),
            'progress': 75,
            'books_detected': ['book_001', 'book_002'],
            'navigation_attempts': 3,
            'scan_attempts': 5
        }

        context = self.l2_recovery._save_task_context(task_info)

        self.assertIsNotNone(context)
        self.assertEqual(context['task_id'], 'test_task_001')
        self.assertEqual(context['current_progress'], 75)
        self.assertEqual(len(context['books_detected']), 2)
        self.assertIn('saved_at', context)

    def test_restart_single_component_success(self):
        """测试单个组件重启成功"""
        # 模拟随机成功（90%概率）
        with patch('random.random', return_value=0.8):  # 小于0.9，应该成功
            result = self.l2_recovery._restart_single_component('rfid_processor')

        self.assertTrue(result)

    def test_restart_single_component_failure(self):
        """测试单个组件重启失败"""
        # 模拟随机失败（10%概率）
        with patch('random.random', return_value=0.95):  # 大于0.9，应该失败
            result = self.l2_recovery._restart_single_component('rfid_processor')

        self.assertFalse(result)

    def test_service_timeout_handling(self):
        """测试服务超时处理"""
        # 模拟服务调用超时
        mock_future = Mock()
        mock_future.done.return_value = False  # 永远不会完成

        self.mock_global_costmap_client.wait_for_service.return_value = True
        self.mock_global_costmap_client.call_async.return_value = mock_future

        result = self.l2_recovery._clear_global_costmap()

        self.assertFalse(result)  # 应该因为超时而失败

    def test_wait_for_service_result_timeout(self):
        """测试服务结果等待超时"""
        mock_future = Mock()
        mock_future.done.return_value = False
        mock_future.result.return_value = None

        result = self.l2_recovery._wait_for_service_result(mock_future, 0.1)  # 短超时

        self.assertFalse(result)

    def test_wait_for_service_result_success(self):
        """测试服务结果等待成功"""
        mock_future = Mock()
        mock_future.done.return_value = True
        mock_future.result.return_value = Mock()  # 非None结果

        result = self.l2_recovery._wait_for_service_result(mock_future, 1.0)

        self.assertTrue(result)

    def test_set_l1_recovery(self):
        """测试设置L1恢复实例"""
        mock_l1_recovery = Mock()

        self.l2_recovery.set_l1_recovery(mock_l1_recovery)

        self.assertEqual(self.l2_recovery.l1_recovery, mock_l1_recovery)

    def test_parameter_validation(self):
        """测试参数验证"""
        # 验证关键参数在合理范围内
        self.assertGreaterEqual(self.l2_recovery.max_consecutive_failures, 1)
        self.assertLessEqual(self.l2_recovery.max_consecutive_failures, 5)
        self.assertGreaterEqual(self.l2_recovery.global_costmap_timeout, 5.0)
        self.assertLessEqual(self.l2_recovery.global_costmap_timeout, 60.0)

    def test_error_handling_in_clear_costmaps(self):
        """测试代价地图清除中的错误处理"""
        # 模拟异常情况
        self.mock_global_costmap_client.wait_for_service.side_effect = Exception("Service error")

        result = self.l2_recovery.clear_costmaps_and_replan({'x': 5.0, 'y': 3.0})

        self.assertFalse(result)

    def test_error_handling_in_task_reset(self):
        """测试任务重置中的错误处理"""
        task_info = {'task_id': 'test_task_001'}

        # 模拟异常
        with patch.object(self.l2_recovery, '_save_task_context', side_effect=Exception("Save error")):
            result = self.l2_recovery.reset_task_state(task_info)

        self.assertFalse(result)


class TestL2RecoveryIntegration(unittest.TestCase):
    """L2恢复集成测试"""

    def test_recovery_sequence(self):
        """测试完整的恢复序列"""
        # 创建模拟节点
        mock_node = Mock()
        mock_node.get_logger = Mock()
        mock_node.get_logger.return_value = Mock()
        mock_node.declare_parameter = Mock()

        def mock_declare_param(name, default):
            param = Mock()
            param.value = default
            return param

        mock_node.declare_parameter.side_effect = mock_declare_param
        mock_node.create_client = Mock()
        mock_node.get_clock = Mock()
        mock_node.get_clock.return_value.now.return_value.to_msg.return_value = Mock()

        # 创建L2恢复实例
        l2_recovery = L2RecoveryBehaviors(mock_node)

        # 模拟所有方法成功
        with patch.multiple(
            l2_recovery,
            clear_costmaps_and_replan=Mock(return_value=True),
            reset_task_state=Mock(return_value=True),
            restart_system_components=Mock(return_value=True),
            return_to_home_and_reset=Mock(return_value=True)
        ):
            # 测试完整的恢复序列
            goal_pose = {'x': 5.0, 'y': 3.0}
            task_info = {'task_id': 'test_task'}
            components = ['component1', 'component2']

            # 执行各种恢复操作
            result1 = l2_recovery.clear_costmaps_and_replan(goal_pose)
            result2 = l2_recovery.reset_task_state(task_info)
            result3 = l2_recovery.restart_system_components(components)
            result4 = l2_recovery.return_to_home_and_reset()

            # 验证所有操作都成功
            self.assertTrue(result1)
            self.assertTrue(result2)
            self.assertTrue(result3)
            self.assertTrue(result4)

    def test_recovery_failure_handling(self):
        """测试恢复失败处理"""
        # 创建模拟节点
        mock_node = Mock()
        mock_node.get_logger = Mock()
        mock_node.get_logger.return_value = Mock()
        mock_node.declare_parameter = Mock()

        def mock_declare_param(name, default):
            param = Mock()
            param.value = default
            return param

        mock_node.declare_parameter.side_effect = mock_declare_param
        mock_node.create_client = Mock()
        mock_node.get_clock = Mock()
        mock_node.get_clock.return_value.now.return_value.to_msg.return_value = Mock()

        # 创建L2恢复实例
        l2_recovery = L2RecoveryBehaviors(mock_node)

        # 测试各种失败场景
        with patch.multiple(
            l2_recovery,
            clear_costmaps_and_replan=Mock(return_value=False),
            reset_task_state=Mock(return_value=False),
            restart_system_components=Mock(return_value=False),
            return_to_home_and_reset=Mock(return_value=False)
        ):
            # 验证失败处理
            result1 = l2_recovery.clear_costmaps_and_replan({'x': 5.0, 'y': 3.0})
            result2 = l2_recovery.reset_task_state({'task_id': 'test'})
            result3 = l2_recovery.restart_system_components(['comp1'])
            result4 = l2_recovery.return_to_home_and_reset()

            # 验证所有操作都正确处理了失败
            self.assertFalse(result1)
            self.assertFalse(result2)
            self.assertFalse(result3)
            self.assertFalse(result4)


if __name__ == '__main__':
    # 运行所有测试
    unittest.main(verbosity=2)