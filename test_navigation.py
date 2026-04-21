#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import time

def test_navigation():
    rclpy.init()
    node = Node('test_navigation')

    # 创建发布者
    goal_publisher = node.create_publisher(PoseStamped, '/goal_pose', 10)

    # 等待连接建立
    time.sleep(2.0)

    # 创建导航目标消息
    goal_msg = PoseStamped()
    goal_msg.header.frame_id = 'map'
    goal_msg.header.stamp = node.get_clock().now().to_msg()
    goal_msg.pose.position.x = 0.0
    goal_msg.pose.position.y = 0.0
    goal_msg.pose.position.z = 0.0
    goal_msg.pose.orientation.w = 1.0  # 无旋转

    # 发布导航目标
    print("🚀 发布导航目标到原点 (0.0, 0.0)")
    goal_publisher.publish(goal_msg)
    print("✅ 导航目标已发布")

    # 保持节点运行一段时间
    time.sleep(3.0)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    test_navigation()
