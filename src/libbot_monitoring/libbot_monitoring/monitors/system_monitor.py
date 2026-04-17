# system_monitor.py

import rclpy
from rclpy.node import Node
import time
from typing import Dict, List


class SystemMonitor:
    """系统状态监控"""

    def __init__(self, node: Node):
        self.node = node

        # 节点状态
        self.known_nodes = set()
        self.node_status = {}

        # 话题状态
        self.known_topics = set()
        self.topic_status = {}

        # 服务状态
        self.known_services = set()
        self.service_status = {}

        # 上一次检查时间
        self.last_check_time = 0

    def start(self):
        """启动系统监控"""
        self._discover_system_components()
        self.node.get_logger().info("系统监控组件启动")

    def stop(self):
        """停止系统监控"""
        self.node.get_logger().info("系统监控组件停止")

    def _discover_system_components(self):
        """发现系统中的组件"""
        try:
            # 发现节点
            node_names = self.node.get_node_names()
            self.known_nodes = set(node_names)

            # 发现话题
            topic_names_and_types = self.node.get_topic_names_and_types()
            self.known_topics = set([name for name, _ in topic_names_and_types])

            # 发现服务
            service_names_and_types = self.node.get_service_names_and_types()
            self.known_services = set([name for name, _ in service_names_and_types])

        except Exception as e:
            self.node.get_logger().warn(f"系统组件发现失败: {str(e)}")

    def get_health_data(self) -> Dict:
        """获取系统健康数据"""
        current_time = time.time()

        # 更新系统组件状态
        self._update_node_status()
        self._update_topic_status()
        self._update_service_status()

        # 计算系统健康指标
        node_health = self._calculate_node_health()
        topic_health = self._calculate_topic_health()
        service_health = self._calculate_service_health()
        connection_health = self._check_connections()

        return {
            'node_count': len(self.known_nodes),
            'active_nodes': len([n for n, status in self.node_status.items() if status == 'active']),
            'topic_count': len(self.known_topics),
            'active_topics': len([t for t, status in self.topic_status.items() if status == 'active']),
            'service_count': len(self.known_services),
            'active_services': len([s for s, status in self.service_status.items() if status == 'active']),
            'node_health': node_health,
            'topic_health': topic_health,
            'service_health': service_health,
            'connection_status': connection_health,
            'last_check_time': current_time
        }

    def _update_node_status(self):
        """更新节点状态"""
        try:
            current_nodes = set(self.node.get_node_names())

            # 检查节点活跃状态
            for node_name in self.known_nodes:
                if node_name in current_nodes:
                    # 简单的活跃性检查
                    try:
                        # 检查节点是否响应
                        node_info = self.node.get_publishers_info_by_topic(node_name)
                        self.node_status[node_name] = 'active'
                    except Exception:
                        self.node_status[node_name] = 'inactive'
                else:
                    self.node_status[node_name] = 'offline'

            # 添加新发现的节点
            for node_name in current_nodes:
                if node_name not in self.known_nodes:
                    self.known_nodes.add(node_name)
                    self.node_status[node_name] = 'active'

        except Exception as e:
            self.node.get_logger().warn(f"节点状态更新失败: {str(e)}")

    def _update_topic_status(self):
        """更新话题状态"""
        try:
            current_topics = set([name for name, _ in self.node.get_topic_names_and_types()])

            for topic_name in self.known_topics:
                if topic_name in current_topics:
                    # 检查话题是否有发布者和订阅者
                    try:
                        pub_info = self.node.get_publishers_info_by_topic(topic_name)
                        sub_info = self.node.get_subscribers_info_by_topic(topic_name)

                        if len(pub_info) > 0 and len(sub_info) > 0:
                            self.topic_status[topic_name] = 'active'
                        elif len(pub_info) > 0:
                            self.topic_status[topic_name] = 'publisher_only'
                        elif len(sub_info) > 0:
                            self.topic_status[topic_name] = 'subscriber_only'
                        else:
                            self.topic_status[topic_name] = 'idle'
                    except Exception:
                        self.topic_status[topic_name] = 'error'
                else:
                    self.topic_status[topic_name] = 'offline'

            # 添加新发现的话题
            for topic_name in current_topics:
                if topic_name not in self.known_topics:
                    self.known_topics.add(topic_name)
                    self.topic_status[topic_name] = 'active'

        except Exception as e:
            self.node.get_logger().warn(f"话题状态更新失败: {str(e)}")

    def _update_service_status(self):
        """更新服务状态"""
        try:
            current_services = set([name for name, _ in self.node.get_service_names_and_types()])

            for service_name in self.known_services:
                if service_name in current_services:
                    # 简单的服务可用性检查
                    try:
                        # 这里可以添加实际的服务调用测试
                        self.service_status[service_name] = 'active'
                    except Exception:
                        self.service_status[service_name] = 'inactive'
                else:
                    self.service_status[service_name] = 'offline'

            # 添加新发现的服务
            for service_name in current_services:
                if service_name not in self.known_services:
                    self.known_services.add(service_name)
                    self.service_status[service_name] = 'active'

        except Exception as e:
            self.node.get_logger().warn(f"服务状态更新失败: {str(e)}")

    def _calculate_node_health(self) -> float:
        """计算节点健康度"""
        if not self.node_status:
            return 100.0

        active_count = len([status for status in self.node_status.values() if status == 'active'])
        return (active_count / len(self.node_status)) * 100.0

    def _calculate_topic_health(self) -> float:
        """计算话题健康度"""
        if not self.topic_status:
            return 100.0

        active_count = len([status for status in self.topic_status.values() if status == 'active'])
        return (active_count / len(self.topic_status)) * 100.0

    def _calculate_service_health(self) -> float:
        """计算服务健康度"""
        if not self.service_status:
            return 100.0

        active_count = len([status for status in self.service_status.values() if status == 'active'])
        return (active_count / len(self.service_status)) * 100.0

    def _check_connections(self) -> str:
        """检查系统连接状态"""
        total_components = len(self.known_nodes) + len(self.known_topics) + len(self.known_services)

        if total_components == 0:
            return 'UNKNOWN'

        active_components = (
            len([s for s in self.node_status.values() if s == 'active']) +
            len([s for s in self.topic_status.values() if s == 'active']) +
            len([s for s in self.service_status.values() if s == 'active'])
        )

        connection_ratio = active_components / total_components

        if connection_ratio >= 0.9:
            return 'EXCELLENT'
        elif connection_ratio >= 0.7:
            return 'GOOD'
        elif connection_ratio >= 0.5:
            return 'FAIR'
        else:
            return 'POOR'

    def get_system_summary(self) -> Dict:
        """获取系统摘要信息"""
        return {
            'nodes': {
                'total': len(self.known_nodes),
                'active': len([s for s in self.node_status.values() if s == 'active']),
                'inactive': len([s for s in self.node_status.values() if s == 'inactive']),
                'offline': len([s for s in self.node_status.values() if s == 'offline'])
            },
            'topics': {
                'total': len(self.known_topics),
                'active': len([s for s in self.topic_status.values() if s == 'active']),
                'idle': len([s for s in self.topic_status.values() if s == 'idle']),
                'offline': len([s for s in self.topic_status.values() if s == 'offline'])
            },
            'services': {
                'total': len(self.known_services),
                'active': len([s for s in self.service_status.values() if s == 'active']),
                'inactive': len([s for s in self.service_status.values() if s == 'inactive']),
                'offline': len([s for s in self.service_status.values() if s == 'offline'])
            }
        }
