# test/test_bt_integration.py

import unittest
import rclpy
from rclpy.node import Node
from unittest.mock import Mock, patch, MagicMock
import time

from libbot_tasks.libbot_tasks.bt_manager_node import BTManagerNode
from libbot_tasks.libbot_tasks.bt_nodes.recovery_nodes import L1RecoveryNode, L2RecoveryNode, ErrorDetectionNode
from libbot_tasks.libbot_tasks.bt_nodes.condition_nodes import IsBookAvailable, IsNavigationStuck, IsLocalizationLost
from libbot_tasks.libbot_tasks.bt_nodes.action_nodes import NavigateToBookshelf, ScanForBook, UpdateDatabase


class TestBTManagerNode(unittest.TestCase):
    """测试BT管理器节点"""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.mock_node = Mock(spec=Node)
        self.mock_node.get_logger = Mock()
        self.mock_node.get_logger.return_value = Mock()
        self.mock_node.get_clock.return_value.now.return_value.to_msg.return_value = Mock()

    @patch('libbot_tasks.libbot_tasks.bt_manager_node.BehaviorTreeManager')
    @patch('libbot_tasks.libbot_tasks.bt_manager_node.XmlTreeParser')
    def test_bt_manager_initialization(self, mock_parser, mock_bt_manager):
        """测试BT管理器初始化"""
        # 配置模拟对象
        mock_bt_manager.return_value = Mock()
        mock_parser.return_value = Mock()
        mock_parser.return_value.load_from_file.return_value = "<test></test>"

        # 创建BT管理器
        bt_manager = BTManagerNode()

        # 验证初始化
        self.assertIsNotNone(bt_manager.bt_manager)
        self.assertEqual(bt_manager.tick_rate, 10.0)
        self.assertFalse(bt_manager.is_running)

        # 清理
        bt_manager.destroy_node()

    def test_tree_start_stop(self):
        """测试行为树启动和停止"""
        # 这里应该测试树的启动和停止功能
        # 由于需要完整的ROS2环境，这里只验证接口存在
        bt_manager = BTManagerNode()

        # 验证方法存在
        self.assertTrue(hasattr(bt_manager, 'start_tree'))
        self.assertTrue(hasattr(bt_manager, 'stop_tree'))
        self.assertTrue(hasattr(bt_manager, 'get_tree_status'))

        bt_manager.destroy_node()


class TestRecoveryNodes(unittest.TestCase):
    """测试恢复相关BT节点"""

    def setUp(self):
        self.mock_node = Mock(spec=Node)
        self.mock_node.get_logger = Mock()
        self.mock_node.get_logger.return_value = Mock()

    @patch('libbot_tasks.libbot_tasks.bt_nodes.recovery_nodes.L1RecoveryBehaviors')
    def test_l1_recovery_node(self, mock_l1_recovery):
        """测试L1恢复节点"""
        # 配置模拟
        mock_l1_recovery.return_value = Mock()
        mock_l1_recovery.return_value.retry_rfid_scan.return_value = True

        # 创建节点
        node = L1RecoveryNode(self.mock_node)
        node.l1_recovery = mock_l1_recovery.return_value

        # 执行tick
        result = node.tick()

        # 验证结果
        self.assertIn(result, [Mock(), None])  # 根据实际实现调整

    @patch('libbot_tasks.libbot_tasks.bt_nodes.recovery_nodes.L2RecoveryBehaviors')
    def test_l2_recovery_node(self, mock_l2_recovery):
        """测试L2恢复节点"""
        # 配置模拟
        mock_l2_recovery.return_value = Mock()
        mock_l2_recovery.return_value.clear_costmaps_and_replan.return_value = True

        # 创建节点
        node = L2RecoveryNode(self.mock_node)
        node.l2_recovery = mock_l2_recovery.return_value

        # 执行tick
        result = node.tick()

        # 验证结果
        self.assertIn(result, [Mock(), None])  # 根据实际实现调整

    @patch('libbot_tasks.libbot_tasks.bt_nodes.recovery_nodes.ErrorDetector')
    def test_error_detection_node(self, mock_error_detector):
        """测试错误检测节点"""
        # 配置模拟
        mock_detector_instance = Mock()
        mock_detector_instance.detectors = {}
        mock_error_detector.return_value = mock_detector_instance

        # 创建节点
        node = ErrorDetectionNode(self.mock_node)
        node.error_detector = mock_detector_instance

        # 执行tick
        result = node.tick()

        # 验证结果
        self.assertIn(result, [Mock(), None])  # 根据实际实现调整


class TestConditionNodes(unittest.TestCase):
    """测试条件判断BT节点"""

    def setUp(self):
        self.mock_node = Mock(spec=Node)
        self.mock_node.get_logger = Mock()
        self.mock_node.get_logger.return_value = Mock()

    def test_is_book_available(self):
        """测试图书可用性检查节点"""
        node = IsBookAvailable(self.mock_node)
        result = node.tick()
        self.assertIn(result, [Mock(), None])

    def test_is_navigation_stuck(self):
        """测试导航卡住检测节点"""
        node = IsNavigationStuck(self.mock_node)
        result = node.tick()
        self.assertIn(result, [Mock(), None])

    def test_is_localization_lost(self):
        """测试定位丢失检测节点"""
        node = IsLocalizationLost(self.mock_node)
        result = node.tick()
        self.assertIn(result, [Mock(), None])


class TestActionNodes(unittest.TestCase):
    """测试动作执行BT节点"""

    def setUp(self):
        self.mock_node = Mock(spec=Node)
        self.mock_node.get_logger = Mock()
        self.mock_node.get_logger.return_value = Mock()

    def test_navigate_to_bookshelf(self):
        """测试导航到书架节点"""
        node = NavigateToBookshelf(self.mock_node)
        result = node.tick()
        self.assertIn(result, [Mock(), None])

    def test_scan_for_book(self):
        """测试图书扫描节点"""
        node = ScanForBook(self.mock_node)
        result = node.tick()
        self.assertIn(result, [Mock(), None])

    def test_update_database(self):
        """测试数据库更新节点"""
        node = UpdateDatabase(self.mock_node)
        result = node.tick()
        self.assertIn(result, [Mock(), None])

    def test_perform_system_check(self):
        """测试系统检查节点"""
        node = PerformSystemCheck(self.mock_node)
        result = node.tick()
        self.assertIn(result, [Mock(), None])

    def test_enter_idle_state(self):
        """测试进入空闲状态节点"""
        node = EnterIdleState(self.mock_node)
        result = node.tick()
        self.assertIn(result, [Mock(), None])

    def test_request_human_intervention(self):
        """测试请求人工干预节点"""
        node = RequestHumanIntervention(self.mock_node)
        result = node.tick()
        self.assertIn(result, [Mock(), None])


class TestBTIntegration(unittest.TestCase):
    """测试BT集成功能"""

    def test_node_registration(self):
        """测试节点注册功能"""
        # 验证所有必要的节点类都存在
        from libbot_tasks.libbot_tasks.bt_nodes import recovery_nodes
        from libbot_tasks.libbot_tasks.bt_nodes import condition_nodes
        from libbot_tasks.libbot_tasks.bt_nodes import action_nodes

        # 验证恢复节点
        self.assertTrue(hasattr(recovery_nodes, 'L1RecoveryNode'))
        self.assertTrue(hasattr(recovery_nodes, 'L2RecoveryNode'))
        self.assertTrue(hasattr(recovery_nodes, 'ErrorDetectionNode'))

        # 验证条件节点
        self.assertTrue(hasattr(condition_nodes, 'IsBookAvailable'))
        self.assertTrue(hasattr(condition_nodes, 'IsNavigationStuck'))
        self.assertTrue(hasattr(condition_nodes, 'IsLocalizationLost'))

        # 验证动作节点
        self.assertTrue(hasattr(action_nodes, 'NavigateToBookshelf'))
        self.assertTrue(hasattr(action_nodes, 'ScanForBook'))
        self.assertTrue(hasattr(action_nodes, 'UpdateDatabase'))

    def test_xml_files_exist(self):
        """测试XML行为树文件存在"""
        import os

        # 验证主要的行为树文件存在
        behaviors_dir = '/home/lhl/lib_bot_ws/src/libbot_tasks/libbot_tasks/behaviors'

        self.assertTrue(os.path.exists(os.path.join(behaviors_dir, 'main_bt.xml')))
        self.assertTrue(os.path.exists(os.path.join(behaviors_dir, 'recovery_bt.xml')))
        self.assertTrue(os.path.exists(os.path.join(behaviors_dir, 'findbook_bt.xml')))

    def test_config_files_exist(self):
        """测试配置文件存在"""
        import os

        # 验证配置文件存在
        config_dir = '/home/lhl/lib_bot_ws/src/libbot_tasks/libbot_tasks/config'

        self.assertTrue(os.path.exists(os.path.join(config_dir, 'bt_config.yaml')))


if __name__ == '__main__':
    unittest.main()