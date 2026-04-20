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
import yaml
import os
from typing import List, Dict, Tuple, Optional

from libbot_msgs.msg import RFIDScan
from geometry_msgs.msg import Pose, Point
from geometry_msgs.msg import PoseWithCovarianceStamped
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
        noise_config = self.config.get('noise_model', {})
        # 确保包含默认方向配置
        if 'directions' not in noise_config:
            noise_config['directions'] = self.config.get('sensor', {}).get('directions', ['front', 'back', 'left', 'right'])
        self.rfid_simulator = RFIDNoiseSimulator(noise_config)

        # 四向RFID发布器
        self._rfid_publishers = {}
        self._setup_publishers()

        # 机器人状态
        self.robot_pose = (0.0, 0.0, 0.0)  # (x, y, theta)
        self.robot_moving = False
        self.last_update_time = time.time()
        self.pose_received = False  # 标记是否收到有效位姿

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

        # 订阅机器人位姿 - 支持多种位姿源
        self.pose_subscription = self.create_subscription(
            Pose,
            '/robot_pose',  # 来自Gazebo的位姿
            self._pose_callback,
            10
        )

        # 订阅AMCL定位结果（用于导航系统集成）
        self.amcl_pose_subscription = self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',  # AMCL定位结果
            self._amcl_pose_callback,
            10
        )

        self.get_logger().info("RFID传感器节点启动完成")
        self.get_logger().info(f"扫描频率: {1.0/scan_interval:.1f} Hz")
        self.get_logger().info(f"检测方向: {list(self._rfid_publishers.keys())}")
        self.get_logger().info("位姿源: /robot_pose (Gazebo) 和 /amcl_pose (导航定位)")
        self.get_logger().info("模式: 支持无位姿运行（使用默认位置）")

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
            'rfid_tags': {
                'predefined_tags': []
            }
        }

        # 从YAML文件加载配置
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    file_config = yaml.safe_load(f)
                if file_config:
                    # 合并配置
                    if 'rfid_noise_model' in file_config:
                        default_config['noise_model'].update(file_config['rfid_noise_model'])
                    if 'rfid_sensor' in file_config:
                        default_config['sensor'].update(file_config['rfid_sensor'])
                    if 'rfid_tags' in file_config:
                        default_config['rfid_tags'] = file_config['rfid_tags']
                    self.get_logger().info(f'成功加载配置文件: {config_file}')
            except Exception as e:
                self.get_logger().warn(f'加载配置文件失败: {e}, 使用默认配置')

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
            self._rfid_publishers[direction] = publisher
            self.get_logger().info(f"创建发布器: {topic_name}")

    def _load_rfid_tags(self):
        """加载RFID标签数据库"""
        # 默认标签（用于测试）
        default_tags = [
            {'id': 'book_001', 'position': (2.0, 1.5, 0.3), 'power': 1.0},
            {'id': 'book_002', 'position': (2.5, 1.5, 0.3), 'power': 1.0},
            {'id': 'book_003', 'position': (3.0, 1.5, 0.3), 'power': 1.0},
            {'id': 'book_004', 'position': (-2.0, 1.5, 0.3), 'power': 1.0},
            {'id': 'book_005', 'position': (-2.5, 1.5, 0.3), 'power': 1.0},
            {'id': 'book_006', 'position': (1.5, -2.0, 0.3), 'power': 1.0},
            {'id': 'book_007', 'position': (1.5, -2.5, 0.3), 'power': 1.0},
            {'id': 'book_008', 'position': (-1.5, -2.0, 0.3), 'power': 1.0},
        ]

        # 尝试从配置文件中加载标签
        config_tags = self.config.get('rfid_tags', {}).get('predefined_tags', [])
        if config_tags:
            loaded_tags = []
            for tag in config_tags:
                loaded_tags.append({
                    'id': tag['id'],
                    'position': tuple(tag['position']),
                    'power': tag.get('power', 1.0)
                })
            self.rfid_tags = loaded_tags
            self.get_logger().info(f"从配置文件加载 {len(self.rfid_tags)} 个RFID标签")
        else:
            self.rfid_tags = default_tags
            self.get_logger().info(f"使用默认的 {len(self.rfid_tags)} 个RFID标签")

    def _pose_callback(self, msg: Pose):
        """机器人位姿回调 - 来自Gazebo"""
        self.robot_pose = (
            msg.position.x,
            msg.position.y,
            self._quaternion_to_yaw(msg.orientation)
        )
        self.pose_received = True

        # 简单判断是否在移动（实际应该使用速度信息）
        current_time = time.time()
        if current_time - self.last_update_time > 0.1:  # 100ms内更新认为在移动
            self.robot_moving = True
        else:
            self.robot_moving = False
        self.last_update_time = current_time

    def _amcl_pose_callback(self, msg: PoseWithCovarianceStamped):
        """AMCL定位结果回调 - 用于导航系统集成"""
        pose = msg.pose.pose
        self.robot_pose = (
            pose.position.x,
            pose.position.y,
            self._quaternion_to_yaw(pose.orientation)
        )
        self.pose_received = True

        # AMCL定位通常认为是稳定的，不处于移动状态
        self.robot_moving = False
        self.last_update_time = time.time()

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

        # 检查是否收到有效位姿
        if not self.pose_received:
            # 如果没有收到位姿，记录警告但继续运行
            if int(current_time) % 5 == 0:  # 每5秒记录一次
                self.get_logger().warn('等待机器人位姿数据...')
            # 使用默认位姿继续扫描
            self.robot_pose = (0.0, 0.0, 0.0)

        # 对每个方向进行扫描
        for direction in self._rfid_publishers.keys():
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

            self._rfid_publishers[direction].publish(scan_msg)

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
            'active_directions': list(self._rfid_publishers.keys()),
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