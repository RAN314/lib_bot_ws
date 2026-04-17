#!/usr/bin/env python3
"""
RFID检测可视化节点
在RVIZ中显示RFID检测区域和检测结果
"""

import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point, Vector3, Pose
from std_msgs.msg import ColorRGBA, Header
from libbot_msgs.msg import RFIDScan
import math
import time

class RFIDVisualizer(Node):
    def __init__(self):
        super().__init__('rfid_visualizer')

        # 创建Marker发布器
        self.marker_publisher = self.create_publisher(MarkerArray, '/rfid_visualization', 10)

        # 订阅RFID检测结果
        self.rfid_subscriptions = []
        for direction in ['front', 'back', 'left', 'right']:
            topic_name = f'/rfid/scan/{direction}'
            sub = self.create_subscription(
                RFIDScan,
                topic_name,
                lambda msg, d=direction: self.rfid_callback(msg, d),
                10
            )
            self.rfid_subscriptions.append(sub)

        # 订阅机器人位姿
        self.robot_pose = None
        self.create_subscription(Pose, '/robot_pose', self.pose_callback, 10)

        # 创建定时器，定期更新可视化
        self.timer = self.create_timer(0.5, self.update_visualization)  # 2Hz

        # 存储检测到的标签
        self.detected_tags = {}
        self.last_update_time = time.time()

        # RFID检测区域参数
        self.detection_range = 0.5  # 检测范围
        self.antenna_positions = {
            'front': [0.15, 0.0, 0.1],
            'back': [-0.15, 0.0, 0.1],
            'left': [0.0, 0.15, 0.1],
            'right': [0.0, -0.15, 0.1]
        }

        self.get_logger().info('RFID可视化节点启动完成')

    def pose_callback(self, msg):
        """获取机器人位姿"""
        self.robot_pose = msg

    def rfid_callback(self, msg, direction):
        """处理RFID检测结果"""
        current_time = time.time()

        if msg.detected_book_ids:
            for i, book_id in enumerate(msg.detected_book_ids):
                if not book_id.startswith('fake_'):  # 只显示真实标签
                    strength = msg.signal_strengths[i]

                    # 存储检测信息
                    self.detected_tags[book_id] = {
                        'direction': direction,
                        'strength': strength,
                        'timestamp': current_time,
                        'position': self.calculate_tag_position(direction, strength)
                    }

        # 清理过期的检测
        self.cleanup_old_detections(current_time)

    def calculate_tag_position(self, direction, strength):
        """根据方向和信号强度估算标签位置"""
        # 简化的位置估算，实际应用中需要更复杂的算法
        antenna_pos = self.antenna_positions[direction]

        # 根据信号强度估算距离（简化模型）
        estimated_distance = self.detection_range * (1.0 - strength)

        # 根据天线方向计算位置
        if direction == 'front':
            return [antenna_pos[0] + estimated_distance, antenna_pos[1], antenna_pos[2]]
        elif direction == 'back':
            return [antenna_pos[0] - estimated_distance, antenna_pos[1], antenna_pos[2]]
        elif direction == 'left':
            return [antenna_pos[0], antenna_pos[1] + estimated_distance, antenna_pos[2]]
        elif direction == 'right':
            return [antenna_pos[0], antenna_pos[1] - estimated_distance, antenna_pos[2]]

        return antenna_pos

    def cleanup_old_detections(self, current_time):
        """清理过期的检测"""
        timeout = 5.0  # 5秒超时
        expired_tags = []

        for tag_id, info in self.detected_tags.items():
            if current_time - info['timestamp'] > timeout:
                expired_tags.append(tag_id)

        for tag_id in expired_tags:
            del self.detected_tags[tag_id]

    def transform_to_map(self, local_pos):
        """将局部坐标转换为map坐标"""
        if self.robot_pose is None:
            return local_pos

        # 获取机器人位置和朝向
        robot_x = self.robot_pose.position.x
        robot_y = self.robot_pose.position.y
        robot_z = self.robot_pose.position.z

        # 从四元数获取yaw角度
        q = self.robot_pose.orientation
        yaw = math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                        1.0 - 2.0 * (q.y * q.y + q.z * q.z))

        # 旋转局部坐标
        cos_yaw = math.cos(yaw)
        sin_yaw = math.sin(yaw)
        map_x = robot_x + local_pos[0] * cos_yaw - local_pos[1] * sin_yaw
        map_y = robot_y + local_pos[0] * sin_yaw + local_pos[1] * cos_yaw
        map_z = robot_z + local_pos[2]

        return [map_x, map_y, map_z]

    def create_detection_marker(self, tag_id, position, strength):
        """创建标签检测Marker"""
        # 转换到map坐标系
        map_position = self.transform_to_map(position)

        marker = Marker()
        marker.header = Header()
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.header.frame_id = 'map'  # 使用map坐标系

        marker.ns = 'rfid_tags'
        marker.id = hash(tag_id) % 1000000  # 生成唯一ID
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD

        # 设置位置
        marker.pose.position = Point(x=map_position[0], y=map_position[1], z=map_position[2])
        marker.pose.orientation.w = 1.0

        # 设置大小（根据信号强度）
        marker_scale = 0.05 + 0.1 * strength
        marker.scale = Vector3(x=marker_scale, y=marker_scale, z=marker_scale)

        # 设置颜色（根据信号强度）
        marker.color = ColorRGBA(
            r=1.0 - strength,  # 信号越强，红色越少
            g=strength,        # 信号越强，绿色越多
            b=0.0,
            a=0.8
        )

        # 添加文本标签
        text_marker = Marker()
        text_marker.header = marker.header
        text_marker.ns = 'rfid_labels'
        text_marker.id = marker.id + 1000000
        text_marker.type = Marker.TEXT_VIEW_FACING
        text_marker.action = Marker.ADD

        text_marker.pose.position = Point(x=map_position[0], y=map_position[1], z=map_position[2] + 0.1)
        text_marker.pose.orientation.w = 1.0
        text_marker.text = f"{tag_id}\n强度:{strength:.2f}"
        text_marker.scale.z = 0.08  # 文字大小
        text_marker.color = ColorRGBA(r=1.0, g=1.0, b=1.0, a=1.0)

        return [marker, text_marker]

    def create_detection_range_markers(self):
        """创建检测范围可视化"""
        markers = []

        if self.robot_pose is None:
            return markers

        for direction, pos in self.antenna_positions.items():
            # 转换到map坐标系
            map_pos = self.transform_to_map(pos)

            marker = Marker()
            marker.header = Header()
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.header.frame_id = 'map'  # 使用map坐标系

            marker.ns = 'rfid_ranges'
            marker.id = hash(direction) % 1000000
            marker.type = Marker.CYLINDER
            marker.action = Marker.ADD

            # 设置位置
            marker.pose.position = Point(x=map_pos[0], y=map_pos[1], z=map_pos[2])
            marker.pose.orientation.w = 1.0

            # 检测范围圆锥（简化为圆柱）
            marker.scale = Vector3(x=self.detection_range, y=self.detection_range, z=0.02)
            marker.color = ColorRGBA(r=0.0, g=0.5, b=1.0, a=0.2)  # 半透明蓝色

            markers.append(marker)

        return markers

    def update_visualization(self):
        """更新可视化"""
        # 等待机器人位姿
        if self.robot_pose is None:
            return

        marker_array = MarkerArray()

        # 添加检测范围标记
        range_markers = self.create_detection_range_markers()
        marker_array.markers.extend(range_markers)

        # 添加检测到的标签标记
        for tag_id, info in self.detected_tags.items():
            tag_markers = self.create_detection_marker(tag_id, info['position'], info['strength'])
            marker_array.markers.extend(tag_markers)

        # 发布标记数组
        self.marker_publisher.publish(marker_array)

        # 显示统计信息
        if len(self.detected_tags) > 0:
            self.get_logger().info(f'当前检测到 {len(self.detected_tags)} 个RFID标签')

def main(args=None):
    rclpy.init(args=args)

    try:
        node = RFIDVisualizer()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if 'node' in locals():
            node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()