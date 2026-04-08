#!/usr/bin/env python3
"""
PerformInventory Action 测试
基于 action_cancel_example 的正确实现模式
测试盘点任务的执行和取消功能
"""

import rclpy
from rclpy.action import ActionClient, ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
import time
import json

from libbot_msgs.action import PerformInventory


class TestPerformInventoryActionClient(Node):
    """PerformInventory Action 客户端测试"""

    def __init__(self):
        super().__init__("test_perform_inventory_client")
        self._action_client = ActionClient(self, PerformInventory, "/perform_inventory")
        self._goal_handle = None
        self._cancel_requested = False

        # 创建定时器来自动测试
        self.create_timer(2.0, self._send_goal_timer_callback)

    def send_inventory_goal(self, target_zone="A", update_database=True):
        """发送盘点任务"""
        if not self._action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error("PerformInventory action server not available")
            return False

        goal_msg = PerformInventory.Goal()
        goal_msg.target_zone = target_zone
        goal_msg.update_database = update_database

        self.get_logger().info(f"Sending PerformInventory goal for zone: {target_zone}")

        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self._feedback_callback
        )
        self._send_goal_future.add_done_callback(self._goal_response_callback)
        return True

    def _send_goal_timer_callback(self):
        """定时器回调 - 发送goal"""
        if self._goal_handle is None:
            self.send_inventory_goal()
            # 8秒后尝试取消
            self.create_timer(8.0, self._cancel_goal_timer_callback)

    def _cancel_goal_timer_callback(self):
        """定时器回调 - 取消goal"""
        if self._goal_handle and not self._cancel_requested:
            self.get_logger().info("Attempting to cancel inventory goal...")
            self.cancel_goal()
            self._cancel_requested = True

    def cancel_goal(self):
        """取消当前goal"""
        if self._goal_handle:
            self.get_logger().info("Sending cancel request for inventory...")
            cancel_future = self._goal_handle.cancel_goal_async()
            cancel_future.add_done_callback(self._cancel_done_callback)
            return True
        else:
            self.get_logger().warn("No active inventory goal to cancel")
            return False

    def _goal_response_callback(self, future):
        """Goal响应回调"""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error("Inventory goal rejected by server")
            return

        self.get_logger().info("Inventory goal accepted by server")
        self._goal_handle = goal_handle

        # 获取结果
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self._get_result_callback)

    def _feedback_callback(self, feedback_msg):
        """反馈回调"""
        feedback = feedback_msg.feedback
        self.get_logger().info(
            f"Inventory Feedback: status={feedback.status}, progress={feedback.progress:.1f}%, "
            f"zone={feedback.current_zone}, checked={feedback.books_checked}, "
            f"misplaced={feedback.misplacements_current}"
        )

    def _get_result_callback(self, future):
        """结果回调"""
        result = future.result().result
        status = future.result().status

        if status == 2:  # GoalStatus.STATUS_CANCELED
            self.get_logger().info(f"Inventory goal was cancelled: {result.message}")
        elif status == 4:  # GoalStatus.STATUS_SUCCEEDED
            self.get_logger().info(
                f"Inventory goal succeeded: {result.message}, "
                f"checked={result.books_checked}, misplaced={result.books_misplaced}"
            )
        else:
            self.get_logger().info(f"Inventory goal finished with status {status}: {result.message}")

        self._goal_handle = None

    def _cancel_done_callback(self, future):
        """取消完成回调"""
        cancel_response = future.result()
        if cancel_response.goals_canceling:
            self.get_logger().info("Inventory cancel request accepted")
        else:
            self.get_logger().warn("Inventory cancel request rejected")


class TestPerformInventoryActionServer(Node):
    """PerformInventory Action 服务器测试"""

    def __init__(self):
        super().__init__("test_perform_inventory_server")

        # 使用可重入回调组支持并行执行
        self.callback_group = ReentrantCallbackGroup()

        self._action_server = ActionServer(
            self,
            PerformInventory,
            "/perform_inventory",
            execute_callback=self._execute_callback,
            callback_group=self.callback_group,
            goal_callback=self._goal_callback,
            cancel_callback=self._cancel_callback
        )

        self.get_logger().info("TestPerformInventoryActionServer started")

    def _goal_callback(self, goal_request):
        """Goal请求回调"""
        self.get_logger().info(
            f"Received inventory goal for zone: {goal_request.target_zone}, "
            f"update_db: {goal_request.update_database}"
        )
        return GoalResponse.ACCEPT

    def _cancel_callback(self, goal_handle):
        """取消请求回调"""
        self.get_logger().info("Inventory cancel request received")
        return CancelResponse.ACCEPT

    async def _execute_callback(self, goal_handle):
        """执行回调"""
        self.get_logger().info("Starting inventory execution...")

        target_zone = goal_handle.request.target_zone
        update_database = goal_handle.request.update_database

        # 创建反馈消息
        feedback = PerformInventory.Feedback()

        try:
            total_zones = 5 if target_zone == "all" else 1
            books_per_zone = 50

            # 阶段1: 规划 (0-10%)
            self.get_logger().info("Phase 1: Planning")
            for i in range(1, 11):
                if self._check_cancel_request(goal_handle):
                    return PerformInventory.Result()

                feedback.status = "planning"
                feedback.progress = i * 1.0  # 0-10%
                feedback.current_zone = "planning"
                feedback.books_checked = 0
                feedback.misplacements_current = 0
                feedback.estimated_remaining = total_zones * 10.0

                goal_handle.publish_feedback(feedback)
                self.get_logger().info(f"Planning: {feedback.progress:.1f}%")

                rclpy.spin_once(self, timeout_sec=0.2)

            total_books_checked = 0
            total_misplaced = 0
            misplaced_books = []

            # 阶段2: 扫描区域 (10-90%)
            for zone_idx in range(total_zones):
                current_zone = chr(65 + zone_idx) if target_zone == "all" else target_zone  # A, B, C...

                self.get_logger().info(f"Phase 2: Scanning zone {current_zone}")

                for book_idx in range(books_per_zone):
                    if self._check_cancel_request(goal_handle):
                        return PerformInventory.Result()

                    # 模拟检查每本书
                    feedback.status = "scanning_zone"
                    progress = 10.0 + (zone_idx * books_per_zone + book_idx) * 80.0 / (total_zones * books_per_zone)
                    feedback.progress = progress
                    feedback.current_zone = current_zone
                    feedback.books_checked = total_books_checked + book_idx + 1

                    # 模拟发现错架图书
                    if book_idx % 20 == 0:  # 每20本书有1本错架
                        feedback.misplacements_current += 1
                        total_misplaced += 1
                        misplaced_books.append(f"book_{current_zone}_{book_idx}")

                    feedback.estimated_remaining = (total_zones - zone_idx - 1) * 10.0 + (books_per_zone - book_idx) * 0.2

                    goal_handle.publish_feedback(feedback)

                    if book_idx % 10 == 0:  # 每10本书记录一次日志
                        self.get_logger().info(
                            f"Zone {current_zone}: {feedback.progress:.1f}%, "
                            f"checked={feedback.books_checked}, misplaced={feedback.misplacements_current}"
                        )

                    rclpy.spin_once(self, timeout_sec=0.1)

                total_books_checked += books_per_zone
                feedback.misplacements_current = 0  # 重置当前区域的错架数

            # 阶段3: 验证和完成 (90-100%)
            self.get_logger().info("Phase 3: Verification and completion")
            for i in range(1, 11):
                if self._check_cancel_request(goal_handle):
                    return PerformInventory.Result()

                feedback.status = "verifying"
                feedback.progress = 90.0 + i * 1.0  # 90-100%
                feedback.current_zone = "verification"
                feedback.estimated_remaining = (10 - i) * 0.5

                goal_handle.publish_feedback(feedback)
                self.get_logger().info(f"Verification: {feedback.progress:.1f}%")

                rclpy.spin_once(self, timeout_sec=0.3)

            # 完成
            goal_handle.succeed()

            result = PerformInventory.Result()
            result.success = True
            result.message = f"Inventory completed for zone {target_zone}"
            result.execution_time = total_zones * 10.0
            result.books_checked = total_books_checked
            result.books_misplaced = total_misplaced
            result.books_missing = 0
            result.mismatched_books = json.dumps(misplaced_books)

            self.get_logger().info(
                f"Inventory completed: checked={result.books_checked}, "
                f"misplaced={result.books_misplaced}"
            )
            return result

        except Exception as e:
            self.get_logger().error(f"Error during inventory execution: {e}")
            goal_handle.abort()
            return PerformInventory.Result()

    def _check_cancel_request(self, goal_handle):
        """检查取消请求"""
        if not goal_handle.is_active:
            self.get_logger().info("Inventory goal is no longer active")
            return True

        if goal_handle.is_cancel_requested:
            self.get_logger().info("Inventory cancel requested, stopping execution")
            result = PerformInventory.Result()
            result.success = False
            result.message = "Inventory was cancelled"
            result.execution_time = 0.0
            goal_handle.canceled()
            return True

        return False


def main(args=None):
    rclpy.init(args=args)

    # 创建服务器和客户端
    server = TestPerformInventoryActionServer()
    client = TestPerformInventoryActionClient()

    # 使用多线程执行器
    executor = MultiThreadedExecutor()
    executor.add_node(server)
    executor.add_node(client)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        server.destroy_node()
        client.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()