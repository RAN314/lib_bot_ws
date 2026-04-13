#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统健康检测器 - 检测系统级问题
实现节点健康、资源使用、通信等检测
"""

import rclpy
from rclpy.node import Node
import time
import psutil
import threading
from rcl_interfaces.msg import ParameterEvent


class SystemHealthDetector:
    """系统健康检测器 - 检测系统级问题"""

    def __init__(self, node: Node):
        """初始化系统健康检测器"""
        self.node = node
        self.node_health_timeout = 10.0        # 节点健康超时(秒)
        self.memory_usage_threshold = 0.9      # 内存使用率阈值(90%)
        self.cpu_usage_threshold = 0.8         # CPU使用率阈值(80%)
        self.communication_timeout = 2.0       # 通信超时(秒)

        # 状态跟踪
        self.node_last_seen = {}
        self.parameter_events = []
        self.max_parameter_history = 100
        self.last_system_check = None

        # 从参数服务器加载配置
        self._load_parameters()

        # 订阅参数事件
        self.param_sub = node.create_subscription(
            ParameterEvent,
            '/parameter_events',
            self._parameter_callback,
            10
        )

    def _load_parameters(self):
        """加载检测参数"""
        try:
            self.node_health_timeout = self.node.declare_parameter(
                'detection.system.node_health_timeout', 10.0
            ).value
            self.memory_usage_threshold = self.node.declare_parameter(
                'detection.system.memory_usage_threshold', 0.9
            ).value
            self.cpu_usage_threshold = self.node.declare_parameter(
                'detection.system.cpu_usage_threshold', 0.8
            ).value
            self.communication_timeout = self.node.declare_parameter(
                'detection.system.communication_timeout', 2.0
            ).value

            self.node.get_logger().info("系统检测器参数加载完成")
        except Exception as e:
            self.node.get_logger().warn(f"系统检测器参数加载失败: {str(e)}")

    def detect(self) -> list:
        """执行系统健康检测

        Returns:
            检测到的错误列表
        """
        errors = []

        # 检测内存使用
        errors.extend(self._check_memory_usage())

        # 检测CPU使用
        errors.extend(self._check_cpu_usage())

        # 检测节点健康
        errors.extend(self._check_node_health())

        # 检测通信超时
        errors.extend(self._check_communication_timeout())

        # 检测系统资源
        errors.extend(self._check_system_resources())

        return errors

    def _parameter_callback(self, msg: ParameterEvent):
        """参数事件回调"""
        current_time = time.time()

        # 记录参数事件
        event_info = {
            'timestamp': current_time,
            'node': msg.node,
            'parameters': len(msg.changed_parameters)
        }

        self.parameter_events.append(event_info)

        # 保持历史记录大小
        if len(self.parameter_events) > self.max_parameter_history:
            self.parameter_events.pop(0)

        # 更新节点最后活跃时间
        self.node_last_seen[msg.node] = current_time

    def _check_memory_usage(self) -> list:
        """检查内存使用"""
        errors = []

        try:
            # 获取当前进程内存使用
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()

            # 检查内存使用率是否超过阈值
            if memory_percent > self.memory_usage_threshold * 100:
                errors.append({
                    'error_type': 'memory_exhausted',
                    'message': f'内存使用率过高: {memory_percent:.1f}%',
                    'memory_percent': memory_percent,
                    'memory_rss': memory_info.rss,
                    'threshold': self.memory_usage_threshold * 100
                })

            # 检查系统内存使用
            system_memory = psutil.virtual_memory()
            if system_memory.percent > 95:  # 系统内存超过95%
                errors.append({
                    'error_type': 'memory_exhausted',
                    'message': f'系统内存使用率过高: {system_memory.percent:.1f}%',
                    'memory_percent': system_memory.percent,
                    'memory_available': system_memory.available,
                    'threshold': 95.0
                })

        except Exception as e:
            self.node.get_logger().error(f"内存检查失败: {str(e)}")

        return errors

    def _check_cpu_usage(self) -> list:
        """检查CPU使用"""
        errors = []

        try:
            # 获取当前进程CPU使用
            process = psutil.Process()
            cpu_percent = process.cpu_percent(interval=0.1)

            # 检查CPU使用率是否超过阈值
            if cpu_percent > self.cpu_usage_threshold * 100:
                errors.append({
                    'error_type': 'cpu_overload',
                    'message': f'CPU使用率过高: {cpu_percent:.1f}%',
                    'cpu_percent': cpu_percent,
                    'threshold': self.cpu_usage_threshold * 100
                })

            # 检查系统CPU使用
            system_cpu = psutil.cpu_percent(interval=0.1)
            if system_cpu > 90:  # 系统CPU超过90%
                errors.append({
                    'error_type': 'cpu_overload',
                    'message': f'系统CPU使用率过高: {system_cpu:.1f}%',
                    'cpu_percent': system_cpu,
                    'threshold': 90.0
                })

        except Exception as e:
            self.node.get_logger().error(f"CPU检查失败: {str(e)}")

        return errors

    def _check_node_health(self) -> list:
        """检查节点健康状态"""
        errors = []
        current_time = time.time()

        # 检查已知节点的健康状态
        for node_name, last_seen in self.node_last_seen.items():
            time_since_seen = current_time - last_seen

            if time_since_seen > self.node_health_timeout:
                # 确定错误严重程度
                if time_since_seen > self.node_health_timeout * 3:
                    severity = 'Fatal'
                    error_type = 'node_crash'
                else:
                    severity = 'Critical'
                    error_type = 'communication_timeout'

                errors.append({
                    'error_type': error_type,
                    'message': f'节点通信超时: {node_name} ({time_since_seen:.1f}秒)',
                    'node_name': node_name,
                    'time_since_seen': time_since_seen,
                    'timeout_threshold': self.node_health_timeout
                })

        return errors

    def _check_communication_timeout(self) -> list:
        """检查通信超时"""
        errors = []
        current_time = time.time()

        # 检查参数通信频率
        if self.parameter_events:
            recent_events = [event for event in self.parameter_events
                           if current_time - event['timestamp'] < self.communication_timeout]

            # 如果通信超时内没有参数事件，可能是通信问题
            if not recent_events and current_time > 10.0:  # 启动10秒后检查
                # 但这不一定是错误，因为参数可能不经常变化
                pass

        return errors

    def _check_system_resources(self) -> list:
        """检查系统资源"""
        errors = []

        try:
            # 检查磁盘空间
            disk_usage = psutil.disk_usage('/')
            if disk_usage.percent > 95:
                errors.append({
                    'error_type': 'system_resource_low',
                    'message': f'磁盘空间不足: {disk_usage.percent:.1f}%',
                    'disk_percent': disk_usage.percent,
                    'disk_free': disk_usage.free
                })

            # 检查文件描述符
            process = psutil.Process()
            fd_count = process.num_fds()
            if fd_count > 1000:  # 文件描述符过多
                errors.append({
                    'error_type': 'system_resource_low',
                    'message': f'文件描述符使用过多: {fd_count}',
                    'fd_count': fd_count
                })

            # 检查线程数
            thread_count = process.num_threads()
            if thread_count > 100:  # 线程过多
                errors.append({
                    'error_type': 'system_resource_low',
                    'message': f'线程数过多: {thread_count}',
                    'thread_count': thread_count
                })

        except Exception as e:
            self.node.get_logger().error(f"系统资源检查失败: {str(e)}")

        return errors

    def register_node_activity(self, node_name: str):
        """注册节点活动（用于手动跟踪节点）"""
        self.node_last_seen[node_name] = time.time()

    def get_status(self) -> dict:
        """获取检测器状态"""
        try:
            process = psutil.Process()
            system_memory = psutil.virtual_memory()
            system_cpu = psutil.cpu_percent(interval=0.1)

            status = {
                'memory_percent': process.memory_percent(),
                'cpu_percent': process.cpu_percent(interval=0.0),
                'system_memory_percent': system_memory.percent,
                'system_cpu_percent': system_cpu,
                'node_count': len(self.node_last_seen),
                'parameter_events': len(self.parameter_events),
                'last_check': self.last_system_check,
                'memory_threshold': self.memory_usage_threshold,
                'cpu_threshold': self.cpu_usage_threshold,
                'node_timeout': self.node_health_timeout
            }
        except Exception as e:
            status = {'error': str(e)}

        return status

    def reset(self):
        """重置检测器"""
        self.node_last_seen.clear()
        self.parameter_events.clear()
        self.last_system_check = None
        self.node.get_logger().info("系统健康检测器已重置")


def main():
    """测试函数"""
    import rclpy

    rclpy.init()

    # 创建测试节点
    test_node = Node("system_detector_test")

    # 创建系统检测器实例
    detector = SystemHealthDetector(test_node)

    try:
        print("🧪 系统健康检测器测试")
        print("监控系统资源...")

        # 运行测试10秒
        start_time = time.time()
        while time.time() - start_time < 10.0:
            rclpy.spin_once(test_node, timeout_sec=0.5)

            # 执行检测
            errors = detector.detect()
            if errors:
                for error in errors:
                    print(f"检测到系统错误: {error}")

            time.sleep(1.0)  # 每秒检测一次

    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
    finally:
        # 清理
        test_node.destroy_node()
        rclpy.shutdown()

    print("✅ 系统健康检测器测试完成")


if __name__ == "__main__":
    main()