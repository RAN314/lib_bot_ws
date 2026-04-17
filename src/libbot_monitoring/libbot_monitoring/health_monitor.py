# health_monitor.py

import rclpy
from rclpy.node import Node
import threading
import time
import psutil
import statistics
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from libbot_msgs.msg import SystemHealth
from libbot_msgs.srv import GetHealthReport


@dataclass
class HealthThreshold:
    """健康阈值定义"""
    warning_threshold: float
    error_threshold: float
    critical_threshold: float


class HealthMonitor:
    """系统健康监控管理器"""

    def __init__(self, node: Node):
        """初始化健康监控管理器

        Args:
            node: ROS2节点实例
        """
        self.node = node
        self.is_running = False
        self.monitoring_thread = None

        # 监控组件
        self.navigation_monitor = None
        self.perception_monitor = None
        self.system_monitor = None
        self.resource_monitor = None

        # 健康数据存储
        self.health_data = {}
        self.health_history = []
        self.data_lock = threading.RLock()

        # ROS2接口
        self.health_publisher = None
        self.health_service = None

        # 配置参数
        self.monitor_frequency = 10.0  # 10Hz
        self.history_duration = 3600   # 1小时历史数据
        self.thresholds = self._load_thresholds()

        self._init_monitors()
        self._init_ros2_interfaces()

    def _init_monitors(self):
        """初始化监控组件"""
        from .monitors.navigation_monitor import NavigationMonitor
        from .monitors.perception_monitor import PerceptionMonitor
        from .monitors.system_monitor import SystemMonitor
        from .monitors.resource_monitor import ResourceMonitor

        self.navigation_monitor = NavigationMonitor(self.node)
        self.perception_monitor = PerceptionMonitor(self.node)
        self.system_monitor = SystemMonitor(self.node)
        self.resource_monitor = ResourceMonitor(self.node)

    def _init_ros2_interfaces(self):
        """初始化ROS2接口"""
        # 健康状态发布
        self.health_publisher = self.node.create_publisher(
            SystemHealth,
            '/system/health',
            10
        )

        # 健康报告服务
        self.health_service = self.node.create_service(
            GetHealthReport,
            '/system/get_health_report',
            self._health_report_callback
        )

    def start_monitoring(self):
        """启动健康监控"""
        if self.is_running:
            return

        self.is_running = True

        # 启动各监控组件
        self.navigation_monitor.start()
        self.perception_monitor.start()
        self.system_monitor.start()
        self.resource_monitor.start()

        # 启动监控线程
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()

        self.node.get_logger().info("系统健康监控启动")

    def stop_monitoring(self):
        """停止健康监控"""
        self.is_running = False

        # 停止监控组件
        if self.navigation_monitor:
            self.navigation_monitor.stop()
        if self.perception_monitor:
            self.perception_monitor.stop()
        if self.system_monitor:
            self.system_monitor.stop()
        if self.resource_monitor:
            self.resource_monitor.stop()

        # 等待监控线程结束
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)

        self.node.get_logger().info("系统健康监控停止")

    def _monitoring_loop(self):
        """监控主循环"""
        period = 1.0 / self.monitor_frequency

        while self.is_running:
            start_time = time.time()

            try:
                # 收集各组件健康数据
                health_data = self._collect_health_data()

                # 评估健康状态
                overall_health = self._evaluate_health(health_data)

                # 存储健康数据
                self._store_health_data(health_data, overall_health)

                # 发布健康状态
                self._publish_health_status(health_data, overall_health)

                # 检查告警条件
                self._check_alerts(health_data)

            except Exception as e:
                self.node.get_logger().error(f"监控循环错误: {str(e)}")

            # 保持固定频率
            elapsed = time.time() - start_time
            sleep_time = max(0, period - elapsed)
            time.sleep(sleep_time)

    def _collect_health_data(self) -> Dict:
        """收集健康数据"""
        return {
            'timestamp': time.time(),
            'navigation': self.navigation_monitor.get_health_data(),
            'perception': self.perception_monitor.get_health_data(),
            'system': self.system_monitor.get_health_data(),
            'resource': self.resource_monitor.get_health_data()
        }

    def _evaluate_health(self, health_data: Dict) -> str:
        """评估整体健康状态"""
        health_scores = []

        # 评估各个子系统
        for component, data in health_data.items():
            if component == 'timestamp':
                continue

            score = self._calculate_component_score(component, data)
            health_scores.append(score)

        # 计算整体健康分数
        if health_scores:
            avg_score = statistics.mean(health_scores)

            if avg_score >= 0.9:
                return 'HEALTHY'
            elif avg_score >= 0.7:
                return 'WARNING'
            elif avg_score >= 0.5:
                return 'ERROR'
            else:
                return 'CRITICAL'

        return 'UNKNOWN'

    def _calculate_component_score(self, component: str, data: Dict) -> float:
        """计算组件健康分数"""
        score = 1.0

        # 根据组件类型计算分数
        if component == 'navigation':
            # AMCL频率权重40%，规划成功率权重60%
            amcl_score = min(1.0, data.get('amcl_frequency', 0) / 10.0)
            plan_score = data.get('planning_success_rate', 0) / 100.0
            score = amcl_score * 0.4 + plan_score * 0.6

        elif component == 'perception':
            # RFID频率权重30%，检测成功率权重70%
            rfid_score = min(1.0, data.get('rfid_frequency', 0) / 10.0)
            detect_score = data.get('detection_success_rate', 0) / 100.0
            score = rfid_score * 0.3 + detect_score * 0.7

        elif component == 'resource':
            # CPU、内存、延迟综合评估
            cpu_score = max(0, 1.0 - data.get('cpu_usage', 0) / 100.0)
            mem_score = max(0, 1.0 - data.get('memory_usage', 0) / 2048.0)  # 2GB限制
            latency_score = max(0, 1.0 - data.get('topic_latency', 0) / 100.0)  # 100ms限制
            score = (cpu_score + mem_score + latency_score) / 3.0

        return max(0.0, min(1.0, score))

    def _store_health_data(self, health_data: Dict, overall_health: str):
        """存储健康数据"""
        with self.data_lock:
            # 添加到历史记录
            record = {
                'timestamp': health_data['timestamp'],
                'overall_health': overall_health,
                'details': health_data
            }

            self.health_history.append(record)

            # 清理过期数据
            cutoff_time = time.time() - self.history_duration
            self.health_history = [
                record for record in self.health_history
                if record['timestamp'] > cutoff_time
            ]

    def _publish_health_status(self, health_data: Dict, overall_health: str):
        """发布健康状态"""
        msg = SystemHealth()
        msg.header.stamp = self.node.get_clock().now().to_msg()
        msg.overall_health = overall_health

        # 将健康数据转换为JSON格式
        import json
        metrics_data = {}

        for component, data in health_data.items():
            if component == 'timestamp':
                continue

            metrics_data[component] = {}
            for metric_name, value in data.items():
                metrics_data[component][metric_name] = {
                    'value': float(value),
                    'unit': self._get_metric_unit(component, metric_name),
                    'status': self._get_metric_status(component, metric_name, value)
                }

        msg.health_metrics_json = json.dumps(metrics_data, ensure_ascii=False)

        # 检查告警并添加到告警列表
        active_warnings = []
        active_errors = []

        for component, data in health_data.items():
            if component == 'timestamp':
                continue

            for metric_name, value in data.items():
                status = self._get_metric_status(component, metric_name, value)
                if status == 'WARNING':
                    active_warnings.append(f"{component}.{metric_name}: {value}")
                elif status in ['ERROR', 'CRITICAL']:
                    active_errors.append(f"{component}.{metric_name}: {value}")

        msg.active_warnings = active_warnings
        msg.active_errors = active_errors

        self.health_publisher.publish(msg)

    def _get_metric_unit(self, component: str, metric_name: str) -> str:
        """获取指标单位"""
        units = {
            'navigation': {
                'amcl_frequency': 'Hz',
                'planning_success_rate': '%',
                'plan_attempts': 'count',
                'plan_successes': 'count'
            },
            'perception': {
                'rfid_frequency': 'Hz',
                'detection_success_rate': '%',
                'scan_attempts': 'count',
                'successful_scans': 'count'
            },
            'resource': {
                'cpu_usage': '%',
                'memory_usage': 'MB',
                'topic_latency': 'ms'
            },
            'system': {
                'node_count': 'count',
                'connection_status': 'status'
            }
        }

        return units.get(component, {}).get(metric_name, 'unknown')

    def _get_metric_status(self, component: str, metric_name: str, value: float) -> str:
        """获取指标状态"""
        thresholds = self.thresholds.get(component, {})
        threshold = thresholds.get(metric_name)

        if not threshold:
            return 'NORMAL'

        if value >= threshold.critical_threshold:
            return 'CRITICAL'
        elif value >= threshold.error_threshold:
            return 'ERROR'
        elif value >= threshold.warning_threshold:
            return 'WARNING'
        else:
            return 'NORMAL'

    def _check_alerts(self, health_data: Dict):
        """检查告警条件"""
        for component, data in health_data.items():
            if component == 'timestamp':
                continue

            thresholds = self.thresholds.get(component, {})

            for metric_name, value in data.items():
                if metric_name in thresholds:
                    threshold = thresholds[metric_name]

                    if value >= threshold.critical_threshold:
                        self._trigger_alert(component, metric_name, value, 'CRITICAL')
                    elif value >= threshold.error_threshold:
                        self._trigger_alert(component, metric_name, value, 'ERROR')
                    elif value >= threshold.warning_threshold:
                        self._trigger_alert(component, metric_name, value, 'WARNING')

    def _trigger_alert(self, component: str, metric: str, value: float, level: str):
        """触发告警"""
        message = f"{component} {metric} = {value} ({level})"

        if level == 'CRITICAL':
            self.node.get_logger().fatal(message)
        elif level == 'ERROR':
            self.node.get_logger().error(message)
        elif level == 'WARNING':
            self.node.get_logger().warn(message)

    def _health_report_callback(self, request, response):
        """健康报告服务回调"""
        try:
            # 生成健康报告
            from .health_reporter import HealthReporter

            reporter = HealthReporter(self.health_history)
            report = reporter.generate_report(request.duration_seconds)

            response.success = True
            response.overall_health = self._get_current_overall_health()
            response.report_time = datetime.now().isoformat()
            response.report_json = json.dumps(report, ensure_ascii=False)

        except Exception as e:
            self.node.get_logger().error(f"生成健康报告错误: {str(e)}")
            response.success = False
            response.message = str(e)
            response.report_json = "{}"

        return response

    def _get_current_overall_health(self) -> str:
        """获取当前整体健康状态"""
        if not self.health_history:
            return 'UNKNOWN'

        return self.health_history[-1]['overall_health']

    def _load_thresholds(self) -> Dict:
        """加载健康阈值配置"""
        # 默认阈值配置
        return {
            'navigation': {
                'amcl_frequency': HealthThreshold(5.0, 3.0, 1.0),
                'planning_success_rate': HealthThreshold(95.0, 85.0, 70.0)
            },
            'perception': {
                'rfid_frequency': HealthThreshold(9.0, 7.0, 5.0),
                'detection_success_rate': HealthThreshold(90.0, 80.0, 60.0)
            },
            'resource': {
                'cpu_usage': HealthThreshold(70.0, 85.0, 95.0),
                'memory_usage': HealthThreshold(1536.0, 1792.0, 1920.0),  # MB
                'topic_latency': HealthThreshold(50.0, 100.0, 200.0)  # ms
            }
        }
