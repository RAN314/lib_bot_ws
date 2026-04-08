#!/usr/bin/env python3
"""
FindBook Action服务器
完全基于action_cancel_example的正确模式
"""

import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.node import Node

from libbot_msgs.action import FindBook


class TestActionServer(Node):
    """FindBook Action服务器
    完全基于action_cancel_example的正确实现
    """

    def __init__(self):
        super().__init__('test_find_book_server')
        self.get_logger().info('Initializing TestFindBookServer')

        # 创建Action服务器（完全按照action_cancel_example的模式）
        self._action_server = ActionServer(
            self,
            FindBook,
            '/find_book',
            self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=ReentrantCallbackGroup(),
        )

        self.get_logger().info('Test FindBook Action Server started and ready to accept goals')
        print("✅ FindBook Action服务器已启动")
        print("等待客户端连接...")

    def goal_callback(self, goal_request):
        """Goal请求回调
        完全按照action_cancel_example的模式
        """
        book_id = goal_request.book_id
        guide_patron = goal_request.guide_patron

        self.get_logger().info(f'Received goal request for book: {book_id}')
        self.get_logger().info(f'Guide patron: {guide_patron}')
        print(f"📚 收到找书请求: {book_id}, 引导读者: {guide_patron}")

        # 接受所有goal
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        """取消请求回调
        完全按照action_cancel_example的模式
        """
        self.get_logger().info('Cancel callback triggered! Accepting cancel request')
        print("🛑 收到取消请求")
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        """执行回调
        完全按照action_cancel_example的模式
        """
        book_id = goal_handle.request.book_id
        self.get_logger().info(f'Starting goal execution for book: {book_id}')
        print(f"🚀 开始执行找书任务: {book_id}")

        feedback = FindBook.Feedback()

        try:
            # 模拟找书过程（简化版本，完全按照action_cancel_example的模式）
            total_steps = 20
            self.get_logger().info(f'Goal will execute {total_steps} steps')

            for i in range(total_steps):
                if goal_handle.is_cancel_requested:
                    self.get_logger().warn('Goal execution was canceled by client')
                    goal_handle.canceled()
                    result = FindBook.Result()
                    result.success = False
                    result.message = f'Goal was canceled for book {book_id}'
                    self.get_logger().info('Returning cancel result to client')
                    print(f"🛑 任务被取消: {book_id}")
                    return result

                # 更新反馈
                feedback.status = 'executing'
                feedback.progress = (i + 1) * 5.0  # 5% increments
                feedback.distance_to_goal = max(0.0, 10.0 - i * 0.5)
                feedback.current_pose.position.x = i * 0.2
                feedback.current_pose.position.y = i * 0.1
                feedback.signal_strength = 0.8 if i > 15 else 0.0
                feedback.books_detected = [book_id] if i > 15 else []
                feedback.estimated_remaining = (total_steps - i - 1) * 0.5

                goal_handle.publish_feedback(feedback)
                print(f"  执行进度: {feedback.progress:.1f}% - 距离目标: {feedback.distance_to_goal:.2f}m")

                # 关键：使用rclpy.spin_once，完全按照action_cancel_example的模式
                rclpy.spin_once(self, timeout_sec=0.5)

            # 任务完成
            self.get_logger().info('Goal execution completed successfully')
            goal_handle.succeed()
            result = FindBook.Result()
            result.success = True
            result.message = f'Successfully found book {book_id}!'
            result.search_time = 10.0
            result.navigation_attempts = 1
            result.scan_attempts = 10

            self.get_logger().info('Goal execution completed successfully')
            self.get_logger().info('Returning success result to client')
            print(f"✅ 找书任务完成: {book_id}")
            return result

        except Exception as e:
            self.get_logger().error(f'Error during execution: {e}')
            print(f"❌ 执行过程中出错: {e}")
            goal_handle.abort()
            return FindBook.Result()


def main(args=None):
    """主函数
    完全按照action_cancel_example的模式
    """
    print("=== FindBook Action Server ===")
    print("这个服务器基于action_cancel_example的正确模式")
    print("应该能够正确处理取消后重新发送goal的情况")
    print()

    rclpy.init(args=args)
    print("ROS2 initialized")

    action_server = TestActionServer()
    print("Server node created, starting spin...")

    try:
        # 关键：使用rclpy.spin()而不是MultiThreadedExecutor
        # 这是action_cancel_example使用的模式
        rclpy.spin(action_server)
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt, shutting down...")

    action_server.destroy_node()
    rclpy.shutdown()
    print("Shutdown complete")


if __name__ == '__main__':
    main()