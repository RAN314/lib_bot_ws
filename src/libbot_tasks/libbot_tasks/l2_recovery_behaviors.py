#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L2恢复行为实现 - 任务层面重置，30-40秒恢复时间
继承L1恢复的基础架构，实现更深层的系统重置
"""

import rclpy
from rclpy.node import Node
from typing import Optional, Dict, Any, List
import time
import threading
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from nav2_msgs.srv import ClearEntireCostmap
import rclpy.action


class L2RecoveryBehaviors:
    """L2状态重置行为 - 任务层面重置，30-40秒"""

    def __init__(self, node: Node):
        """初始化L2恢复行为

        Args:
            node: ROS2节点实例
        """
        self.node = node
        self.recovery_timeout = 40.0  # 40秒超时
        self.l1_recovery = None  # L1恢复实例

        # 从参数服务器获取配置
        self._load_parameters()

        # ROS2客户端初始化
        self._init_ros_clients()

    def _load_parameters(self):
        """从ROS2参数服务器加载配置"""
        try:
            # L2恢复基本参数
            self.max_consecutive_failures = self.node.declare_parameter(
                'recovery.l2.max_consecutive_failures', 2
            ).value

            # 代价地图清除参数
            self.global_costmap_timeout = self.node.declare_parameter(
                'recovery.l2.costmap_clear.global_timeout', 15.0
            ).value
            self.local_costmap_timeout = self.node.declare_parameter(
                'recovery.l2.costmap_clear.local_timeout', 10.0
            ).value
            self.replan_timeout = self.node.declare_parameter(
                'recovery.l2.costmap_clear.replan_timeout', 15.0
            ).value

            # 任务重置参数
            self.context_save_timeout = self.node.declare_parameter(
                'recovery.l2.task_reset.context_save_timeout', 5.0
            ).value
            self.reset_timeout = self.node.declare_parameter(
                'recovery.l2.task_reset.reset_timeout', 10.0
            ).value
            self.restore_timeout = self.node.declare_parameter(
                'recovery.l2.task_reset.restore_timeout', 5.0
            ).value

            # 组件重启参数
            self.component_restart_timeout = self.node.declare_parameter(
                'recovery.l2.component_restart.restart_timeout', 20.0
            ).value

            # Home重置参数
            self.home_navigation_timeout = self.node.declare_parameter(
                'recovery.l2.home_reset.navigation_timeout', 25.0
            ).value
            self.reinit_timeout = self.node.declare_parameter(
                'recovery.l2.home_reset.reinit_timeout', 15.0
            ).value

            self.node.get_logger().info("L2恢复参数加载完成")

        except Exception as e:
            self.node.get_logger().warn(f"参数加载失败，使用默认值: {str(e)}")
            # 设置默认值
            self._set_default_parameters()

    def _set_default_parameters(self):
        """设置默认参数值"""
        self.max_consecutive_failures = 2
        self.global_costmap_timeout = 15.0
        self.local_costmap_timeout = 10.0
        self.replan_timeout = 15.0
        self.context_save_timeout = 5.0
        self.reset_timeout = 10.0
        self.restore_timeout = 5.0
        self.component_restart_timeout = 20.0
        self.home_navigation_timeout = 25.0
        self.reinit_timeout = 15.0

    def _init_ros_clients(self):
        """初始化ROS2服务客户端"""
        try:
            # 代价地图清除服务客户端
            self.global_costmap_client = self.node.create_client(
                ClearEntireCostmap, '/global_costmap/clear_entire_costmap'
            )
            self.local_costmap_client = self.node.create_client(
                ClearEntireCostmap, '/local_costmap/clear_entire_costmap'
            )

            # 导航Action客户端
            self.nav_action_client = rclpy.action.ActionClient(
                self.node, NavigateToPose, '/navigate_to_pose'
            )

            self.node.get_logger().info("ROS2客户端初始化完成")

        except Exception as e:
            self.node.get_logger().error(f"ROS2客户端初始化失败: {str(e)}")

    def set_l1_recovery(self, l1_recovery):
        """设置L1恢复实例用于协同工作"""
        self.l1_recovery = l1_recovery

    def clear_costmaps_and_replan(self, goal_pose: Dict[str, Any]) -> bool:
        """清除代价地图并重新规划路径

        当导航持续失败时，清除所有代价地图并重新规划

        Args:
            goal_pose: 目标位置信息

        Returns:
            bool: 重新规划是否成功
        """
        start_time = time.time()

        try:
            self.node.get_logger().info("L2恢复: 清除代价地图并重新规划")

            # 清除全局代价地图
            if not self._clear_global_costmap():
                self.node.get_logger().error("L2恢复失败: 全局代价地图清除失败")
                return False

            # 清除局部代价地图
            if not self._clear_local_costmap():
                self.node.get_logger().error("L2恢复失败: 局部代价地图清除失败")
                return False

            # 重新规划路径
            success = self._replan_path(goal_pose)

            elapsed_time = time.time() - start_time

            if success:
                self.node.get_logger().info(f"L2恢复成功: 代价地图清除并重新规划完成 (耗时: {elapsed_time:.1f}s)")
                return True
            else:
                self.node.get_logger().warn(f"L2恢复失败: 重新规划未成功 (耗时: {elapsed_time:.1f}s)")
                return False

        except Exception as e:
            elapsed_time = time.time() - start_time
            self.node.get_logger().error(f"L2代价地图清除错误 (耗时: {elapsed_time:.1f}s): {str(e)}")
            return False

    def reset_task_state(self, task_info: Dict[str, Any]) -> bool:
        """任务状态重置

        重置当前任务状态，重新开始任务执行

        Args:
            task_info: 任务信息

        Returns:
            bool: 重置是否成功
        """
        start_time = time.time()

        try:
            task_id = task_info.get('task_id', 'unknown')
            self.node.get_logger().info(f"L2恢复: 重置任务状态 {task_id}")

            # 保存任务上下文
            saved_context = self._save_task_context(task_info)
            if saved_context is None:
                self.node.get_logger().error("L2恢复失败: 任务上下文保存失败")
                return False

            # 重置任务执行状态
            if not self._reset_task_execution():
                self.node.get_logger().error("L2恢复失败: 任务执行状态重置失败")
                return False

            # 恢复任务上下文
            if not self._restore_task_context(saved_context):
                self.node.get_logger().error("L2恢复失败: 任务上下文恢复失败")
                return False

            # 重新开始任务
            success = self._restart_task(task_info)

            elapsed_time = time.time() - start_time

            if success:
                self.node.get_logger().info(f"L2恢复成功: 任务状态重置完成 (耗时: {elapsed_time:.1f}s)")
                return True
            else:
                self.node.get_logger().warn(f"L2恢复失败: 任务重启失败 (耗时: {elapsed_time:.1f}s)")
                return False

        except Exception as e:
            elapsed_time = time.time() - start_time
            self.node.get_logger().error(f"L2任务重置错误 (耗时: {elapsed_time:.1f}s): {str(e)}")
            return False

    def restart_system_components(self, components: List[str]) -> bool:
        """系统组件重启

        选择性重启指定的系统组件

        Args:
            components: 需要重启的组件列表

        Returns:
            bool: 重启是否成功
        """
        start_time = time.time()

        try:
            self.node.get_logger().info(f"L2恢复: 重启系统组件 {components}")

            success_count = 0
            failed_components = []

            for component in components:
                if self._restart_single_component(component):
                    success_count += 1
                    self.node.get_logger().info(f"组件 {component} 重启成功")
                else:
                    failed_components.append(component)
                    self.node.get_logger().warn(f"组件 {component} 重启失败")

            elapsed_time = time.time() - start_time

            # 如果所有组件都成功重启
            if success_count == len(components):
                self.node.get_logger().info(f"L2恢复成功: 所有组件重启完成 (耗时: {elapsed_time:.1f}s)")
                return True
            elif success_count > 0:
                self.node.get_logger().warn(
                    f"L2恢复部分成功: {success_count}/{len(components)} 组件重启成功, "
                    f"失败组件: {failed_components} (耗时: {elapsed_time:.1f}s)"
                )
                return True  # 部分成功也算成功
            else:
                self.node.get_logger().error(
                    f"L2恢复失败: 所有组件重启失败 {failed_components} (耗时: {elapsed_time:.1f}s)"
                )
                return False

        except Exception as e:
            elapsed_time = time.time() - start_time
            self.node.get_logger().error(f"L2组件重启错误 (耗时: {elapsed_time:.1f}s): {str(e)}")
            return False

    def return_to_home_and_reset(self) -> bool:
        """返回Home位置并重新初始化

        当其他恢复方法都失败时，返回Home位置重新开始

        Returns:
            bool: 返回并重置是否成功
        """
        start_time = time.time()

        try:
            self.node.get_logger().info("L2恢复: 返回Home位置并重新初始化")

            # 导航到Home位置
            if not self._navigate_to_home():
                self.node.get_logger().error("L2恢复失败: 返回Home位置失败")
                return False

            # 重新初始化系统
            if not self._reinitialize_system():
                self.node.get_logger().error("L2恢复失败: 系统重新初始化失败")
                return False

            # 更新系统状态
            success = self._update_system_status()

            elapsed_time = time.time() - start_time

            if success:
                self.node.get_logger().info(f"L2恢复成功: 返回Home并重新初始化完成 (耗时: {elapsed_time:.1f}s)")
                return True
            else:
                self.node.get_logger().warn(f"L2恢复失败: 系统重新初始化失败 (耗时: {elapsed_time:.1f}s)")
                return False

        except Exception as e:
            elapsed_time = time.time() - start_time
            self.node.get_logger().error(f"L2返回Home错误 (耗时: {elapsed_time:.1f}s): {str(e)}")
            return False

    # 私有方法实现
    def _clear_global_costmap(self) -> bool:
        """清除全局代价地图"""
        try:
            if not self.global_costmap_client.wait_for_service(timeout_sec=5.0):
                self.node.get_logger().error("全局代价地图清除服务不可用")
                return False

            request = ClearEntireCostmap.Request()
            future = self.global_costmap_client.call_async(request)

            # 等待服务调用完成
            if not self._wait_for_service_result(future, self.global_costmap_timeout):
                self.node.get_logger().error("全局代价地图清除超时")
                return False

            return True

        except Exception as e:
            self.node.get_logger().error(f"清除全局代价地图错误: {str(e)}")
            return False

    def _clear_local_costmap(self) -> bool:
        """清除局部代价地图"""
        try:
            if not self.local_costmap_client.wait_for_service(timeout_sec=5.0):
                self.node.get_logger().error("局部代价地图清除服务不可用")
                return False

            request = ClearEntireCostmap.Request()
            future = self.local_costmap_client.call_async(request)

            # 等待服务调用完成
            if not self._wait_for_service_result(future, self.local_costmap_timeout):
                self.node.get_logger().error("局部代价地图清除超时")
                return False

            return True

        except Exception as e:
            self.node.get_logger().error(f"清除局部代价地图错误: {str(e)}")
            return False

    def _replan_path(self, goal_pose: Dict[str, Any]) -> bool:
        """重新规划路径"""
        try:
            # 创建目标位姿
            goal = PoseStamped()
            goal.header.frame_id = "map"
            goal.header.stamp = self.node.get_clock().now().to_msg()
            goal.pose.position.x = goal_pose.get('x', 0.0)
            goal.pose.position.y = goal_pose.get('y', 0.0)
            goal.pose.orientation.w = 1.0

            # 发送导航目标
            if not self.nav_action_client.wait_for_server(timeout_sec=5.0):
                self.node.get_logger().error("导航Action服务器不可用")
                return False

            action_goal = NavigateToPose.Goal()
            action_goal.pose = goal

            # 发送目标并等待结果
            send_goal_future = self.nav_action_client.send_goal_async(action_goal)

            if not self._wait_for_future(send_goal_future, self.replan_timeout):
                self.node.get_logger().error("发送导航目标超时")
                return False

            goal_handle = send_goal_future.result()
            if not goal_handle.accepted:
                self.node.get_logger().error("导航目标被拒绝")
                return False

            # 获取结果
            result_future = goal_handle.get_result_async()
            if not self._wait_for_future(result_future, self.replan_timeout):
                self.node.get_logger().error("获取导航结果超时")
                return False

            result = result_future.result().result
            return result.result.success

        except Exception as e:
            self.node.get_logger().error(f"重新规划路径错误: {str(e)}")
            return False

    def _save_task_context(self, task_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """保存任务上下文"""
        try:
            # 创建任务上下文快照
            context = {
                'task_id': task_info.get('task_id'),
                'start_time': task_info.get('start_time'),
                'current_progress': task_info.get('progress', 0),
                'books_detected': task_info.get('books_detected', []),
                'navigation_attempts': task_info.get('navigation_attempts', 0),
                'scan_attempts': task_info.get('scan_attempts', 0),
                'saved_at': time.time()
            }

            self.node.get_logger().info(f"任务上下文保存完成: {context['task_id']}")
            return context

        except Exception as e:
            self.node.get_logger().error(f"保存任务上下文错误: {str(e)}")
            return None

    def _reset_task_execution(self) -> bool:
        """重置任务执行状态"""
        try:
            # 重置任务状态到初始状态
            self.node.get_logger().info("重置任务执行状态到初始状态")

            # 模拟重置操作
            time.sleep(0.5)  # 模拟重置时间

            return True

        except Exception as e:
            self.node.get_logger().error(f"重置任务执行状态错误: {str(e)}")
            return False

    def _restore_task_context(self, context: Dict[str, Any]) -> bool:
        """恢复任务上下文"""
        try:
            task_id = context.get('task_id', 'unknown')
            self.node.get_logger().info(f"恢复任务上下文: {task_id}")

            # 模拟恢复操作
            time.sleep(0.3)  # 模拟恢复时间

            return True

        except Exception as e:
            self.node.get_logger().error(f"恢复任务上下文错误: {str(e)}")
            return False

    def _restart_task(self, task_info: Dict[str, Any]) -> bool:
        """重新开始任务"""
        try:
            task_id = task_info.get('task_id', 'unknown')
            self.node.get_logger().info(f"重新开始任务: {task_id}")

            # 模拟任务重启
            time.sleep(0.5)  # 模拟重启时间

            return True

        except Exception as e:
            self.node.get_logger().error(f"重新开始任务错误: {str(e)}")
            return False

    def _restart_single_component(self, component: str) -> bool:
        """重启单个系统组件"""
        try:
            self.node.get_logger().info(f"重启组件: {component}")

            # 模拟组件重启过程
            time.sleep(1.0)  # 模拟重启时间

            # 模拟重启结果（90%成功率）
            import random
            success = random.random() < 0.9

            return success

        except Exception as e:
            self.node.get_logger().error(f"重启组件 {component} 错误: {str(e)}")
            return False

    def _navigate_to_home(self) -> bool:
        """导航到Home位置"""
        try:
            # Home位置配置
            home_position = {
                'x': 0.0,
                'y': 0.0,
                'z': 0.0
            }

            self.node.get_logger().info(f"导航到Home位置: {home_position}")

            # 使用重新规划方法导航到Home
            return self._replan_path(home_position)

        except Exception as e:
            self.node.get_logger().error(f"导航到Home位置错误: {str(e)}")
            return False

    def _reinitialize_system(self) -> bool:
        """重新初始化系统"""
        try:
            self.node.get_logger().info("重新初始化系统")

            # 模拟系统重新初始化过程
            time.sleep(2.0)  # 模拟初始化时间

            # 重新初始化各个子系统
            subsystems = ['navigation', 'perception', 'rfid', 'sensors']
            for subsystem in subsystems:
                self.node.get_logger().info(f"初始化子系统: {subsystem}")
                time.sleep(0.3)

            return True

        except Exception as e:
            self.node.get_logger().error(f"重新初始化系统错误: {str(e)}")
            return False

    def _update_system_status(self) -> bool:
        """更新系统状态"""
        try:
            self.node.get_logger().info("更新系统状态到正常")

            # 模拟状态更新
            time.sleep(0.2)

            return True

        except Exception as e:
            self.node.get_logger().error(f"更新系统状态错误: {str(e)}")
            return False

    def _wait_for_service_result(self, future, timeout: float) -> bool:
        """等待服务调用结果"""
        try:
            end_time = time.time() + timeout
            while time.time() < end_time:
                if future.done():
                    return future.result() is not None
                time.sleep(0.1)
            return False
        except Exception:
            return False

    def _wait_for_future(self, future, timeout: float) -> bool:
        """等待Future完成"""
        try:
            end_time = time.time() + timeout
            while time.time() < end_time:
                if future.done():
                    return True
                time.sleep(0.1)
            return False
        except Exception:
            return False


def main():
    """测试函数"""
    import rclpy

    rclpy.init()

    # 创建测试节点
    test_node = Node("l2_recovery_test")

    # 创建L2恢复实例
    l2_recovery = L2RecoveryBehaviors(test_node)

    # 测试各个恢复方法
    print("🧪 开始L2恢复测试")

    # 测试代价地图清除
    print("\n=== 测试代价地图清除 ===")
    test_goal = {'x': 5.0, 'y': 3.0}
    result = l2_recovery.clear_costmaps_and_replan(test_goal)
    print(f"代价地图清除结果: {'成功' if result else '失败'}")

    # 测试任务重置
    print("\n=== 测试任务重置 ===")
    test_task = {
        'task_id': 'test_task_001',
        'progress': 50,
        'books_detected': ['book_001']
    }
    result = l2_recovery.reset_task_state(test_task)
    print(f"任务重置结果: {'成功' if result else '失败'}")

    # 测试组件重启
    print("\n=== 测试组件重启 ===")
    test_components = ['rfid_processor', 'navigation_node', 'sensor_fusion']
    result = l2_recovery.restart_system_components(test_components)
    print(f"组件重启结果: {'成功' if result else '失败'}")

    # 测试返回Home
    print("\n=== 测试返回Home ===")
    result = l2_recovery.return_to_home_and_reset()
    print(f"返回Home结果: {'成功' if result else '失败'}")

    # 清理
    test_node.destroy_node()
    rclpy.shutdown()

    print("\n✅ L2恢复测试完成")


if __name__ == "__main__":
    main()