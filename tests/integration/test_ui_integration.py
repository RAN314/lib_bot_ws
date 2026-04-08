#!/usr/bin/env python3
"""
UI集成测试
测试UI与Action服务器的集成，包括任务启动和取消功能
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import time
import threading
import sys
import os

# 添加UI包路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/libbot_ui'))

from libbot_msgs.action import FindBook, PerformInventory
from libbot_ui.ros2_manager import Ros2Manager


class TestUIIntegrationServer(Node):
    """UI集成测试的Action服务器"""

    def __init__(self):
        super().__init__("test_ui_integration_server")

        # 使用可重入回调组支持并行执行
        self.callback_group = ReentrantCallbackGroup()

        # 创建FindBook Action服务器
        self._find_book_server = ActionServer(
            self,
            FindBook,
            "/find_book",
            execute_callback=self._find_book_execute_callback,
            callback_group=self.callback_group,
            goal_callback=self._goal_callback,
            cancel_callback=self._cancel_callback
        )

        # 创建PerformInventory Action服务器
        self._inventory_server = ActionServer(
            self,
            PerformInventory,
            "/perform_inventory",
            execute_callback=self._inventory_execute_callback,
            callback_group=self.callback_group,
            goal_callback=self._goal_callback,
            cancel_callback=self._cancel_callback
        )

        self.get_logger().info("UI Integration Test Servers started")

    def _goal_callback(self, goal_request):
        """Goal请求回调"""
        self.get_logger().info(f"Received goal request")
        return GoalResponse.ACCEPT

    def _cancel_callback(self, goal_handle):
        """取消请求回调"""
        self.get_logger().info("Cancel request received")
        return CancelResponse.ACCEPT

    async def _find_book_execute_callback(self, goal_handle):
        """FindBook执行回调"""
        self.get_logger().info("Starting FindBook execution for UI integration test...")

        book_id = goal_handle.request.book_id
        feedback = FindBook.Feedback()

        try:
            # 模拟找书过程
            for i in range(1, 51):  # 50 steps, 2 seconds each
                if self._check_cancel_request(goal_handle):
                    return FindBook.Result()

                # 更新反馈
                feedback.status = "navigating" if i <= 20 else "scanning" if i <= 40 else "approaching"
                feedback.progress = i * 2.0  # 0-100%
                feedback.distance_to_goal = max(0.0, 10.0 - i * 0.2)
                feedback.current_pose.position.x = i * 0.2
                feedback.current_pose.position.y = i * 0.1
                feedback.signal_strength = 0.8 if i > 35 else 0.0
                feedback.books_detected = [book_id] if i > 35 else []
                feedback.estimated_remaining = (50 - i) * 2.0

                goal_handle.publish_feedback(feedback)

                if i % 10 == 0:
                    self.get_logger().info(f"FindBook: {feedback.progress:.1f}% - {feedback.status}")

                rclpy.spin_once(self, timeout_sec=2.0)

            # 完成
            goal_handle.succeed()

            result = FindBook.Result()
            result.success = True
            result.message = f"Successfully found book {book_id} in UI integration test"
            result.search_time = 100.0
            result.navigation_attempts = 1
            result.scan_attempts = 20

            self.get_logger().info("FindBook goal completed successfully")
            return result

        except Exception as e:
            self.get_logger().error(f"Error during FindBook execution: {e}")
            goal_handle.abort()
            return FindBook.Result()

    async def _inventory_execute_callback(self, goal_handle):
        """PerformInventory执行回调"""
        self.get_logger().info("Starting PerformInventory execution for UI integration test...")

        target_zone = goal_handle.request.target_zone
        feedback = PerformInventory.Feedback()

        try:
            # 模拟盘点过程
            for i in range(1, 26):  # 25 steps, 3 seconds each
                if self._check_cancel_request(goal_handle):
                    return PerformInventory.Result()

                # 更新反馈
                feedback.status = "planning" if i <= 5 else "scanning_zone" if i <= 20 else "verifying"
                feedback.progress = i * 4.0  # 0-100%
                feedback.current_zone = target_zone if i > 5 else "planning"
                feedback.books_checked = i * 10
                feedback.misplacements_current = i // 5
                feedback.estimated_remaining = (25 - i) * 3.0

                goal_handle.publish_feedback(feedback)

                if i % 5 == 0:
                    self.get_logger().info(
                        f"Inventory: {feedback.progress:.1f}% - {feedback.status}, "
                        f"checked={feedback.books_checked}"
                    )

                rclpy.spin_once(self, timeout_sec=3.0)

            # 完成
            goal_handle.succeed()

            result = PerformInventory.Result()
            result.success = True
            result.message = f"Successfully completed inventory for zone {target_zone}"
            result.execution_time = 75.0
            result.books_checked = 250
            result.books_misplaced = 5
            result.books_missing = 0
            result.mismatched_books = "[]"

            self.get_logger().info("PerformInventory goal completed successfully")
            return result

        except Exception as e:
            self.get_logger().error(f"Error during PerformInventory execution: {e}")
            goal_handle.abort()
            return PerformInventory.Result()

    def _check_cancel_request(self, goal_handle):
        """检查取消请求"""
        if not goal_handle.is_active:
            self.get_logger().info("Goal is no longer active")
            return True

        if goal_handle.is_cancel_requested:
            self.get_logger().info("Cancel requested, stopping execution")
            if goal_handle.request.__class__.__name__ == 'FindBook_Goal':
                result = FindBook.Result()
                result.success = False
                result.message = "FindBook was cancelled"
            else:
                result = PerformInventory.Result()
                result.success = False
                result.message = "Inventory was cancelled"
            goal_handle.canceled()
            return True

        return False


class TestUIIntegration:
    """UI集成测试类"""

    def __init__(self):
        self.ros2_manager = None
        self.server = None
        self.executor = None

    def setup(self):
        """设置测试环境"""
        rclpy.init()

        # 创建服务器
        self.server = TestUIIntegrationServer()

        # 创建ROS2管理器
        self.ros2_manager = Ros2Manager()

        # 创建多线程执行器
        self.executor = MultiThreadedExecutor()
        self.executor.add_node(self.server)

        # 在后台线程中启动执行器
        self.executor_thread = threading.Thread(target=self._spin_executor, daemon=True)
        self.executor_thread.start()

        # 等待服务器启动
        time.sleep(2.0)

        print("=== UI集成测试环境已启动 ===")

    def _spin_executor(self):
        """在后台线程中运行执行器"""
        try:
            self.executor.spin()
        except Exception as e:
            print(f"Executor error: {e}")

    def test_find_book_flow(self):
        """测试找书流程"""
        print("\n=== 测试找书流程 ===")

        # 发送找书任务
        success = self.ros2_manager.send_find_book_goal("test_book_ui_001")
        if not success:
            print("❌ 发送找书任务失败")
            return False

        print("✅ 找书任务已发送")

        # 等待5秒后取消
        time.sleep(5.0)
        print("尝试取消找书任务...")

        cancel_success = self.ros2_manager.cancel_current_goal()
        if cancel_success:
            print("✅ 取消请求已发送")
        else:
            print("❌ 取消请求发送失败")

        # 等待任务完成
        time.sleep(3.0)
        return True

    def test_inventory_flow(self):
        """测试盘点流程"""
        print("\n=== 测试盘点流程 ===")

        # 注意：当前Ros2Manager没有实现inventory action client
        # 这里只是演示如何扩展
        print("⚠️  当前Ros2Manager未实现PerformInventory action client")
        print("需要扩展Ros2Manager以支持盘点功能")

        return True

    def test_concurrent_operations(self):
        """测试并发操作"""
        print("\n=== 测试并发操作 ===")

        # 发送找书任务
        success = self.ros2_manager.send_find_book_goal("concurrent_test_book")
        if success:
            print("✅ 并发找书任务已发送")

        # 立即尝试取消
        time.sleep(1.0)
        cancel_success = self.ros2_manager.cancel_current_goal()
        if cancel_success:
            print("✅ 并发取消请求已发送")

        time.sleep(2.0)
        return True

    def cleanup(self):
        """清理测试环境"""
        print("\n=== 清理测试环境 ===")

        if self.ros2_manager:
            self.ros2_manager.shutdown()

        if self.server:
            self.server.destroy_node()

        rclpy.shutdown()
        print("✅ 测试环境已清理")


def main():
    """主测试函数"""
    test = TestUIIntegration()

    try:
        # 设置测试环境
        test.setup()

        # 运行测试
        test.test_find_book_flow()
        test.test_inventory_flow()
        test.test_concurrent_operations()

        print("\n=== 所有测试完成 ===")

    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
    finally:
        test.cleanup()


if __name__ == "__main__":
    main()