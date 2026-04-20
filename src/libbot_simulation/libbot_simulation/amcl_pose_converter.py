#!/usr/bin/env python3
"""
AMCL位姿转换器
将AMCL的PoseWithCovarianceStamped消息转换为简单的Pose消息
用于与现有RFID传感器和其他系统兼容
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose, PoseWithCovarianceStamped


class AMCLPoseConverter(Node):
    """AMCL位姿转换器节点"""

    def __init__(self):
        super().__init__('amcl_pose_converter')

        # 订阅AMCL定位结果
        self.amcl_subscription = self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self.amcl_pose_callback,
            10
        )

        # 发布转换后的位姿
        self.pose_publisher = self.create_publisher(
            Pose,
            '/robot_pose',
            10
        )

        self.get_logger().info("AMCL位姿转换器启动完成")
        self.get_logger().info("订阅: /amcl_pose -> 发布: /robot_pose")

    def amcl_pose_callback(self, msg: PoseWithCovarianceStamped):
        """AMCL位姿回调 - 转换为简单Pose并重新发布"""
        # 创建新的Pose消息
        pose_msg = Pose()

        # 复制位姿数据
        pose_msg.position = msg.pose.pose.position
        pose_msg.orientation = msg.pose.pose.orientation

        # 发布转换后的位姿
        self.pose_publisher.publish(pose_msg)


def main(args=None):
    rclpy.init(args=args)

    try:
        node = AMCLPoseConverter()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if 'node' in locals():
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()