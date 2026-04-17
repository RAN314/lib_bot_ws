#!/usr/bin/env python3
"""
鲁棒机器人位姿发布器
多种方式获取机器人位姿，确保RFID传感器始终有数据可用
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose, Point, Quaternion
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseWithCovarianceStamped
from gazebo_msgs.srv import GetEntityState
import time
import math


class RobustPosePublisher(Node):
    """鲁棒位姿发布器 - 多源位姿获取"""

    def __init__(self):
        super().__init__('robust_pose_publisher')

        # 创建位姿发布器
        self.pose_publisher = self.create_publisher(Pose, '/robot_pose', 10)

        # 当前位姿状态
        self.current_pose = self._create_default_pose()
        self.pose_source = "default"
        self.last_update_time = time.time()

        # 订阅多种位姿源
        self._setup_pose_subscriptions()

        # 尝试连接Gazebo服务
        self._setup_gazebo_client()

        # 创建定时器，确保持续发布位姿
        self.timer = self.create_timer(0.1, self._publish_current_pose)  # 10Hz

        # 创建定时器，定期检查位姿源
        self.status_timer = self.create_timer(5.0, self._check_pose_sources)

        self.get_logger().info("鲁棒位姿发布器启动完成")
        self.get_logger().info(f"当前位姿源: {self.pose_source}")

    def _create_default_pose(self):
        """创建默认位姿"""
        pose = Pose()
        pose.position = Point(x=0.0, y=0.0, z=0.0)
        pose.orientation = Quaternion(w=1.0, x=0.0, y=0.0, z=0.0)
        return pose

    def _setup_pose_subscriptions(self):
        """设置多种位姿源订阅"""

        # 1. 订阅里程计数据
        try:
            self.odom_subscription = self.create_subscription(
                Odometry,
                '/odom',
                self._odom_callback,
                10
            )
            self.get_logger().info("已订阅 /odom 话题")
        except Exception as e:
            self.get_logger().warn(f"订阅 /odom 失败: {e}")

        # 2. 订阅AMCL定位
        try:
            self.amcl_subscription = self.create_subscription(
                PoseWithCovarianceStamped,
                '/amcl_pose',
                self._amcl_callback,
                10
            )
            self.get_logger().info("已订阅 /amcl_pose 话题")
        except Exception as e:
            self.get_logger().warn(f"订阅 /amcl_pose 失败: {e}")

        # 3. 订阅TF变换（如果有）
        # 注意：这里简化处理，实际可能需要使用tf2_ros

    def _setup_gazebo_client(self):
        """设置Gazebo服务客户端"""
        try:
            self.gazebo_client = self.create_client(GetEntityState, '/gazebo/get_entity_state')
            self.get_logger().info("已创建Gazebo服务客户端")
        except Exception as e:
            self.get_logger().warn(f"创建Gazebo客户端失败: {e}")
            self.gazebo_client = None

    def _odom_callback(self, msg: Odometry):
        """里程计回调 - 最高优先级"""
        self.current_pose.position = msg.pose.pose.position
        self.current_pose.orientation = msg.pose.pose.orientation
        self.pose_source = "odom"
        self.last_update_time = time.time()

    def _amcl_callback(self, msg: PoseWithCovarianceStamped):
        """AMCL回调 - 第二优先级"""
        self.current_pose.position = msg.pose.pose.position
        self.current_pose.orientation = msg.pose.pose.orientation
        if self.pose_source != "odom":  # 只有当odom不可用时才使用AMCL
            self.pose_source = "amcl"
            self.last_update_time = time.time()

    def _publish_current_pose(self):
        """发布当前位姿"""
        try:
            self.pose_publisher.publish(self.current_pose)

            # 每秒更新一次日志
            if int(time.time()) % 10 == 0:
                self.get_logger().debug(f"发布位姿 - 源: {self.pose_source}, "
                                      f"位置: ({self.current_pose.position.x:.2f}, "
                                      f"{self.current_pose.position.y:.2f})")

        except Exception as e:
            self.get_logger().error(f"发布位姿失败: {e}")

    def _check_pose_sources(self):
        """定期检查位姿源状态"""
        current_time = time.time()
        time_since_update = current_time - self.last_update_time

        if time_since_update > 2.0:  # 2秒没有更新
            if self.pose_source != "default":
                self.get_logger().warn(f"位姿源 {self.pose_source} 超时，切换到默认位姿")
                self.pose_source = "default"
                self.current_pose = self._create_default_pose()

        # 尝试重新连接Gazebo服务
        if self.gazebo_client and not self.gazebo_client.service_is_ready():
            self.get_logger().debug("尝试重新连接Gazebo服务...")


def main(args=None):
    rclpy.init(args=args)

    try:
        node = RobustPosePublisher()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if 'node' in locals():
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()