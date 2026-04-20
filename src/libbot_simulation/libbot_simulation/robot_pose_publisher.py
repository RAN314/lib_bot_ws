#!/usr/bin/env python3
"""
机器人位姿发布器
从Gazebo仿真中获取机器人实际位置并发布到/robot_pose话题
供RFID传感器使用
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose, Point, Quaternion
from gazebo_msgs.srv import GetEntityState
from std_msgs.msg import Header
import time
import math

class RobotPosePublisher(Node):
    def __init__(self):
        super().__init__('robot_pose_publisher')

        # 创建位姿发布器
        self.pose_publisher = self.create_publisher(Pose, '/robot_pose', 10)

        # 创建Gazebo服务客户端 - 尝试多个可能的服务路径
        gazebo_services = [
            '/gazebo/get_entity_state',
            '/gazebo.gazebo/get_entity_state',
            '/world/empty/get_entity_state'
        ]

        self.gazebo_client = None
        for service_name in gazebo_services:
            try:
                client = self.create_client(GetEntityState, service_name)
                self.get_logger().info(f'尝试连接Gazebo服务: {service_name}')

                # 等待服务可用（最多5秒）
                if client.wait_for_service(timeout_sec=5.0):
                    self.gazebo_client = client
                    self.get_logger().info(f'成功连接到Gazebo服务: {service_name}')
                    break
                else:
                    self.get_logger().warn(f'无法连接到服务: {service_name}')
            except Exception as e:
                self.get_logger().warn(f'连接服务 {service_name} 失败: {e}')
                continue

        if self.gazebo_client is None:
            self.get_logger().error('无法连接到任何Gazebo服务，将使用默认位姿')
            # 创建虚拟客户端避免后续错误
            self.gazebo_client = self.create_client(GetEntityState, '/dummy_service')
            # 设置默认位姿
            self.default_pose = Pose()
            self.default_pose.position.x = 0.0
            self.default_pose.position.y = 0.0
            self.default_pose.position.z = 0.0
            self.default_pose.orientation.w = 1.0

        # 创建定时器，定期获取机器人位姿
        self.timer = self.create_timer(0.1, self.publish_robot_pose)  # 10Hz

        self.get_logger().info('机器人位姿发布器启动完成')

    def publish_robot_pose(self):
        try:
            # 检查是否连接到了有效的Gazebo服务
            if self.gazebo_client.service_name == '/dummy_service':
                # 使用默认位姿
                self.pose_publisher.publish(self.default_pose)
                return

            # 创建请求
            request = GetEntityState.Request()
            request.name = 'turtlebot3_waffle_pi'  # 机器人实体名称

            # 异步调用服务
            future = self.gazebo_client.call_async(request)

            # 使用spin_once等待结果（非阻塞）
            rclpy.spin_once(self, timeout_sec=0.05)

            if future.done():
                result = future.result()

                if result and result.success:
                    # 创建位姿消息
                    pose = Pose()
                    pose.position = result.state.pose.position
                    pose.orientation = result.state.pose.orientation

                    # 发布位姿
                    self.pose_publisher.publish(pose)
                else:
                    self.get_logger().debug('获取机器人位姿失败，使用默认位姿')
                    self.pose_publisher.publish(self.default_pose)
            else:
                # 服务调用超时，使用默认位姿
                self.pose_publisher.publish(self.default_pose)

        except Exception as e:
            self.get_logger().debug(f'获取位姿时出错，使用默认位姿: {e}')
            try:
                self.pose_publisher.publish(self.default_pose)
            except:
                pass

def main(args=None):
    rclpy.init(args=args)

    try:
        node = RobotPosePublisher()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if 'node' in locals():
            node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()