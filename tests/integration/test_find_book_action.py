#!/usr/bin/env python3
"""
FindBook Action 测试
基于 action_cancel_example 的正确实现模式
测试找书任务的执行和取消功能
"""

import rclpy
from rclpy.action import ActionClient, ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
import time
import threading

from libbot_msgs.action import FindBook


class TestFindBookActionClient(Node):
    """FindBook Action 客户端测试"""

    def __init__(self):
        super().__init__("test_find_book_client")
        self._action_client = ActionClient(self, FindBook, "/find_book")
        self._goal_handle = None
        self._cancel_requested = False

        # 创建定时器来自动测试取消功能
        self.create_timer(2.0, self._send_goal_timer_callback)

    def send_find_book_goal(self, book_id="test_book_001"):
        """发送找书任务"""
        if not self._action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error("FindBook action server not available")
            return False

        goal_msg = FindBook.Goal()
        goal_msg.book_id = book_id
        goal_msg.guide_patron = False

        self.get_logger().info(f"Sending FindBook goal for book: {book_id}")

        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self._feedback_callback
        )
        self._send_goal_future.add_done_callback(self._goal_response_callback)
        return True

    def _send_goal_timer_callback(self):
        """定时器回调 - 发送goal"""
        if self._goal_handle is None:
            self.send_find_book_goal()
            # 5秒后尝试取消
            self.create_timer(5.0, self._cancel_goal_timer_callback)

    def _cancel_goal_timer_callback(self):
        """定时器回调 - 取消goal"""
        if self._goal_handle and not self._cancel_requested:
            self.get_logger().info("Attempting to cancel goal...")
            self.cancel_goal()
            self._cancel_requested = True

    def cancel_goal(self):
        """取消当前goal"""
        if self._goal_handle:
            self.get_logger().info("Sending cancel request...")
            cancel_future = self._goal_handle.cancel_goal_async()
            cancel_future.add_done_callback(self._cancel_done_callback)
            return True
        else:
            self.get_logger().warn("No active goal to cancel")
            return False

    def _goal_response_callback(self, future):
        """Goal响应回调"""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error("Goal rejected by server")
            return

        self.get_logger().info("Goal accepted by server")
        self._goal_handle = goal_handle

        # 获取结果
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self._get_result_callback)

    def _feedback_callback(self, feedback_msg):
        """反馈回调"""
        feedback = feedback_msg.feedback
        self.get_logger().info(
            f"Feedback: status={feedback.status}, progress={feedback.progress:.1f}%, "
            f"distance={feedback.distance_to_goal:.2f}m, signal={feedback.signal_strength:.2f}"
        )

    def _get_result_callback(self, future):
        """结果回调"""
        result = future.result().result
        status = future.result().status

        if status == 2:  # GoalStatus.STATUS_CANCELED
            self.get_logger().info(f"Goal was cancelled: {result.message}")
        elif status == 4:  # GoalStatus.STATUS_SUCCEEDED
            self.get_logger().info(f"Goal succeeded: {result.message}")
        else:
            self.get_logger().info(f"Goal finished with status {status}: {result.message}")

        self._goal_handle = None

    def _cancel_done_callback(self, future):
        """取消完成回调"""
        cancel_response = future.result()
        if cancel_response.goals_canceling:
            self.get_logger().info("Cancel request accepted")
        else:
            self.get_logger().warn("Cancel request rejected")


class TestFindBookActionServer(Node):
    """FindBook Action 服务器测试"""

    def __init__(self):
        super().__init__("test_find_book_server")

        # 使用可重入回调组支持并行执行
        self.callback_group = ReentrantCallbackGroup()

        self._action_server = ActionServer(
            self,
            FindBook,
            "/find_book",
            execute_callback=self._execute_callback,
            callback_group=self.callback_group,
            goal_callback=self._goal_callback,
            cancel_callback=self._cancel_callback
        )

        self.get_logger().info("TestFindBookActionServer started")

    def _goal_callback(self, goal_request):
        """Goal请求回调"""
        self.get_logger().info(f"Received goal request for book: {goal_request.book_id}")
        return GoalResponse.ACCEPT

    def _cancel_callback(self, goal_handle):
        """取消请求回调"""
        self.get_logger().info("Cancel request received")
        return CancelResponse.ACCEPT

    async def _execute_callback(self, goal_handle):
        """执行回调"""
        self.get_logger().info("Starting goal execution...")

        book_id = goal_handle.request.book_id

        # 创建反馈消息
        feedback = FindBook.Feedback()

        try:
            # 阶段1: 导航 (0-40%)
            self.get_logger().info("Phase 1: Navigation")
            for i in range(1, 21):  # 20 steps
                if self._check_cancel_request(goal_handle):
                    return FindBook.Result()

                # 更新反馈
                feedback.status = "navigating"
                feedback.progress = i * 2.0  # 0-40%
                feedback.distance_to_goal = max(0.0, 10.0 - i * 0.5)
                feedback.current_pose.position.x = i * 0.2
                feedback.current_pose.position.y = i * 0.1
                feedback.signal_strength = 0.0
                feedback.estimated_remaining = (20 - i) * 0.5

                goal_handle.publish_feedback(feedback)
                self.get_logger().info(f"Navigation: {feedback.progress:.1f}%")

                # 使用spin_once而不是sleep，确保可以处理取消请求
                rclpy.spin_once(self, timeout_sec=0.5)

            # 阶段2: 扫描 (40-80%)
            self.get_logger().info("Phase 2: Scanning")
            for i in range(1, 21):  # 20 steps
                if self._check_cancel_request(goal_handle):
                    return FindBook.Result()

                feedback.status = "scanning"
                feedback.progress = 40.0 + i * 2.0  # 40-80%
                feedback.distance_to_goal = 0.0
                feedback.signal_strength = 0.8 if i > 15 else 0.0
                feedback.books_detected = [book_id] if i > 15 else []
                feedback.estimated_remaining = (20 - i) * 0.2

                goal_handle.publish_feedback(feedback)
                self.get_logger().info(f"Scanning: {feedback.progress:.1f}%")

                rclpy.spin_once(self, timeout_sec=0.3)

            # 阶段3: 确认 (80-100%)
            self.get_logger().info("Phase 3: Confirmation")
            for i in range(1, 21):  # 20 steps
                if self._check_cancel_request(goal_handle):
                    return FindBook.Result()

                feedback.status = "approaching"
                feedback.progress = 80.0 + i * 1.0  # 80-100%
                feedback.estimated_remaining = (20 - i) * 0.1

                goal_handle.publish_feedback(feedback)
                self.get_logger().info(f"Confirmation: {feedback.progress:.1f}%")

                rclpy.spin_once(self, timeout_sec=0.2)

            # 完成
            goal_handle.succeed()

            result = FindBook.Result()
            result.success = True
            result.message = f"Successfully found book {book_id}"
            result.search_time = 20.0
            result.navigation_attempts = 1
            result.scan_attempts = 20

            self.get_logger().info("Goal completed successfully")
            return result

        except Exception as e:
            self.get_logger().error(f"Error during execution: {e}")
            goal_handle.abort()
            return FindBook.Result()

    def _check_cancel_request(self, goal_handle):
        """检查取消请求"""
        if not goal_handle.is_active:
            self.get_logger().info("Goal is no longer active")
            return True

        if goal_handle.is_cancel_requested:
            self.get_logger().info("Cancel requested, stopping execution")
            result = FindBook.Result()
            result.success = False
            result.message = "Goal was cancelled"
            result.search_time = 0.0
            goal_handle.canceled()
            return True

        return False


def main(args=None):
    rclpy.init(args=args)

    # 创建服务器和客户端
    server = TestFindBookActionServer()
    client = TestFindBookActionClient()

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