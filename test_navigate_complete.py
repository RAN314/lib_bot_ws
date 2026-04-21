#!/usr/bin/env python3
"""
测试NavigateToPose Action的完整生命周期
"""

import sys
import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose

def test_navigate_complete():
    """测试完整的NavigateToPose Action生命周期"""
    print("🚀 测试NavigateToPose Action完整生命周期")
    print("=" * 50)

    rclpy.init()
    node = Node('test_navigate_complete')

    # 创建Action客户端
    client = ActionClient(node, NavigateToPose, '/navigate_to_pose')

    print("等待NavigateToPose Action服务器...")
    if not client.wait_for_server(timeout_sec=10.0):
        print("❌ NavigateToPose Action服务器不可用")
        node.destroy_node()
        rclpy.shutdown()
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

    print("🚀 发送导航目标到原点 (0.0, 0.0)")

    # 用于跟踪状态的变量
    goal_accepted = False
    feedback_received = False
    result_received = False
    final_status = None

    def feedback_callback(feedback):
        nonlocal feedback_received
        feedback_received = True
        fb = feedback.feedback
        print(f"📊 收到反馈: 剩余距离={fb.distance_remaining:.2f}米")

    def result_callback(future):
        nonlocal result_received, final_status
        result_received = True
        try:
            result = future.result()
            final_status = result.status
            print(f"🎯 收到结果: 状态={final_status}")

            if final_status == 0:
                print("✅ 导航成功完成")
            elif final_status == 1:
                print("⏹️ 导航被取消")
            elif final_status == 2:
                print("🔄 导航被抢占")
            else:
                print(f"❌ 导航失败，状态码: {final_status}")

        except Exception as e:
            print(f"❌ 获取结果时出错: {e}")

    def goal_response_callback(future):
        nonlocal goal_accepted
        try:
            goal_handle = future.result()
            if goal_handle.accepted:
                goal_accepted = True
                print("✅ 导航目标被接受")

                # 获取结果
                result_future = goal_handle.get_result_async()
                result_future.add_done_callback(result_callback)
            else:
                print("❌ 导航目标被拒绝")
        except Exception as e:
            print(f"❌ 目标响应出错: {e}")

    # 发送目标
    future = client.send_goal_async(
        goal,
        feedback_callback=feedback_callback
    )
    future.add_done_callback(goal_response_callback)

    # 等待结果，最多30秒
    start_time = time.time()
    timeout = 30.0

    print("\n⏳ 等待导航完成...")

    while rclpy.ok() and not result_received:
        rclpy.spin_once(node, timeout_sec=0.1)

        # 检查超时
        if time.time() - start_time > timeout:
            print(f"❌ 导航超时（{timeout}秒）")
            break

    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"  目标接受: {'✅' if goal_accepted else '❌'}")
    print(f"  反馈接收: {'✅' if feedback_received else '❌'}")
    print(f"  结果接收: {'✅' if result_received else '❌'}")
    print(f"  最终状态: {final_status}")

    success = goal_accepted and result_received and final_status == 0
    print(f"  总体结果: {'✅ 成功' if success else '❌ 失败'}")

    # 清理
    node.destroy_node()
    rclpy.shutdown()

    return success

if __name__ == "__main__":
    success = test_navigate_complete()
    sys.exit(0 if success else 1)