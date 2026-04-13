#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L1恢复行为ROS2节点
图书馆机器人ROS2项目 - Epic 2错误处理与恢复机制

提供一个可运行的L1恢复行为演示节点
"""

import rclpy
from rclpy.node import Node
import time
import threading

from libbot_tasks.libbot_tasks.recovery_behaviors import L1RecoveryBehaviors


class L1RecoveryNode(Node):
    """L1恢复行为演示节点"""

    def __init__(self):
        super().__init__('l1_recovery_node')

        self.get_logger().info("L1恢复行为节点启动")

        # 创建L1恢复行为实例
        self.recovery = L1RecoveryBehaviors(self)

        # 设置ROS2通信
        self.recovery.setup_ros_communication()

        # 创建定时器进行演示
        self.timer = self.create_timer(5.0, self.demo_callback)

        # 演示状态
        self.demo_count = 0
        self.max_demos = 3

    def demo_callback(self):
        """演示回调函数"""
        self.demo_count += 1

        if self.demo_count > self.max_demos:
            self.get_logger().info("演示完成，节点将退出")
            self.destroy_timer(self.timer)
            return

        self.get_logger().info(f"\n=== 开始第 {self.demo_count} 次演示 ===")

        # 演示不同的恢复行为
        if self.demo_count == 1:
            self.demo_rfid_recovery()
        elif self.demo_count == 2:
            self.demo_localization_recovery()
        elif self.demo_count == 3:
            self.demo_target_redefinition()

    def demo_rfid_recovery(self):
        """演示RFID重新扫描恢复"""
        self.get_logger().info("演示: RFID重新扫描恢复")

        # 在后台线程中模拟RFID数据
        def simulate_rfid_data():
            time.sleep(2.0)  # 等待2秒后发布RFID数据

            # 注意：这里需要实际的ROS2消息发布，简化演示
            self.get_logger().info("模拟RFID数据到达")

        thread = threading.Thread(target=simulate_rfid_data)
        thread.daemon = True
        thread.start()

        # 执行RFID重新扫描
        result = self.recovery.retry_rfid_scan(
            "demo_book_001",
            {'x': 1.0, 'y': 2.0, 'z': 0.0}
        )

        if result:
            self.get_logger().info("✅ RFID重新扫描成功")
        else:
            self.get_logger().warn("❌ RFID重新扫描失败")

        thread.join(timeout=5)

    def demo_localization_recovery(self):
        """演示重新定位恢复"""
        self.get_logger().info("演示: 重新定位恢复")

        # 执行重新定位
        result = self.recovery.relocalize_robot()

        if result:
            self.get_logger().info("✅ 重新定位成功")
        else:
            self.get_logger().warn("❌ 重新定位失败")

    def demo_target_redefinition(self):
        """演示目标重定义恢复"""
        self.get_logger().info("演示: 目标重定义恢复")

        original_goal = {
            'book_id': 'original_book',
            'position': {'x': 1.0, 'y': 2.0, 'z': 0.0},
            'priority': 'high'
        }

        # 执行目标重定义
        alternative_goal = self.recovery.redefine_target(original_goal)

        if alternative_goal:
            self.get_logger().info(f"✅ 找到替代目标: {alternative_goal['book_id']}")
        else:
            self.get_logger().warn("❌ 未找到替代目标")

    def cleanup(self):
        """清理资源"""
        self.recovery.cleanup()
        self.get_logger().info("L1恢复节点清理完成")


def main(args=None):
    """主函数"""
    rclpy.init(args=args)

    try:
        # 创建并运行节点
        node = L1RecoveryNode()

        # 运行ROS2循环
        rclpy.spin(node)

    except KeyboardInterrupt:
        print("\n收到Ctrl+C，正在关闭...")

    finally:
        # 清理
        if 'node' in locals():
            node.cleanup()
            node.destroy_node()

        rclpy.shutdown()


if __name__ == '__main__':
    main()