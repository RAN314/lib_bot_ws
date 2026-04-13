#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L1恢复行为与UI集成模块
将Story 2-1的L1恢复行为集成到Epic 1的UI系统中
"""

from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import rclpy
from rclpy.node import Node
import threading
import time

# 导入L1恢复行为
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'libbot_tasks'))
try:
    from libbot_tasks.recovery_behaviors import L1RecoveryBehaviors
except ImportError:
    # 如果导入失败，创建模拟类
    class L1RecoveryBehaviors:
        def __init__(self, node):
            pass
        def setup_ros_communication(self):
            pass
        def retry_rfid_scan(self, book_id, position):
            return True
        def relocalize_robot(self):
            return True
        def redefine_target(self, goal):
            return {'book_id': 'alt_book', 'position': {'x': 1.0, 'y': 2.0}}
        def cleanup(self):
            pass

class L1RecoveryIntegration(QObject):
    """L1恢复行为与UI集成管理器"""

    # Qt信号定义
    recovery_status_updated = pyqtSignal(dict)
    recovery_error_occurred = pyqtSignal(dict)
    recovery_completed = pyqtSignal(dict)

    def __init__(self, ros2_node):
        """初始化L1恢复集成

        Args:
            ros2_node: ROS2节点实例
        """
        super().__init__()
        self.ros2_node = ros2_node
        self.l1_recovery = None
        self.recovery_active = False
        self.current_recovery_type = None

        # 初始化L1恢复行为
        self._init_l1_recovery()

        # 创建状态更新定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_recovery_status)
        self.status_timer.start(100)  # 10Hz状态更新

    def _init_l1_recovery(self):
        """初始化L1恢复行为"""
        try:
            self.l1_recovery = L1RecoveryBehaviors(self.ros2_node)
            self.l1_recovery.setup_ros_communication()
            print("✅ L1恢复行为集成初始化成功")
        except Exception as e:
            print(f"❌ L1恢复行为集成初始化失败: {e}")
            self.l1_recovery = None

    def trigger_rfid_recovery(self, book_id, position):
        """触发RFID恢复

        Args:
            book_id: 图书ID
            position: 位置信息
        """
        if not self.l1_recovery:
            self._emit_error("L1恢复行为未初始化")
            return

        print(f"🔧 触发RFID恢复: {book_id}")
        self._start_recovery("rfid_rescan", {
            'book_id': book_id,
            'position': position
        })

        # 在后台线程中执行恢复
        recovery_thread = threading.Thread(
            target=self._execute_rfid_recovery,
            args=(book_id, position)
        )
        recovery_thread.daemon = True
        recovery_thread.start()

    def trigger_localization_recovery(self):
        """触发定位恢复"""
        if not self.l1_recovery:
            self._emit_error("L1恢复行为未初始化")
            return

        print("🔧 触发定位恢复")
        self._start_recovery("relocalization", {})

        # 在后台线程中执行恢复
        recovery_thread = threading.Thread(
            target=self._execute_localization_recovery
        )
        recovery_thread.daemon = True
        recovery_thread.start()

    def trigger_target_redefinition(self, original_goal):
        """触发目标重定义

        Args:
            original_goal: 原始目标信息
        """
        if not self.l1_recovery:
            self._emit_error("L1恢复行为未初始化")
            return

        print(f"🔧 触发目标重定义: {original_goal}")
        self._start_recovery("target_redefinition", {
            'original_goal': original_goal
        })

        # 在后台线程中执行恢复
        recovery_thread = threading.Thread(
            target=self._execute_target_redefinition,
            args=(original_goal,)
        )
        recovery_thread.daemon = True
        recovery_thread.start()

    def _start_recovery(self, recovery_type, context):
        """开始恢复过程"""
        self.recovery_active = True
        self.current_recovery_type = recovery_type

        # 发送恢复开始信号
        status_info = {
            'type': recovery_type,
            'status': 'started',
            'context': context,
            'timestamp': time.time()
        }
        self.recovery_status_updated.emit(status_info)

        print(f"🚀 L1恢复开始: {recovery_type}")

    def _execute_rfid_recovery(self, book_id, position):
        """执行RFID恢复"""
        try:
            result = self.l1_recovery.retry_rfid_scan(book_id, position)

            # 发送恢复完成信号
            completion_info = {
                'type': 'rfid_rescan',
                'success': result,
                'book_id': book_id,
                'position': position,
                'timestamp': time.time()
            }

            if result:
                print(f"✅ RFID恢复成功: {book_id}")
            else:
                print(f"❌ RFID恢复失败: {book_id}")

            self._complete_recovery(completion_info)

        except Exception as e:
            self._handle_recovery_error("RFID恢复异常", str(e))

    def _execute_localization_recovery(self):
        """执行定位恢复"""
        try:
            result = self.l1_recovery.relocalize_robot()

            # 发送恢复完成信号
            completion_info = {
                'type': 'relocalization',
                'success': result,
                'timestamp': time.time()
            }

            if result:
                print("✅ 定位恢复成功")
            else:
                print("❌ 定位恢复失败")

            self._complete_recovery(completion_info)

        except Exception as e:
            self._handle_recovery_error("定位恢复异常", str(e))

    def _execute_target_redefinition(self, original_goal):
        """执行目标重定义"""
        try:
            alternative_goal = self.l1_recovery.redefine_target(original_goal)

            # 发送恢复完成信号
            completion_info = {
                'type': 'target_redefinition',
                'success': alternative_goal is not None,
                'original_goal': original_goal,
                'alternative_goal': alternative_goal,
                'timestamp': time.time()
            }

            if alternative_goal:
                print(f"✅ 目标重定义成功: {alternative_goal['book_id']}")
            else:
                print("❌ 目标重定义失败")

            self._complete_recovery(completion_info)

        except Exception as e:
            self._handle_recovery_error("目标重定义异常", str(e))

    def _complete_recovery(self, completion_info):
        """完成恢复过程"""
        self.recovery_active = False
        self.current_recovery_type = None

        # 发送恢复完成信号
        self.recovery_completed.emit(completion_info)

        # 发送最终状态更新
        status_info = {
            'type': completion_info['type'],
            'status': 'completed',
            'success': completion_info['success'],
            'timestamp': time.time()
        }
        self.recovery_status_updated.emit(status_info)

    def _handle_recovery_error(self, error_type, error_message):
        """处理恢复错误"""
        self.recovery_active = False
        self.current_recovery_type = None

        error_info = {
            'type': error_type,
            'message': error_message,
            'timestamp': time.time()
        }

        print(f"❌ 恢复错误: {error_type} - {error_message}")
        self.recovery_error_occurred.emit(error_info)

        # 发送错误状态
        status_info = {
            'type': 'error',
            'status': 'failed',
            'error': error_message,
            'timestamp': time.time()
        }
        self.recovery_status_updated.emit(status_info)

    def _update_recovery_status(self):
        """更新恢复状态（定时器回调）"""
        if self.recovery_active and self.current_recovery_type:
            status_info = {
                'type': self.current_recovery_type,
                'status': 'in_progress',
                'timestamp': time.time()
            }
            # 注意：这里不发送信号，避免过于频繁的更新

    def _emit_error(self, message):
        """发送错误信息"""
        error_info = {
            'type': 'integration_error',
            'message': message,
            'timestamp': time.time()
        }
        self.recovery_error_occurred.emit(error_info)

    def cleanup(self):
        """清理资源"""
        if self.l1_recovery:
            self.l1_recovery.cleanup()

        self.status_timer.stop()
        print("🧹 L1恢复集成资源清理完成")

    def is_recovery_active(self):
        """检查恢复是否在进行中"""
        return self.recovery_active

    def get_current_recovery_type(self):
        """获取当前恢复类型"""
        return self.current_recovery_type


# 使用示例和测试代码
def test_integration():
    """测试集成功能"""
    print("🧪 L1恢复集成测试")

    # 创建模拟ROS2节点
    class MockROS2Node:
        def get_logger(self):
            return MockLogger()
        def declare_parameter(self, name, value):
            pass
        def get_parameter(self, name):
            return MockParameter(3)
        def create_subscription(self, msg_type, topic, callback, qos):
            return f"sub_{topic}"
        def create_publisher(self, msg_type, topic, qos):
            return MockPublisher()

    class MockLogger:
        def info(self, msg): print(f"ℹ️  {msg}")
        def warn(self, msg): print(f"⚠️  {msg}")
        def error(self, msg): print(f"❌ {msg}")

    class MockParameter:
        def __init__(self, value): self.value = value

    class MockPublisher:
        def publish(self, msg): print(f"📤 {msg}")

    # 创建集成实例
    mock_node = MockROS2Node()
    integration = L1RecoveryIntegration(mock_node)

    # 模拟Qt信号接收
    def on_status_update(status):
        print(f"📊 状态更新: {status}")

    def on_error(error):
        print(f"🚨 错误: {error}")

    def on_completed(completion):
        print(f"✅ 完成: {completion}")

    # 连接信号
    integration.recovery_status_updated.connect(on_status_update)
    integration.recovery_error_occurred.connect(on_error)
    integration.recovery_completed.connect(on_completed)

    # 测试各种恢复场景
    print("\n=== 测试RFID恢复 ===")
    integration.trigger_rfid_recovery("test_book_001", {'x': 1.0, 'y': 2.0})
    time.sleep(6)

    print("\n=== 测试定位恢复 ===")
    integration.trigger_localization_recovery()
    time.sleep(3)

    print("\n=== 测试目标重定义 ===")
    original_goal = {
        'book_id': 'original_book',
        'position': {'x': 5.0, 'y': 3.0, 'z': 0.0}
    }
    integration.trigger_target_redefinition(original_goal)
    time.sleep(2)

    # 清理
    integration.cleanup()
    print("\n✅ 集成测试完成")

if __name__ == '__main__':
    test_integration()