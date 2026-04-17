# perception_monitor.py

import rclpy
from rclpy.node import Node
import time
from typing import Dict
from libbot_msgs.msg import RFIDScan


class PerceptionMonitor:
    """感知健康监控"""

    def __init__(self, node: Node):
        self.node = node
        self.rfid_subs = {}
        self.last_rfid_time = 0
        self.scan_attempts = 0
        self.successful_scans = 0

        # 四向RFID监控
        self.directions = ['front', 'back', 'left', 'right']
        self.rfid_timestamps = {direction: [] for direction in self.directions}
        self.rfid_counts = {direction: 0 for direction in self.directions}
        self.window_size = 10  # 滑动窗口大小

    def start(self):
        """启动感知监控"""
        # 订阅四个方向的RFID扫描话题
        for direction in self.directions:
            topic_name = f'/rfid/scan/{direction}'
            self.rfid_subs[direction] = self.node.create_subscription(
                RFIDScan,
                topic_name,
                lambda msg, dir=direction: self._rfid_callback(msg, dir),
                10
            )

        self.node.get_logger().info("感知监控组件启动")

    def stop(self):
        """停止感知监控"""
        for direction, sub in self.rfid_subs.items():
            if sub:
                self.node.destroy_subscription(sub)

        self.rfid_subs.clear()
        self.node.get_logger().info("感知监控组件停止")

    def _rfid_callback(self, msg, direction: str):
        """RFID扫描回调"""
        current_time = time.time()

        # 更新该方向的统计
        self.rfid_timestamps[direction].append(current_time)
        self.rfid_counts[direction] += 1

        # 保持滑动窗口大小
        if len(self.rfid_timestamps[direction]) > self.window_size:
            self.rfid_timestamps[direction].pop(0)

        self.last_rfid_time = current_time
        self.scan_attempts += 1

        # 简单判断：如果检测到了RFID标签，认为扫描成功
        if msg.detected:
            self.successful_scans += 1

    def get_health_data(self) -> Dict:
        """获取感知健康数据"""
        current_time = time.time()

        # 计算整体RFID扫描频率
        rfid_frequency = self._calculate_overall_rfid_frequency(current_time)

        # 计算检测成功率
        if self.scan_attempts > 0:
            success_rate = (self.successful_scans / self.scan_attempts) * 100.0
        else:
            success_rate = 100.0

        # 各方向详细数据
        direction_data = {}
        for direction in self.directions:
            direction_data[f'{direction}_count'] = self.rfid_counts[direction]
            direction_data[f'{direction}_frequency'] = self._calculate_direction_frequency(direction, current_time)

        return {
            'rfid_frequency': rfid_frequency,
            'detection_success_rate': success_rate,
            'scan_attempts': self.scan_attempts,
            'successful_scans': self.successful_scans,
            'last_rfid_time': self.last_rfid_time,
            'current_time': current_time,
            **direction_data
        }

    def _calculate_overall_rfid_frequency(self, current_time: float) -> float:
        """计算整体RFID扫描频率"""
        total_count = sum(len(timestamps) for timestamps in self.rfid_timestamps.values())

        if total_count < 2:
            return 0.0

        # 找到所有时间戳的最小值和最大值
        all_timestamps = []
        for timestamps in self.rfid_timestamps.values():
            all_timestamps.extend(timestamps)

        if len(all_timestamps) < 2:
            return 0.0

        time_span = max(all_timestamps) - min(all_timestamps)
        if time_span > 0:
            return (len(all_timestamps) - 1) / time_span
        else:
            return 0.0

    def _calculate_direction_frequency(self, direction: str, current_time: float) -> float:
        """计算特定方向的RFID扫描频率"""
        timestamps = self.rfid_timestamps[direction]

        if len(timestamps) < 2:
            return 0.0

        time_span = timestamps[-1] - timestamps[0]
        if time_span > 0:
            return (len(timestamps) - 1) / time_span
        else:
            return 0.0
