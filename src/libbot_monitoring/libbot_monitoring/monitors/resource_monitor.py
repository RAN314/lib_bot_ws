# resource_monitor.py

import rclpy
from rclpy.node import Node
import time
import psutil
from typing import Dict
from rclpy.clock import Clock


class ResourceMonitor:
    """系统资源监控"""

    def __init__(self, node: Node):
        self.node = node
        self.process = psutil.Process()
        self.clock = Clock()

        # Topic延迟监控
        self.topic_latencies = {}
        self.subscribers = {}

        # 监控的关键话题
        self.monitored_topics = [
            '/amcl_pose',
            '/plan',
            '/rfid/scan/front',
            '/system/health'
        ]

        # 上一次消息时间
        self.last_message_times = {topic: 0 for topic in self.monitored_topics}

    def start(self):
        """启动资源监控"""
        # 为关键话题创建监控订阅者
        for topic in self.monitored_topics:
            try:
                # 动态创建订阅者来监控话题延迟
                self._create_topic_monitor(topic)
            except Exception as e:
                self.node.get_logger().warn(f"无法监控话题 {topic}: {str(e)}")

        self.node.get_logger().info("资源监控组件启动")

    def stop(self):
        """停止资源监控"""
        for topic, sub in self.subscribers.items():
            if sub:
                self.node.destroy_subscription(sub)

        self.subscribers.clear()
        self.node.get_logger().info("资源监控组件停止")

    def _create_topic_monitor(self, topic_name: str):
        """为话题创建监控订阅者"""
        # 这里使用通用消息类型，实际应用中需要根据话题类型调整
        from std_msgs.msg import String

        def topic_callback(msg):
            current_time = time.time()
            self.last_message_times[topic_name] = current_time

        self.subscribers[topic_name] = self.node.create_subscription(
            String,
            topic_name,
            topic_callback,
            10
        )

    def get_health_data(self) -> Dict:
        """获取资源健康数据"""
        current_time = time.time()

        # CPU使用率
        cpu_usage = self.process.cpu_percent(interval=0.1)

        # 内存使用量(MB)
        memory_info = self.process.memory_info()
        memory_usage = memory_info.rss / 1024 / 1024

        # 系统整体资源使用
        system_cpu = psutil.cpu_percent(interval=0.1)
        system_memory = psutil.virtual_memory().percent

        # Topic延迟（计算平均延迟）
        topic_latency = self._calculate_average_topic_latency(current_time)

        # ROS2节点统计
        node_count = self._count_ros2_nodes()

        return {
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'system_cpu_usage': system_cpu,
            'system_memory_usage': system_memory,
            'topic_latency': topic_latency,
            'node_count': node_count,
            'process_id': self.process.pid,
            'current_time': current_time
        }

    def _calculate_average_topic_latency(self, current_time: float) -> float:
        """计算平均话题延迟"""
        latencies = []

        for topic, last_time in self.last_message_times.items():
            if last_time > 0:
                latency = current_time - last_time
                latencies.append(latency * 1000)  # 转换为毫秒

        if latencies:
            return sum(latencies) / len(latencies)
        else:
            return 0.0

    def _count_ros2_nodes(self) -> int:
        """统计ROS2节点数量"""
        try:
            # 使用ROS2 API获取节点列表
            node_names = self.node.get_node_names()
            return len(node_names)
        except Exception:
            # 如果无法获取，返回估计值
            return 5  # 假设有5个主要节点

    def get_detailed_system_info(self) -> Dict:
        """获取详细的系统信息"""
        return {
            'cpu_count': psutil.cpu_count(),
            'cpu_freq': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
            'total_memory': psutil.virtual_memory().total / (1024**3),  # GB
            'available_memory': psutil.virtual_memory().available / (1024**3),  # GB
            'disk_usage': psutil.disk_usage('/').percent,
            'boot_time': psutil.boot_time(),
            'process_threads': self.process.num_threads(),
            'process_open_files': len(self.process.open_files()) if self.process.open_files() else 0
        }
