# navigation_monitor.py

import rclpy
from rclpy.node import Node
import time
from typing import Dict
from geometry_msgs.msg import PoseWithCovarianceStamped
from nav2_msgs.msg import Path


class NavigationMonitor:
    """导航健康监控"""

    def __init__(self, node: Node):
        self.node = node
        self.amcl_sub = None
        self.plan_sub = None
        self.last_amcl_time = 0
        self.plan_attempts = 0
        self.plan_successes = 0

        # 用于计算频率的滑动窗口
        self.amcl_timestamps = []
        self.window_size = 10  # 最近10次数据

    def start(self):
        """启动导航监控"""
        self.amcl_sub = self.node.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self._amcl_callback,
            10
        )

        self.plan_sub = self.node.create_subscription(
            Path,
            '/plan',
            self._plan_callback,
            10
        )

        self.node.get_logger().info("导航监控组件启动")

    def stop(self):
        """停止导航监控"""
        if self.amcl_sub:
            self.node.destroy_subscription(self.amcl_sub)
            self.amcl_sub = None

        if self.plan_sub:
            self.node.destroy_subscription(self.plan_sub)
            self.plan_sub = None

        self.node.get_logger().info("导航监控组件停止")

    def _amcl_callback(self, msg):
        """AMCL定位回调"""
        current_time = time.time()
        self.amcl_timestamps.append(current_time)

        # 保持滑动窗口大小
        if len(self.amcl_timestamps) > self.window_size:
            self.amcl_timestamps.pop(0)

        self.last_amcl_time = current_time

    def _plan_callback(self, msg):
        """路径规划回调"""
        self.plan_attempts += 1

        # 简单判断：如果路径长度大于0，认为规划成功
        if len(msg.poses) > 0:
            self.plan_successes += 1

    def get_health_data(self) -> Dict:
        """获取导航健康数据"""
        current_time = time.time()

        # 计算AMCL频率
        amcl_frequency = self._calculate_amcl_frequency(current_time)

        # 计算规划成功率
        if self.plan_attempts > 0:
            success_rate = (self.plan_successes / self.plan_attempts) * 100.0
        else:
            success_rate = 100.0

        return {
            'amcl_frequency': amcl_frequency,
            'planning_success_rate': success_rate,
            'plan_attempts': self.plan_attempts,
            'plan_successes': self.plan_successes,
            'last_amcl_time': self.last_amcl_time,
            'current_time': current_time
        }

    def _calculate_amcl_frequency(self, current_time: float) -> float:
        """计算AMCL发布频率"""
        if len(self.amcl_timestamps) < 2:
            return 0.0

        # 使用滑动窗口计算平均频率
        time_span = self.amcl_timestamps[-1] - self.amcl_timestamps[0]
        if time_span > 0:
            return (len(self.amcl_timestamps) - 1) / time_span
        else:
            return 0.0
