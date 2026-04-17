#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RFID传感器ROS2节点 - 集成噪声模型和ROS2接口
管理四向RFID传感器，发布扫描结果到ROS2 Topic
"""

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
import threading
import time
import math
from typing import List, Dict, Tuple, Optional

from libbot_msgs.msg import RFIDScan
from geometry_msgs.msg import Pose, Point
from std_msgs.msg import Header

from .rfid_noise_model import RFIDNoiseSimulator, DetectionResult


class RFIDSensorNode(Node):
    """RFID传感器ROS2节点"""

    def __init__(self, config_file: str = None):
        """初始化RFID传感器节点

        Args:
            config_file: 配置文件路径
        """
        super().__init__('rfid_sensor_node')

        # 加载配置
        self.config = self._load_config(config_file)

        # 初始化RFID噪声模拟器
        self.rfid_simulator = RFIDNoiseSimulator(self.config.get('noise_model', {}))

        # 四向RFID发布器
        self.publishers = {}
        self._setup_publishers()

        # 机器人状态
        self.robot_pose = (0.0, 0.0, 0.0)  # (x, y, theta)
        self.robot_moving = False
        self.last_update_time = time.time()

        # 场景RFID标签数据库
        self.rfid_tags = []
        self._load_rfid_tags()

        # 扫描定时器
        scan_interval = 1.0 / self.config.get('sensor', {}).get('scan_frequency', 10.0)
        self.scan_timer = self.create_timer(
            scan_interval,
            self._scan_callback
        )

        # 状态更新定时器
        self.status_timer = self.create_timer(
            1.0,  # 1秒更新一次状态
            self._status_callback
        )

        # 订阅机器人位姿（模拟）
        self.pose_subscription = self.create_subscription(
            Pose,
            '/robot_pose',  # 假设的位姿话题
            self._pose_callback,
            10
        )

        self.get_logger().info("RFID传感器节点启动完成")
        self.get_logger().info(f"扫描频率: {1.0/scan_interval:.1f} Hz")
        self.get_logger().info(f"检测方向: {list(self.publishers.keys())}")

    def _load_config(self, config_file: str = None) -> Dict:
        """加载配置文件"""
        # 默认配置
        default_config = {
            'noise_model': {
                'base_detection_range': 0.5,
                'false_negative_rate': 0.15,
                'false_positive_rate': 0.05,
                'distance_decay_factor': 2.0,
                'angle_sensitivity': 0.8,
                'environment_noise': 0.1,
                'scan_frequency': 10.0,
                'min_signal_strength': 0.1
            },
            'sensor': {
                'scan_frequency': 10.0,
                'directions': ['front', 'back', 'left', 'right'],
                'publish_frame_id': 'rfid_sensor'
            },
            'tags': {
                'database_file': 'library_tags.db',
                'default_power': 1.0
            }
        }

        # TODO: 从YAML文件加载配置
        # if config_file:
        #     with open(config_file, 'r') as f:
        #         file_config = yaml.safe_load(f)
        #     # 合并配置
        #     default_config.update(file_config)

        return default_config

    def _setup_publishers(self):
        """设置四向RFID发布器"""
        directions = self.config.get('sensor', {}).get('directions', [])

        for direction in directions:
            topic_name = f'/rfid/scan/{direction}'
            publisher = self.create_publisher(
                RFIDScan,
                topic_name,
                10
            )
            self.publishers[direction] = publisher
            self.get_logger().info(f"创建发布器: {topic_name}")

    def _load_rfid_tags(self):
        """加载RFID标签数据库"""
        # 模拟标签数据 - 实际应该从数据库或配置文件加载
        self.rfid_tags = [
            {'id': 'book_001', 'position': (2.0, 1.5, 1.0), 'power': 1.0},
            {'id': 'book_002', 'position': (2.5, 1.5, 1.0), 'power': 1.0},
            {'id': 'book_003', 'position': (3.0, 1.5, 1.0), 'power': 1.0},
            {'id': 'book_004', 'position': (-2.0, 1.5, 1.0), 'power': 1.0},
            {'id': 'book_005', 'position': (-2.5, 1.5, 1.0), 'power': 1.0},
            {'id': 'book_006', 'position': (1.5, -2.0, 1.0), 'power': 1.0},
            {'id': 'book_007', 'position': (1.5, -2.5, 1.0), 'power': 1.0},
            {'id': 'book_008', 'position': (-1.5, -2.0, 1.0), 'power': 1.0},
        ]

        self.get_logger().info(f"加载 {len(self.rfid_tags)} 个RFID标签")

    def _pose_callback(self, msg: Pose):
        """机器人位姿回调"""
        self.robot_pose = (
            msg.position.x,
            msg.position.y,
            self._quaternion_to_yaw(msg.orientation)
        )

        # 简单判断是否在移动（实际应该使用速度信息）
        current_time = time.time()
        if current_time - self.last_update_time > 0.1:  # 100ms内更新认为在移动
            self.robot_moving = True
        else:
            self.robot_moving = False

        self.last_update_time = current_time

    def _quaternion_to_yaw(self, orientation) -> float:
        """四元数转偏航角"""
        # 简化的四元数转欧拉角（只提取yaw）
        # 实际应该使用tf_transformations
        import math
        qx, qy, qz, qw = orientation.x, orientation.y, orientation.z, orientation.w
        yaw = math.atan2(2.0 * (qw * qz + qx * qy), 1.0 - 2.0 * (qy * qy + qz * qz))
        return yaw

    def _scan_callback(self):
        """RFID扫描回调 - 主扫描逻辑"""
        current_time = time.time()
        timestamp = self.get_clock().now().to_msg()

        # 对每个方向进行扫描
        for direction in self.publishers.keys():
            # 获取该方向范围内的标签
            tags_in_range = self._get_tags_in_range(direction)

            # 执行噪声仿真检测
            detection_results = self.rfid_simulator.simulate_detection(
                direction=direction,
                tags_in_range=tags_in_range,
                robot_pose=self.robot_pose,
                robot_orientation=self.robot_pose[2],
                timestamp=current_time
            )

            # 创建并发布RFIDScan消息
            scan_msg = self._create_rfid_scan_msg(
                direction=direction,
                results=detection_results,
                timestamp=timestamp
            )

            self.publishers[direction].publish(scan_msg)

    def _get_tags_in_range(self, direction: str) -> List[Dict]:
        """获取指定方向范围内的标签"""
        max_range = self.config.get('noise_model', {}).get('base_detection_range', 0.5)
        tags_in_range = []

        robot_x, robot_y, robot_theta = self.robot_pose

        for tag in self.rfid_tags:
            tag_x, tag_y, tag_z = tag['position']

            # 计算距离
            distance = math.sqrt(
                (tag_x - robot_x)**2 + (tag_y - robot_y)**2
            )

            # 如果在最大范围内，添加到候选列表
            if distance <= max_range * 2:  # 使用2倍范围进行预筛选
                tags_in_range.append(tag)

        return tags_in_range

    def _create_rfid_scan_msg(self, direction: str,
                            results: List[DetectionResult],
                            timestamp) -> RFIDScan:
        """创建RFIDScan消息"""
        msg = RFIDScan()

        # 设置header
        msg.header = Header()
        msg.header.stamp = timestamp
        msg.header.frame_id = f"rfid_{direction}"

        # 设置基本字段
        msg.antenna_position = direction
        msg.is_moving = self.robot_moving
        msg.detection_range = self.config.get('noise_model', {}).get('base_detection_range', 0.5)

        # 设置检测结果
        detected_books = []
        signal_strengths = []

        for result in results:
            if result.detected:
                detected_books.append(result.tag_id)
                signal_strengths.append(result.signal_strength)

        msg.detected_book_ids = detected_books
        msg.signal_strengths = signal_strengths

        return msg

    def _status_callback(self):
        """状态回调 - 定期报告状态"""
        stats = self.rfid_simulator.get_statistics()

        self.get_logger().info(
            f"RFID状态 - 扫描: {stats['total_scans']}, "
            f"检测率: {stats.get('detection_rate', 0):.2%}, "
            f"误检: {stats['false_positives']}, "
            f"漏检: {stats['false_negatives']}"
        )

    def get_diagnostic_info(self) -> Dict:
        """获取诊断信息"""
        stats = self.rfid_simulator.get_statistics()

        return {
            'node_status': 'running',
            'scan_frequency': self.config.get('sensor', {}).get('scan_frequency', 10.0),
            'active_directions': list(self.publishers.keys()),
            'robot_moving': self.robot_moving,
            'robot_pose': {
                'x': self.robot_pose[0],
                'y': self.robot_pose[1],
                'theta': self.robot_pose[2]
            },
            'tags_in_database': len(self.rfid_tags),
            'statistics': stats
        }

    def reset_statistics(self):
        """重置统计信息"""
        self.rfid_simulator.reset_statistics()
        self.get_logger().info("RFID统计信息已重置")


def main(args=None):
    """主函数 - 用于独立运行测试"""
    rclpy.init(args=args)

    # 创建RFID传感器节点
    rfid_node = RFIDSensorNode()

    try:
        # 启动节点
        rclpy.spin(rfid_node)
    except KeyboardInterrupt:
        pass
    finally:
        # 清理
        rfid_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()