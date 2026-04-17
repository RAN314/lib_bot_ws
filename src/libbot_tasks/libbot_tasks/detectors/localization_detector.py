#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定位错误检测器 - 检测AMCL定位相关问题
实现定位误差、漂移和丢失检测
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped
from nav_msgs.msg import Odometry, OccupancyGrid
import numpy as np
import time


class LocalizationErrorDetector:
    """定位错误检测器 - 检测AMCL定位相关问题"""

    def __init__(self, node: Node):
        """初始化定位错误检测器"""
        self.node = node
        self.pose_covariance_threshold = 0.5  # 协方差阈值
        self.drift_distance_threshold = 0.3   # 漂移距离阈值
        self.lost_timeout = 5.0               # 定位丢失超时
        self.last_pose = None
        self.last_pose_time = None
        self.pose_history = []  # 位姿历史记录
        self.max_history_size = 10

        # 从参数服务器加载配置
        self._load_parameters()

        # 订阅相关Topic
        self.pose_sub = node.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self._pose_callback,
            10
        )

        self.odom_sub = node.create_subscription(
            Odometry,
            '/odom',
            self._odom_callback,
            10
        )

    def _load_parameters(self):
        """加载检测参数"""
        try:
            self.pose_covariance_threshold = self.node.declare_parameter(
                'detection.localization.covariance_threshold', 0.5
            ).value
            self.drift_velocity_threshold = self.node.declare_parameter(
                'detection.localization.drift_velocity_threshold', 2.0
            ).value
            self.lost_timeout = self.node.declare_parameter(
                'detection.localization.lost_timeout', 5.0
            ).value
            self.max_history_size = self.node.declare_parameter(
                'detection.localization.history_size', 10
            ).value

            self.node.get_logger().info("定位检测器参数加载完成")
        except Exception as e:
            self.node.get_logger().warn(f"定位检测器参数加载失败: {str(e)}")

    def detect(self) -> list:
        """执行定位错误检测

        Returns:
            检测到的错误列表
        """
        errors = []

        # 检测定位协方差过大
        errors.extend(self._check_covariance())

        # 检测定位漂移
        errors.extend(self._check_localization_drift())

        # 检测定位丢失
        errors.extend(self._check_localization_lost())

        return errors

    def _pose_callback(self, msg: PoseWithCovarianceStamped):
        """位姿消息回调"""
        current_time = time.time()

        # 更新位姿历史
        pose_info = {
            'timestamp': current_time,
            'position': msg.pose.pose.position,
            'covariance': msg.pose.covariance,
            'confidence': self._calculate_confidence(msg.pose.covariance)
        }

        self.pose_history.append(pose_info)

        # 保持历史记录大小
        if len(self.pose_history) > self.max_history_size:
            self.pose_history.pop(0)

        self.last_pose = pose_info
        self.last_pose_time = current_time

    def _odom_callback(self, msg: Odometry):
        """里程计消息回调"""
        # 用于与定位结果对比，检测漂移
        # 这里可以添加里程计与AMCL的对比逻辑
        pass

    def _check_covariance(self) -> list:
        """检查定位协方差是否过大"""
        errors = []

        if not self.last_pose:
            return errors

        # 计算位置协方差（取x,y方向的方差）
        position_variance = (
            self.last_pose['covariance'][0] +  # x方向方差
            self.last_pose['covariance'][7]    # y方向方差
        )

        if position_variance > self.pose_covariance_threshold:
            errors.append({
                'error_type': 'localization_high_covariance',
                'message': f'定位协方差过大: {position_variance:.3f}',
                'covariance': position_variance,
                'threshold': self.pose_covariance_threshold,
                'confidence': self.last_pose['confidence']
            })

        return errors

    def _check_localization_drift(self) -> list:
        """检查定位漂移"""
        errors = []

        if len(self.pose_history) < 2:
            return errors

        # 计算最近两个位姿之间的距离
        recent = self.pose_history[-1]
        previous = self.pose_history[-2]

        time_diff = recent['timestamp'] - previous['timestamp']
        if time_diff == 0:
            return errors

        # 计算位移
        dx = recent['position'].x - previous['position'].x
        dy = recent['position'].y - previous['position'].y
        distance = np.sqrt(dx*dx + dy*dy)

        # 计算速度
        velocity = distance / time_diff

        # 如果速度异常大，可能是定位漂移
        if velocity > self.drift_velocity_threshold:
            errors.append({
                'error_type': 'localization_drift',
                'message': f'检测到定位漂移: 速度 {velocity:.2f} m/s',
                'velocity': velocity,
                'distance': distance,
                'time_diff': time_diff
            })

        return errors

    def _check_localization_lost(self) -> list:
        """检查定位是否丢失"""
        errors = []

        if not self.last_pose_time:
            return errors

        # 如果超过设定时间没有收到定位更新，认为定位丢失
        current_time = time.time()
        time_since_last_pose = current_time - self.last_pose_time

        if time_since_last_pose > self.lost_timeout:
            errors.append({
                'error_type': 'localization_lost',
                'message': f'定位丢失: {time_since_last_pose:.1f} 秒无更新',
                'time_since_update': time_since_last_pose
            })

        return errors

    def _calculate_confidence(self, covariance: list) -> float:
        """计算定位置信度 (0.0-1.0)"""
        # 基于协方差计算置信度
        position_variance = covariance[0] + covariance[7]  # x,y方向方差和

        # 方差越小，置信度越高
        confidence = 1.0 / (1.0 + position_variance)
        return min(max(confidence, 0.0), 1.0)  # 限制在0-1范围内

    def get_status(self) -> dict:
        """获取检测器状态"""
        status = {
            'last_pose_time': self.last_pose_time,
            'history_size': len(self.pose_history),
            'last_confidence': self.last_pose['confidence'] if self.last_pose else 0.0,
            'covariance_threshold': self.pose_covariance_threshold,
            'drift_threshold': self.drift_velocity_threshold,
            'lost_timeout': self.lost_timeout
        }
        return status

    def reset(self):
        """重置检测器"""
        self.last_pose = None
        self.last_pose_time = None
        self.pose_history.clear()
        self.node.get_logger().info("定位错误检测器已重置")


def main():
    """测试函数"""
    import rclpy

    rclpy.init()

    # 创建测试节点
    test_node = Node("localization_detector_test")

    # 创建定位检测器实例
    detector = LocalizationErrorDetector(test_node)

    try:
        print("🧪 定位错误检测器测试")
        print("等待AMCL位姿数据...")

        # 运行测试5秒
        start_time = time.time()
        while time.time() - start_time < 5.0:
            rclpy.spin_once(test_node, timeout_sec=0.1)

            # 模拟检测
            errors = detector.detect()
            if errors:
                for error in errors:
                    print(f"检测到错误: {error}")

    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
    finally:
        # 清理
        test_node.destroy_node()
        rclpy.shutdown()

    print("✅ 定位错误检测器测试完成")


if __name__ == "__main__":
    main()