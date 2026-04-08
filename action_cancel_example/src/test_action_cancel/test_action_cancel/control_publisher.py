#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool


class ControlPublisher(Node):
    def __init__(self):
        super().__init__("control_publisher")
        self.publisher = self.create_publisher(Bool, "cancel_control", 10)
        self.timer = self.create_timer(10.0, self.publish_control)
        self.state = True  # 开始时为 True (停止运行)
        self.get_logger().info(
            "Control publisher started. Publishing True (stop) initially, then False (run) every 10 seconds."
        )

    def publish_control(self):
        msg = Bool()
        msg.data = self.state
        self.publisher.publish(msg)
        self.get_logger().info(
            f"Published control: {self.state} (run_goals={not self.state})"
        )

        # 切换状态用于演示
        self.state = not self.state
        self.get_logger().info(f"Next will be {self.state}")


def main(args=None):
    rclpy.init(args=args)
    node = ControlPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
