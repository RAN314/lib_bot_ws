#!/usr/bin/env python3

import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from test_action_interfaces.action import TestCancel


class TestCancelServer(Node):
    def __init__(self):
        super().__init__("test_cancel_server")
        self.get_logger().info("Initializing TestCancelServer")
        self._action_server = ActionServer(
            self,
            TestCancel,
            "test_cancel",
            self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=ReentrantCallbackGroup(),
        )
        self.get_logger().info(
            "Action server 'test_cancel' started and ready to accept goals"
        )

    def goal_callback(self, goal_request):
        self.get_logger().info(
            f"Received goal request with duration: {goal_request.duration}"
        )
        self.get_logger().info("Accepting goal request")
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info("Received cancel request for active goal")
        self.get_logger().info("Accepting cancel request")
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        self.get_logger().info("Starting goal execution")
        feedback_msg = TestCancel.Feedback()
        result = TestCancel.Result()

        duration = 20  # 固定执行20步
        self.get_logger().info(f"Goal will execute {duration} steps")

        for i in range(duration):
            if goal_handle.is_cancel_requested:
                self.get_logger().warn("Goal execution was canceled by client")
                goal_handle.canceled()
                result.message = "Goal was canceled"
                self.get_logger().info("Returning cancel result to client")
                return result

            feedback_msg.progress = f"Step {i + 1}/{duration}"
            self.get_logger().info(f"Publishing feedback: {feedback_msg.progress}")
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().debug(f"Sleeping for 1 second (step {i + 1})")
            rclpy.spin_once(self, timeout_sec=1.0)

        self.get_logger().info("Goal execution completed successfully")
        goal_handle.succeed()
        result.message = "Goal succeeded"
        self.get_logger().info("Goal execution completed successfully")
        self.get_logger().info("Returning success result to client")
        return result


def main(args=None):
    rclpy.init(args=args)
    print("ROS2 initialized")

    test_cancel_server = TestCancelServer()
    print("Server node created, starting spin...")

    try:
        rclpy.spin(test_cancel_server)
    except KeyboardInterrupt:
        print("Received keyboard interrupt, shutting down...")

    test_cancel_server.destroy_node()
    rclpy.shutdown()
    print("Shutdown complete")


if __name__ == "__main__":
    main()
