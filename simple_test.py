#!/usr/bin/env python3
"""
简单测试脚本，验证取消功能
"""

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
import time

from libbot_msgs.action import FindBook


class SimpleTestClient(Node):
    def __init__(self):
        super().__init__('simple_test_client')
        self._action_client = ActionClient(self, FindBook, '/find_book')
        self._goal_handle = None

    def send_goal_and_test_cancel(self):
        print("📤 发送找书任务...")

        if not self._action_client.wait_for_server(timeout_sec=5.0):
            print("❌ 服务器不可用")
            return

        goal_msg = FindBook.Goal()
        goal_msg.book_id = "test_book_001"
        goal_msg.guide_patron = False

        # 发送goal
        future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        try:
            goal_handle = future.result()
            if not goal_handle.accepted:
                print("❌ Goal被拒绝")
                return

            print("✅ Goal被接受")
            self._goal_handle = goal_handle

            # 立即尝试取消
            print("🛑 尝试取消goal...")
            self.cancel_current_goal()

            # 设置结果回调
            result_future = goal_handle.get_result_async()
            result_future.add_done_callback(self.result_callback)

        except Exception as e:
            print(f"❌ 错误: {e}")

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        print(f"📊 反馈: {feedback.progress:.1f}%")

    def result_callback(self, future):
        try:
            result = future.result().result
            status = future.result().status

            if status == 2:  # CANCELLED
                print(f"⏹️ Goal被取消: {result.message}")
            elif status == 4:  # SUCCEEDED
                print(f"✅ Goal成功: {result.message}")
            else:
                print(f"❓ Goal状态: {status}")

            self._goal_handle = None

            # 测试重新发送goal
            print("\n🔄 测试重新发送goal...")
            time.sleep(1)
            self.send_goal_again()

        except Exception as e:
            print(f"❌ 结果错误: {e}")

    def cancel_current_goal(self):
        if self._goal_handle:
            cancel_future = self._goal_handle.cancel_goal_async()
            cancel_future.add_done_callback(self.cancel_callback)
        else:
            print("⚠️ 没有活跃的goal")

    def cancel_callback(self, future):
        try:
            cancel_response = future.result()
            if hasattr(cancel_response, 'goals_canceling') and cancel_response.goals_canceling:
                print("✅ 取消请求被接受")
            else:
                print("❌ 取消请求被拒绝")
        except Exception as e:
            print(f"❌ 取消错误: {e}")

    def send_goal_again(self):
        print("📤 重新发送找书任务...")

        goal_msg = FindBook.Goal()
        goal_msg.book_id = "test_book_002"
        goal_msg.guide_patron = False

        future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        future.add_done_callback(self.goal_response_again_callback)

    def goal_response_again_callback(self, future):
        try:
            goal_handle = future.result()
            if not goal_handle.accepted:
                print("❌ 第二个Goal被拒绝")
                return

            print("✅ 第二个Goal被接受！修复成功！")
            self._goal_handle = goal_handle

            # 设置结果回调
            result_future = goal_handle.get_result_async()
            result_future.add_done_callback(self.result_again_callback)

        except Exception as e:
            print(f"❌ 错误: {e}")

    def result_again_callback(self, future):
        try:
            result = future.result().result
            status = future.result().status

            if status == 4:  # SUCCEEDED
                print(f"✅ 第二个Goal成功完成: {result.message}")
                print("🎉 测试成功！服务器可以正确处理取消后重新发送goal！")
            else:
                print(f"❓ 第二个Goal状态: {status}")

        except Exception as e:
            print(f"❌ 结果错误: {e}")


def main():
    print("=== 简单取消功能测试 ===")
    print("测试取消后重新发送goal的功能")
    print()

    rclpy.init()
    client = SimpleTestClient()

    try:
        client.send_goal_and_test_cancel()

        # 运行ROS2事件循环
        try:
            rclpy.spin(client)
        except KeyboardInterrupt:
            print("\n测试被中断")

    finally:
        client.destroy_node()
        rclpy.shutdown()
        print("\n✅ 测试完成")


if __name__ == '__main__':
    main()