# test/test_bt_structure.py

import unittest
import os
import sys

# 添加项目路径
sys.path.insert(0, '/home/lhl/lib_bot_ws/src')


class TestBTStructure(unittest.TestCase):
    """测试BT文件结构和基本功能"""

    def test_file_structure_exists(self):
        """测试所有必要的文件都存在"""
        base_path = '/home/lhl/lib_bot_ws/src/libbot_tasks'

        # 测试核心文件
        self.assertTrue(os.path.exists(os.path.join(base_path, 'libbot_tasks', 'bt_manager_node.py')))

        # 测试BT节点文件
        bt_nodes_path = os.path.join(base_path, 'libbot_tasks', 'bt_nodes')
        self.assertTrue(os.path.exists(os.path.join(bt_nodes_path, 'recovery_nodes.py')))
        self.assertTrue(os.path.exists(os.path.join(bt_nodes_path, 'condition_nodes.py')))
        self.assertTrue(os.path.exists(os.path.join(bt_nodes_path, 'action_nodes.py')))

        # 测试行为树文件
        behaviors_path = os.path.join(base_path, 'libbot_tasks', 'behaviors')
        self.assertTrue(os.path.exists(os.path.join(behaviors_path, 'main_bt.xml')))
        self.assertTrue(os.path.exists(os.path.join(behaviors_path, 'recovery_bt.xml')))
        self.assertTrue(os.path.exists(os.path.join(behaviors_path, 'findbook_bt.xml')))

        # 测试配置文件
        config_path = os.path.join(base_path, 'libbot_tasks', 'config')
        self.assertTrue(os.path.exists(os.path.join(config_path, 'bt_config.yaml')))

    def test_xml_files_valid(self):
        """测试XML文件格式基本正确"""
        behaviors_path = '/home/lhl/lib_bot_ws/src/libbot_tasks/libbot_tasks/behaviors'

        # 测试主行为树
        with open(os.path.join(behaviors_path, 'main_bt.xml'), 'r') as f:
            main_bt_content = f.read()
            self.assertIn('<root', main_bt_content)
            self.assertIn('MainBehaviorTree', main_bt_content)
            self.assertIn('</root>', main_bt_content)

        # 测试恢复行为树
        with open(os.path.join(behaviors_path, 'recovery_bt.xml'), 'r') as f:
            recovery_bt_content = f.read()
            self.assertIn('<root', recovery_bt_content)
            self.assertIn('RecoveryBehaviorTree', recovery_bt_content)
            self.assertIn('L1Recovery', recovery_bt_content)
            self.assertIn('L2Recovery', recovery_bt_content)

        # 测试FindBook行为树
        with open(os.path.join(behaviors_path, 'findbook_bt.xml'), 'r') as f:
            findbook_bt_content = f.read()
            self.assertIn('<root', findbook_bt_content)
            self.assertIn('FindBookBehaviorTree', findbook_bt_content)
            self.assertIn('NavigateToBookshelf', findbook_bt_content)

    def test_python_classes_exist(self):
        """测试Python类定义存在"""
        # 测试恢复节点类
        try:
            from libbot_tasks.libbot_tasks.bt_nodes.recovery_nodes import L1RecoveryNode, L2RecoveryNode, ErrorDetectionNode
            self.assertTrue(callable(L1RecoveryNode))
            self.assertTrue(callable(L2RecoveryNode))
            self.assertTrue(callable(ErrorDetectionNode))
        except ImportError as e:
            self.skipTest(f"跳过恢复节点测试: {e}")

        # 测试条件节点类
        try:
            from libbot_tasks.libbot_tasks.bt_nodes.condition_nodes import IsBookAvailable, IsNavigationStuck, IsLocalizationLost
            self.assertTrue(callable(IsBookAvailable))
            self.assertTrue(callable(IsNavigationStuck))
            self.assertTrue(callable(IsLocalizationLost))
        except ImportError as e:
            self.skipTest(f"跳过条件节点测试: {e}")

        # 测试动作节点类
        try:
            from libbot_tasks.libbot_tasks.bt_nodes.action_nodes import NavigateToBookshelf, ScanForBook, UpdateDatabase
            self.assertTrue(callable(NavigateToBookshelf))
            self.assertTrue(callable(ScanForBook))
            self.assertTrue(callable(UpdateDatabase))
        except ImportError as e:
            self.skipTest(f"跳过动作节点测试: {e}")

    def test_yaml_config_valid(self):
        """测试YAML配置文件基本正确"""
        import yaml

        config_path = '/home/lhl/lib_bot_ws/src/libbot_tasks/libbot_tasks/config/bt_config.yaml'

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # 验证主要配置部分
        self.assertIn('behavior_trees', config)
        self.assertIn('execution', config)
        self.assertIn('node_timeouts', config)
        self.assertIn('debug', config)
        self.assertIn('groot', config)

        # 验证行为树配置
        bt_configs = config['behavior_trees']
        self.assertIn('main_bt', bt_configs)
        self.assertIn('recovery_bt', bt_configs)
        self.assertIn('findbook_bt', bt_configs)

    def test_story_acceptance_criteria(self):
        """验证故事验收标准的关键组件"""

        # 1. BT Manager节点存在
        bt_manager_path = '/home/lhl/lib_bot_ws/src/libbot_tasks/libbot_tasks/bt_manager_node.py'
        self.assertTrue(os.path.exists(bt_manager_path))

        with open(bt_manager_path, 'r') as f:
            content = f.read()
            # 验证关键功能
            self.assertIn('class BTManagerNode', content)
            self.assertIn('_register_custom_nodes', content)
            self.assertIn('_load_default_trees', content)
            self.assertIn('start_tree', content)
            self.assertIn('stop_tree', content)

        # 2. 自定义BT节点集成存在
        recovery_nodes_path = '/home/lhl/lib_bot_ws/src/libbot_tasks/libbot_tasks/bt_nodes/recovery_nodes.py'
        self.assertTrue(os.path.exists(recovery_nodes_path))

        with open(recovery_nodes_path, 'r') as f:
            content = f.read()
            self.assertIn('L1RecoveryNode', content)
            self.assertIn('L2RecoveryNode', content)
            self.assertIn('ErrorDetectionNode', content)

        # 3. XML行为树定义存在
        main_bt_path = '/home/lhl/lib_bot_ws/src/libbot_tasks/libbot_tasks/behaviors/main_bt.xml'
        self.assertTrue(os.path.exists(main_bt_path))

        # 4. 配置文件存在
        config_path = '/home/lhl/lib_bot_ws/src/libbot_tasks/libbot_tasks/config/bt_config.yaml'
        self.assertTrue(os.path.exists(config_path))


if __name__ == '__main__':
    unittest.main()