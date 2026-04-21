#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
import time

class NavigateToPoseClient(Node):
    def __init__(self):
        super().__init__('navigate_to_pose_client')
        self._action_client = ActionClient(
            self,
            NavigateToPose,
            '/navigate_to_pose'
        )

    def send_goal(self, x, y, z=0.0, w=1.0):
        """发送导航目标点

        Args:
            x: 目标位置x坐标
            y: 目标位置y坐标
            z: 目标姿态四元数z分量 (默认0.0)
            w: 目标姿态四元数w分量 (默认1.0，表示无旋转)
        """
        goal_msg = NavigateToPose.Goal()

        # 设置目标位置
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.position.z = 0.0

        # 设置目标姿态（四元数）
        goal_msg.pose.pose.orientation.x = 0.0
        goal_msg.pose.pose.orientation.y = 0.0
        goal_msg.pose.pose.orientation.z = z
        goal_msg.pose.pose.orientation.w = w

        # 等待action服务器可用
        self.get_logger().info('等待NavigateToPose action服务器...')
        if not self._action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('NavigateToPose action服务器不可用')
            return False

        # 发送目标
        self.get_logger().info(f'发送导航目标: x={x}, y={y}')
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        # 添加完成回调
        self._send_goal_future.add_done_callback(self.goal_response_callback)
        return True

    def goal_response_callback(self, future):
        """目标响应回调"""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('导航目标被拒绝')
            return

        self.get_logger().info('导航目标被接受')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.result_callback)

    def feedback_callback(self, feedback_msg):
        """导航反馈回调"""
        feedback = feedback_msg.feedback
        self.get_logger().info(f'导航进度: {feedback.distance_remaining:.2f}米')

    def result_callback(self, future):
        """导航结果回调"""
        result = future.result().result
        status = future.result().status

        if status == 0:  # 成功
            self.get_logger().info('导航成功完成!')
        elif status == 1:  # 取消
            self.get_logger().warn('导航被取消')
        elif status == 2:  # 被抢占
            self.get_logger().warn('导航被抢占')
        else:  # 失败
            self.get_logger().error(f'导航失败，状态码: {status}')

def main(args=None):
    rclpy.init(args=args)

    navigate_client = NavigateToPoseClient()

    try:
        # 示例：导航到坐标 (2.0, 1.0)
        navigate_client.send_goal(2.0, 1.0)

        # 保持节点运行
        while rclpy.ok():
            rclpy.spin_once(navigate_client, timeout_sec=0.1)

    except KeyboardInterrupt:
        navigate_client.get_logger().info('用户中断')
    finally:
        navigate_client.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()