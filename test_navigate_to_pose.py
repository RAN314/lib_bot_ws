#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
import time

def test_navigate_to_pose():
    rclpy.init()
    node = Node('test_navigate_to_pose')

    # 创建Action客户端
    client = ActionClient(node, NavigateToPose, '/navigate_to_pose')

    # 等待服务器
    print("等待NavigateToPose Action服务器...")
    if not client.wait_for_server(timeout_sec=10.0):
        print("❌ NavigateToPose Action服务器不可用")
        return False

    print("✅ NavigateToPose Action服务器已连接")

    # 创建目标
    goal = NavigateToPose.Goal()
    goal.pose.header.frame_id = 'map'
    goal.pose.header.stamp = node.get_clock().now().to_msg()
    goal.pose.pose.position.x = 0.0
    goal.pose.pose.position.y = 0.0
    goal.pose.pose.position.z = 0.0
    goal.pose.pose.orientation.w = 1.0

    # 发送目标
    print("🚀 发送导航目标到原点 (0.0, 0.0)")
    future = client.send_goal_async(goal)

    # 等待目标被接受
    rclpy.spin_until_future_complete(node, future, timeout_sec=5.0)

    if future.done():
        goal_handle = future.result()
        if goal_handle.accepted:
            print("✅ 导航目标被接受")

            # 等待结果
            result_future = goal_handle.get_result_async()
            rclpy.spin_until_future_complete(node, result_future, timeout_sec=30.0)

            if result_future.done():
                result = result_future.result()
                print(f"✅ 导航完成，状态: {result.status}")
                return True
            else:
                print("❌ 导航超时")
                return False
        else:
            print("❌ 导航目标被拒绝")
            return False
    else:
        print("❌ 发送目标超时")
        return False

    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    test_navigate_to_pose()
