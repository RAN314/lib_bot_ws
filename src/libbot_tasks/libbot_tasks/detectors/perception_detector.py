#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
感知错误检测器 - 检测RFID和传感器相关问题
实现RFID检测异常、传感器超时等检测
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from sensor_msgs.msg import LaserScan, Imu
import time


class PerceptionErrorDetector:
    """感知错误检测器 - 检测RFID和传感器相关问题"""

    def __init__(self, node: Node):
        """初始化感知错误检测器"""
        self.node = node
        self.rfid_timeout = 5.0                    # RFID检测超时(秒)
        self.detection_confidence_threshold = 0.7  # 检测置信度阈值
        self.sensor_health_check_interval = 2.0    # 传感器健康检查间隔(秒)

        # 状态跟踪
        self.last_rfid_time = None
        self.last_laser_time = None
        self.last_imu_time = None
        self.rfid_detection_history = []
        self.max_history_size = 10
        self.last_health_check = None

        # 从参数服务器加载配置
        self._load_parameters()

        # 订阅相关Topic
        self.rfid_sub = node.create_subscription(
            String,
            '/rfid/scan',
            self._rfid_callback,
            10
        )

        self.laser_sub = node.create_subscription(
            LaserScan,
            '/scan',
            self._laser_callback,
            10
        )

        self.imu_sub = node.create_subscription(
            Imu,
            '/imu',
            self._imu_callback,
            10
        )

    def _load_parameters(self):
        """加载检测参数"""
        try:
            self.rfid_timeout = self.node.declare_parameter(
                'detection.perception.rfid_timeout', 5.0
            ).value
            self.detection_confidence_threshold = self.node.declare_parameter(
                'detection.perception.detection_confidence_threshold', 0.7
            ).value
            self.sensor_health_check_interval = self.node.declare_parameter(
                'detection.perception.sensor_health_check_interval', 2.0
            ).value

            self.node.get_logger().info("感知检测器参数加载完成")
        except Exception as e:
            self.node.get_logger().warn(f"感知检测器参数加载失败: {str(e)}")

    def detect(self) -> list:
        """执行感知错误检测

        Returns:
            检测到的错误列表
        """
        errors = []

        # 检测RFID超时
        errors.extend(self._check_rfid_timeout())

        # 检测传感器超时
        errors.extend(self._check_sensor_timeout())

        # 检测感知置信度低
        errors.extend(self._check_perception_confidence())

        # 检测传感器健康状态
        errors.extend(self._check_sensor_health())

        return errors

    def _rfid_callback(self, msg: String):
        """RFID消息回调"""
        current_time = time.time()
        self.last_rfid_time = current_time

        # 记录RFID检测结果
        detection_info = {
            'timestamp': current_time,
            'data': msg.data,
            'confidence': self._calculate_rfid_confidence(msg.data)
        }

        self.rfid_detection_history.append(detection_info)

        # 保持历史记录大小
        if len(self.rfid_detection_history) > self.max_history_size:
            self.rfid_detection_history.pop(0)

    def _laser_callback(self, msg: LaserScan):
        """激光雷达消息回调"""
        self.last_laser_time = time.time()

    def _imu_callback(self, msg: Imu):
        """IMU消息回调"""
        self.last_imu_time = time.time()

    def _calculate_rfid_confidence(self, rfid_data: str) -> float:
        """计算RFID检测置信度"""
        # 简化的置信度计算
        # 实际实现可能需要更复杂的算法
        if not rfid_data or rfid_data == "no_detection":
            return 0.0

        # 检查RFID数据格式
        if len(rfid_data) >= 8:  # 假设有效的RFID标签至少有8个字符
            return 0.9
        elif len(rfid_data) >= 4:
            return 0.7
        else:
            return 0.3

    def _check_rfid_timeout(self) -> list:
        """检查RFID检测超时"""
        errors = []

        if not self.last_rfid_time:
            # 从未收到RFID数据，检查是否应该收到
            if time.time() > 10.0:  # 启动10秒后检查
                errors.append({
                    'error_type': 'rfid_detection_failed',
                    'message': 'RFID检测器未启动或未连接',
                    'timeout': float('inf')
                })
            return errors

        # 检查RFID检测是否超时
        current_time = time.time()
        time_since_rfid = current_time - self.last_rfid_time

        if time_since_rfid > self.rfid_timeout:
            errors.append({
                'error_type': 'rfid_detection_failed',
                'message': f'RFID检测超时: {time_since_rfid:.1f} 秒无检测',
                'timeout': time_since_rfid,
                'threshold': self.rfid_timeout
            })

        return errors

    def _check_sensor_timeout(self) -> list:
        """检查传感器超时"""
        errors = []
        current_time = time.time()

        # 检查激光雷达超时
        if self.last_laser_time:
            time_since_laser = current_time - self.last_laser_time
            if time_since_laser > 2.0:  # 激光雷达2秒超时
                errors.append({
                    'error_type': 'sensor_timeout',
                    'message': f'激光雷达超时: {time_since_laser:.1f} 秒无数据',
                    'sensor': 'laser',
                    'timeout': time_since_laser
                })

        # 检查IMU超时
        if self.last_imu_time:
            time_since_imu = current_time - self.last_imu_time
            if time_since_imu > 1.0:  # IMU1秒超时
                errors.append({
                    'error_type': 'sensor_timeout',
                    'message': f'IMU超时: {time_since_imu:.1f} 秒无数据',
                    'sensor': 'imu',
                    'timeout': time_since_imu
                })

        return errors

    def _check_perception_confidence(self) -> list:
        """检查感知置信度低"""
        errors = []

        if not self.rfid_detection_history:
            return errors

        # 检查最近RFID检测的置信度
        recent_detections = self.rfid_detection_history[-3:]  # 最近3次检测
        low_confidence_count = 0

        for detection in recent_detections:
            if detection['confidence'] < self.detection_confidence_threshold:
                low_confidence_count += 1

        # 如果大部分检测置信度都低
        if low_confidence_count >= len(recent_detections) * 0.7:
            errors.append({
                'error_type': 'perception_low_confidence',
                'message': f'RFID检测置信度持续偏低: {low_confidence_count}/{len(recent_detections)} 次检测',
                'low_confidence_count': low_confidence_count,
                'total_checked': len(recent_detections),
                'threshold': self.detection_confidence_threshold
            })

        return errors

    def _check_sensor_health(self) -> list:
        """检查传感器健康状态"""
        errors = []
        current_time = time.time()

        # 定期进行健康检查
        if (not self.last_health_check or
            current_time - self.last_health_check > self.sensor_health_check_interval):

            self.last_health_check = current_time

            # 检查传感器数据质量
            sensor_issues = []

            # 检查激光雷达数据质量（简化检查）
            if self.last_laser_time and current_time - self.last_laser_time < 2.0:
                # 传感器正常工作，检查数据质量
                pass  # 这里可以添加更详细的数据质量检查

            # 检查IMU数据质量
            if self.last_imu_time and current_time - self.last_imu_time < 1.0:
                # 传感器正常工作
                pass

            # 如果没有收到任何传感器数据
            if (not self.last_laser_time and
                not self.last_imu_time and
                current_time > 5.0):  # 启动5秒后检查

                errors.append({
                    'error_type': 'sensor_timeout',
                    'message': '所有传感器均无数据，可能传感器未启动',
                    'sensor': 'all_sensors'
                })

        return errors

    def get_status(self) -> dict:
        """获取检测器状态"""
        status = {
            'last_rfid_time': self.last_rfid_time,
            'last_laser_time': self.last_laser_time,
            'last_imu_time': self.last_imu_time,
            'rfid_history_size': len(self.rfid_detection_history),
            'last_health_check': self.last_health_check,
            'rfid_timeout': self.rfid_timeout,
            'confidence_threshold': self.detection_confidence_threshold
        }
        return status

    def reset(self):
        """重置检测器"""
        self.last_rfid_time = None
        self.last_laser_time = None
        self.last_imu_time = None
        self.rfid_detection_history.clear()
        self.last_health_check = None
        self.node.get_logger().info("感知错误检测器已重置")


def main():
    """测试函数"""
    import rclpy

    rclpy.init()

    # 创建测试节点
    test_node = Node("perception_detector_test")

    # 创建感知检测器实例
    detector = PerceptionErrorDetector(test_node)

    try:
        print("🧪 感知错误检测器测试")
        print("等待传感器数据...")

        # 运行测试10秒
        start_time = time.time()
        while time.time() - start_time < 10.0:
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

    print("✅ 感知错误检测器测试完成")


if __name__ == "__main__":
    main()