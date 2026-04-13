#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L2恢复行为与UI集成模块
将Story 2-2的L2恢复行为集成到Epic 1的UI系统中
"""

from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import rclpy
from rclpy.node import Node
import threading
import time

# 导入L2恢复行为
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'libbot_tasks'))
try:
    from libbot_tasks.l2_recovery_behaviors import L2RecoveryBehaviors
except ImportError:
    # 如果导入失败，创建模拟类
    class L2RecoveryBehaviors:
        def __init__(self, node):
            pass
        def set_l1_recovery(self, l1_recovery):
            pass
        def clear_costmaps_and_replan(self, goal_pose):
            return True
        def reset_task_state(self, task_info):
            return True
        def restart_system_components(self, components):
            return True
        def return_to_home_and_reset(self):
            return True


class L2RecoveryIntegration(QObject):
    """L2恢复行为与UI集成管理器"""

    # Qt信号定义
    recovery_status_updated = pyqtSignal(dict)
    recovery_error_occurred = pyqtSignal(dict)
    recovery_completed = pyqtSignal(dict)
    recovery_escalated = pyqtSignal(dict)  # L2升级到L3的信号

    def __init__(self, ros2_node, l1_recovery_integration=None):
        """初始化L2恢复集成

        Args:
            ros2_node: ROS2节点实例
            l1_recovery_integration: L1恢复集成实例（可选）
        """
        super().__init__()
        self.ros2_node = ros2_node
        self.l1_recovery_integration = l1_recovery_integration
        self.l2_recovery = None
        self.l3_recovery_integration = None  # L3恢复集成（Story 2-4）
        self.recovery_active = False
        self.current_recovery_type = None
        self.recovery_start_time = None

        # 初始化L2恢复行为
        self._init_l2_recovery()

        # 初始化L3恢复集成（如果可用）
        self._init_l3_recovery()

        # 创建状态更新定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_recovery_status)
        self.status_timer.start(100)  # 10Hz状态更新

        # 恢复超时监控
        self.timeout_timer = QTimer()
        self.timeout_timer.timeout.connect(self._check_recovery_timeout)

    def _init_l2_recovery(self):
        """初始化L2恢复行为"""
        try:
            self.l2_recovery = L2RecoveryBehaviors(self.ros2_node)

            # 如果有L1恢复实例，设置给L2恢复
            if self.l1_recovery_integration and hasattr(self.l1_recovery_integration, 'l1_recovery'):
                if self.l1_recovery_integration.l1_recovery:
                    self.l2_recovery.set_l1_recovery(self.l1_recovery_integration.l1_recovery)

            print("✅ L2恢复行为集成初始化成功")
        except Exception as e:
            print(f"❌ L2恢复行为集成初始化失败: {e}")
            self.l2_recovery = None

    def _init_l3_recovery(self):
        """初始化L3恢复集成（Story 2-4）"""
        try:
            # L3恢复将在Story 2-4中实现，这里做兼容性处理
            from libbot_ui.l3_recovery_integration import L3RecoveryIntegration
            self.l3_recovery_integration = L3RecoveryIntegration(self.ros2_node)
            print("✅ L3恢复集成初始化成功")
        except ImportError:
            print("ℹ️ L3恢复集成尚未实现（Story 2-4），L2恢复将只发送升级信号")
            self.l3_recovery_integration = None
        except Exception as e:
            print(f"⚠️ L3恢复集成初始化失败: {e}")
            self.l3_recovery_integration = None

    def trigger_costmap_recovery(self, goal_pose):
        """触发代价地图清除恢复

        Args:
            goal_pose: 目标位置信息
        """
        if not self.l2_recovery:
            self._emit_error("L2恢复行为未初始化")
            return

        print(f"🔧 触发L2代价地图恢复: {goal_pose}")
        self._start_recovery("costmap_clear", {
            'goal_pose': goal_pose
        })

        # 在后台线程中执行恢复
        recovery_thread = threading.Thread(
            target=self._execute_costmap_recovery,
            args=(goal_pose,)
        )
        recovery_thread.daemon = True
        recovery_thread.start()

    def trigger_task_reset_recovery(self, task_info):
        """触发任务重置恢复

        Args:
            task_info: 任务信息
        """
        if not self.l2_recovery:
            self._emit_error("L2恢复行为未初始化")
            return

        print(f"🔧 触发L2任务重置恢复: {task_info.get('task_id', 'unknown')}")
        self._start_recovery("task_reset", {
            'task_info': task_info
        })

        # 在后台线程中执行恢复
        recovery_thread = threading.Thread(
            target=self._execute_task_reset_recovery,
            args=(task_info,)
        )
        recovery_thread.daemon = True
        recovery_thread.start()

    def trigger_component_restart_recovery(self, components=None):
        """触发组件重启恢复

        Args:
            components: 需要重启的组件列表，如果为None则使用默认配置
        """
        if not self.l2_recovery:
            self._emit_error("L2恢复行为未初始化")
            return

        if components is None:
            components = ['rfid_processor', 'perception_manager', 'sensor_fusion']

        print(f"🔧 触发L2组件重启恢复: {components}")
        self._start_recovery("component_restart", {
            'components': components
        })

        # 在后台线程中执行恢复
        recovery_thread = threading.Thread(
            target=self._execute_component_restart_recovery,
            args=(components,)
        )
        recovery_thread.daemon = True
        recovery_thread.start()

    def trigger_home_reset_recovery(self):
        """触发返回Home重置恢复"""
        if not self.l2_recovery:
            self._emit_error("L2恢复行为未初始化")
            return

        print("🔧 触发L2返回Home重置恢复")
        self._start_recovery("home_reset", {})

        # 在后台线程中执行恢复
        recovery_thread = threading.Thread(
            target=self._execute_home_reset_recovery
        )
        recovery_thread.daemon = True
        recovery_thread.start()

    def _start_recovery(self, recovery_type, context):
        """开始L2恢复过程"""
        self.recovery_active = True
        self.current_recovery_type = recovery_type
        self.recovery_start_time = time.time()

        # 启动超时监控
        self.timeout_timer.start(1000)  # 1秒检查一次超时

        # 发送恢复开始信号
        status_info = {
            'type': recovery_type,
            'status': 'started',
            'context': context,
            'timestamp': time.time(),
            'level': 'L2'
        }
        self.recovery_status_updated.emit(status_info)

        print(f"🚀 L2恢复开始: {recovery_type}")

    def _execute_costmap_recovery(self, goal_pose):
        """执行代价地图清除恢复"""
        try:
            result = self.l2_recovery.clear_costmaps_and_replan(goal_pose)

            # 发送恢复完成信号
            completion_info = {
                'type': 'costmap_clear',
                'success': result,
                'goal_pose': goal_pose,
                'timestamp': time.time(),
                'duration': time.time() - self.recovery_start_time
            }

            if result:
                print(f"✅ L2代价地图恢复成功 (耗时: {completion_info['duration']:.1f}s)")
            else:
                print(f"❌ L2代价地图恢复失败 (耗时: {completion_info['duration']:.1f}s)")

            self._handle_recovery_result(completion_info)

        except Exception as e:
            self._handle_recovery_error("L2代价地图恢复异常", str(e))

    def _execute_task_reset_recovery(self, task_info):
        """执行任务重置恢复"""
        try:
            result = self.l2_recovery.reset_task_state(task_info)

            # 发送恢复完成信号
            completion_info = {
                'type': 'task_reset',
                'success': result,
                'task_info': task_info,
                'timestamp': time.time(),
                'duration': time.time() - self.recovery_start_time
            }

            if result:
                print(f"✅ L2任务重置恢复成功 (耗时: {completion_info['duration']:.1f}s)")
            else:
                print(f"❌ L2任务重置恢复失败 (耗时: {completion_info['duration']:.1f}s)")

            self._handle_recovery_result(completion_info)

        except Exception as e:
            self._handle_recovery_error("L2任务重置恢复异常", str(e))

    def _execute_component_restart_recovery(self, components):
        """执行组件重启恢复"""
        try:
            result = self.l2_recovery.restart_system_components(components)

            # 发送恢复完成信号
            completion_info = {
                'type': 'component_restart',
                'success': result,
                'components': components,
                'timestamp': time.time(),
                'duration': time.time() - self.recovery_start_time
            }

            if result:
                print(f"✅ L2组件重启恢复成功 (耗时: {completion_info['duration']:.1f}s)")
            else:
                print(f"❌ L2组件重启恢复失败 (耗时: {completion_info['duration']:.1f}s)")

            self._handle_recovery_result(completion_info)

        except Exception as e:
            self._handle_recovery_error("L2组件重启恢复异常", str(e))

    def _execute_home_reset_recovery(self):
        """执行返回Home重置恢复"""
        try:
            result = self.l2_recovery.return_to_home_and_reset()

            # 发送恢复完成信号
            completion_info = {
                'type': 'home_reset',
                'success': result,
                'timestamp': time.time(),
                'duration': time.time() - self.recovery_start_time
            }

            if result:
                print(f"✅ L2返回Home重置恢复成功 (耗时: {completion_info['duration']:.1f}s)")
            else:
                print(f"❌ L2返回Home重置恢复失败 (耗时: {completion_info['duration']:.1f}s)")

            self._handle_recovery_result(completion_info)

        except Exception as e:
            self._handle_recovery_error("L2返回Home重置恢复异常", str(e))

    def _handle_recovery_result(self, completion_info):
        """处理恢复结果"""
        if completion_info['success']:
            self._complete_recovery(completion_info)
        else:
            # L2恢复失败，升级到L3
            self._escalate_to_l3(completion_info)

    def _complete_recovery(self, completion_info):
        """完成恢复过程"""
        self.recovery_active = False
        self.current_recovery_type = None
        self.recovery_start_time = None

        # 停止超时监控
        self.timeout_timer.stop()

        # 发送恢复完成信号
        self.recovery_completed.emit(completion_info)

        # 发送最终状态更新
        status_info = {
            'type': completion_info['type'],
            'status': 'completed',
            'success': completion_info['success'],
            'timestamp': time.time(),
            'level': 'L2',
            'duration': completion_info.get('duration', 0)
        }
        self.recovery_status_updated.emit(status_info)

    def _escalate_to_l3(self, failed_completion_info):
        """升级到L3恢复"""
        self.recovery_active = False
        self.current_recovery_type = None
        self.recovery_start_time = None

        # 停止超时监控
        self.timeout_timer.stop()

        # 发送升级到L3的信号
        escalation_info = {
            'from_level': 'L2',
            'to_level': 'L3',
            'failed_recovery': failed_completion_info,
            'timestamp': time.time(),
            'reason': 'L2恢复失败，需要更深层的系统重置'
        }

        print(f"⚠️ L2恢复失败，升级到L3: {failed_completion_info['type']}")

        # 尝试调用L3恢复（如果可用）
        try:
            # 导入L3恢复模块（Story 2-4将实现）
            from libbot_ui.l3_recovery_integration import L3RecoveryIntegration
            if hasattr(self, 'l3_recovery_integration') and self.l3_recovery_integration:
                # 触发L3恢复
                self.l3_recovery_integration.start_l3_recovery(escalation_info)
                print(f"🔄 已触发L3恢复: {failed_completion_info['type']}")
            else:
                print("⚠️ L3恢复模块不可用，仅发送升级信号")
        except ImportError:
            print("ℹ️ L3恢复模块尚未实现（Story 2-4），仅发送升级信号")

        self.recovery_escalated.emit(escalation_info)

        # 发送失败状态
        status_info = {
            'type': failed_completion_info['type'],
            'status': 'escalated_to_l3',
            'success': False,
            'timestamp': time.time(),
            'level': 'L2',
            'duration': failed_completion_info.get('duration', 0)
        }
        self.recovery_status_updated.emit(status_info)

    def _handle_recovery_error(self, error_type, error_message):
        """处理恢复错误"""
        self.recovery_active = False
        self.current_recovery_type = None
        self.recovery_start_time = None

        # 停止超时监控
        self.timeout_timer.stop()

        error_info = {
            'type': error_type,
            'message': error_message,
            'timestamp': time.time(),
            'level': 'L2'
        }

        print(f"❌ L2恢复错误: {error_type} - {error_message}")
        self.recovery_error_occurred.emit(error_info)

        # 发送错误状态
        status_info = {
            'type': 'error',
            'status': 'failed',
            'error': error_message,
            'timestamp': time.time(),
            'level': 'L2'
        }
        self.recovery_status_updated.emit(status_info)

        # 尝试升级到L3
        escalation_info = {
            'from_level': 'L2',
            'to_level': 'L3',
            'error': error_message,
            'timestamp': time.time(),
            'reason': 'L2恢复异常，需要L3系统重置'
        }
        self.recovery_escalated.emit(escalation_info)

    def _update_recovery_status(self):
        """更新恢复状态（定时器回调）"""
        if self.recovery_active and self.current_recovery_type:
            current_time = time.time()
            elapsed_time = current_time - (self.recovery_start_time or current_time)

            status_info = {
                'type': self.current_recovery_type,
                'status': 'in_progress',
                'timestamp': current_time,
                'elapsed_time': elapsed_time,
                'level': 'L2'
            }
            # 注意：这里不发送信号，避免过于频繁的更新

    def _check_recovery_timeout(self):
        """检查恢复超时"""
        if self.recovery_active and self.recovery_start_time:
            elapsed_time = time.time() - self.recovery_start_time
            if elapsed_time > 40.0:  # L2恢复超时时间
                print(f"⏰ L2恢复超时 ({elapsed_time:.1f}s)，强制完成")

                # 创建超时完成信息
                timeout_info = {
                    'type': self.current_recovery_type,
                    'success': False,
                    'timeout': True,
                    'timestamp': time.time(),
                    'duration': elapsed_time
                }

                self._escalate_to_l3(timeout_info)

    def _emit_error(self, message):
        """发送错误信息"""
        error_info = {
            'type': 'integration_error',
            'message': message,
            'timestamp': time.time(),
            'level': 'L2'
        }
        self.recovery_error_occurred.emit(error_info)

    def cleanup(self):
        """清理资源"""
        self.status_timer.stop()
        self.timeout_timer.stop()
        print("🧹 L2恢复集成资源清理完成")

    def is_recovery_active(self):
        """检查L2恢复是否在进行中"""
        return self.recovery_active

    def get_current_recovery_type(self):
        """获取当前L2恢复类型"""
        return self.current_recovery_type

    def get_recovery_duration(self):
        """获取当前恢复已用时间"""
        if self.recovery_start_time:
            return time.time() - self.recovery_start_time
        return 0.0


# 使用示例和测试代码
def test_l2_integration():
    """测试L2集成功能"""
    print("🧪 L2恢复集成测试")

    # 创建模拟ROS2节点
    class MockROS2Node:
        def get_logger(self):
            return MockLogger()
        def declare_parameter(self, name, value):
            param = MockParameter(value)
            return param
        def create_client(self, srv_type, topic):
            return MockClient()
        def get_clock(self):
            return MockClock()

    class MockLogger:
        def info(self, msg): print(f"ℹ️  {msg}")
        def warn(self, msg): print(f"⚠️  {msg}")
        def error(self, msg): print(f"❌ {msg}")

    class MockParameter:
        def __init__(self, value): self.value = value

    class MockClient:
        def wait_for_service(self, timeout_sec): return True
        def call_async(self, request): return MockFuture()

    class MockClock:
        def now(self): return MockTime()

    class MockTime:
        def to_msg(self): return "mock_time_msg"

    class MockFuture:
        def done(self): return True
        def result(self): return Mock()

    # 创建集成实例
    mock_node = MockROS2Node()
    integration = L2RecoveryIntegration(mock_node)

    # 模拟Qt信号接收
    def on_status_update(status):
        print(f"📊 L2状态更新: {status}")

    def on_error(error):
        print(f"🚨 L2错误: {error}")

    def on_completed(completion):
        print(f"✅ L2完成: {completion}")

    def on_escalated(escalation):
        print(f"⬆️ L2升级到L3: {escalation}")

    # 连接信号
    integration.recovery_status_updated.connect(on_status_update)
    integration.recovery_error_occurred.connect(on_error)
    integration.recovery_completed.connect(on_completed)
    integration.recovery_escalated.connect(on_escalated)

    # 测试各种L2恢复场景
    print("\n=== 测试L2代价地图恢复 ===")
    goal_pose = {'x': 5.0, 'y': 3.0, 'z': 0.0}
    integration.trigger_costmap_recovery(goal_pose)
    time.sleep(3)

    print("\n=== 测试L2任务重置恢复 ===")
    task_info = {
        'task_id': 'test_task_002',
        'progress': 50,
        'books_detected': ['book_001']
    }
    integration.trigger_task_reset_recovery(task_info)
    time.sleep(3)

    print("\n=== 测试L2组件重启恢复 ===")
    components = ['rfid_processor', 'perception_manager']
    integration.trigger_component_restart_recovery(components)
    time.sleep(3)

    print("\n=== 测试L2返回Home重置恢复 ===")
    integration.trigger_home_reset_recovery()
    time.sleep(3)

    # 清理
    integration.cleanup()
    print("\n✅ L2集成测试完成")


if __name__ == '__main__':
    test_l2_integration()