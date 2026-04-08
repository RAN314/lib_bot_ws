#!/usr/bin/env python3

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from std_msgs.msg import Bool

from test_action_interfaces.action import TestCancel


class TestCancelClient(Node):
    def __init__(self):
        super().__init__("test_cancel_client")
        self._action_client = ActionClient(self, TestCancel, "test_cancel")
        self._should_continue = True  # 默认停止运行 (True=stop, False=run)
        self._goal_handle = None
        self._sending_goal = False  # 防止重复发送goal

        # 订阅控制 topic
        self._control_sub = self.create_subscription(
            Bool, "cancel_control", self.control_callback, 10
        )
        self.get_logger().info(
            "Subscribed to /cancel_control topic (False=run goals, True=cancel)"
        )

    def send_goal(self):
        self.get_logger().info("Waiting for action server...")
        self._action_client.wait_for_server()

        goal_msg = TestCancel.Goal()
        goal_msg.duration = 20  # 固定20步

        self.get_logger().info("Sending goal with 20 steps")

        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback
        )
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def control_callback(self, msg):
        control_run = not msg.data  # False = run, True = cancel
        self._should_continue = not control_run  # True = stop, False = run
        self.get_logger().info(
            f"Control message received: {msg.data} (run_goals={control_run}, _should_continue={self._should_continue})"
        )

        if control_run and not self._goal_handle and not self._sending_goal:
            # 收到 false 且没有活跃 goal，开始发送 goal
            self._sending_goal = True
            self.send_goal()
        elif not control_run and self._goal_handle:
            # 收到 true 且有活跃 goal，取消
            self.cancel_goal()

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error("Goal rejected")
            self._sending_goal = False
            return

        self.get_logger().info("Goal accepted")
        self._goal_handle = goal_handle
        self._sending_goal = False

        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def cancel_goal(self):
        if self._goal_handle:
            self.get_logger().info("Sending cancel request...")
            cancel_future = self._goal_handle.cancel_goal_async()
            cancel_future.add_done_callback(self.cancel_done_callback)
        else:
            self.get_logger().warn("No active goal to cancel")

    def cancel_done_callback(self, future):
        cancel_response = future.result()
        if len(cancel_response.goals_canceling) > 0:
            self.get_logger().info("Cancel request accepted")
        else:
            self.get_logger().info("Cancel request rejected")

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f"Received feedback: {feedback.progress}")

    def get_result_callback(self, future):
        self.get_logger().info("get_result_callback called")
        result = future.result().result
        self.get_logger().info(f"Result: {result.message}")
        self._goal_handle = None  # 重置 goal handle
        self._sending_goal = False

        # 如果当前控制状态允许，继续发送新 goal
        self.get_logger().info(f"_should_continue = {self._should_continue}")
        if not self._should_continue:  # _should_continue False = run goals
            self.get_logger().info("Goal completed, sending next goal...")
            self.send_goal()
        else:
            self.get_logger().info(
                "Goal completed, waiting for control signal to continue"
            )


def main(args=None):
    rclpy.init(args=args)

    client = TestCancelClient()

    try:
        rclpy.spin(client)
    except KeyboardInterrupt:
        pass

    client.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
