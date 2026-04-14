#!/usr/bin/env python3
"""
LibBot日志系统演示ROS2节点

展示如何在ROS2节点中使用混合日志系统
"""

import rclpy
from rclpy.node import Node
import time
import threading
import yaml
import os

from libbot_logging import HybridLogger, QueryInterface


class LoggingDemoNode(Node):
    """日志演示ROS2节点"""

    def __init__(self):
        super().__init__('logging_demo_node')

        self.get_logger().info('正在初始化日志演示节点...')

        # 加载日志配置
        config_path = os.path.join(
            os.path.dirname(__file__),
            'libbot_logging',
            'config',
            'logging_config.yaml'
        )

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # 初始化混合日志系统
        self.logger = HybridLogger(config)
        self.logger.set_ros2_node(self)  # 设置ROS2节点引用
        self.query_interface = QueryInterface(self.logger)

        self.get_logger().info('混合日志系统已初始化')

        # 启动演示线程
        self.demo_thread = threading.Thread(target=self._demo_loop, daemon=True)
        self.demo_thread.start()

        # 创建定时器定期刷新缓冲区
        self.create_timer(5.0, self._flush_buffer)

        self.get_logger().info('日志演示节点启动完成')

    def _demo_loop(self):
        """演示循环"""
        counter = 0

        while rclpy.ok():
            try:
                # 模拟系统日志
                if counter % 10 == 0:
                    self.logger.log_system('INFO', f'系统运行正常 - 计数器: {counter}', 'System')

                if counter % 23 == 0:
                    self.logger.log_system('WARN', '检测到轻微延迟', 'Performance')

                if counter % 50 == 0:
                    self.logger.log_system('ERROR', '模拟错误发生', 'DemoComponent')

                # 模拟业务日志
                if counter % 7 == 0:
                    self.logger.log_business(
                        operation='data_processing',
                        details={
                            'processed_items': counter,
                            'processing_time': 0.123,
                            'memory_usage': 45.6
                        },
                        result='success',
                        component='DataProcessor'
                    )

                if counter % 15 == 0:
                    self.logger.log_business(
                        operation='sensor_reading',
                        details={
                            'sensor_id': 'RFID_001',
                            'readings': [1.2, 3.4, 5.6],
                            'quality': 'good'
                        },
                        result='success',
                        component='SensorManager'
                    )

                counter += 1
                time.sleep(1.0)

            except Exception as e:
                self.get_logger().error(f'演示循环错误: {e}')
                time.sleep(1.0)

    def _flush_buffer(self):
        """定期刷新缓冲区"""
        try:
            self.logger.flush_buffer()
            # self.get_logger().debug('日志缓冲区已刷新')
        except Exception as e:
            self.get_logger().error(f'刷新缓冲区失败: {e}')

    def demo_query(self):
        """演示查询功能"""
        self.get_logger().info('=== 日志查询演示 ===')

        # 查询最近的错误
        errors = self.query_interface.get_recent_errors(hours=1)
        self.get_logger().info(f'最近1小时的错误日志: {len(errors)}条')

        # 查询系统状态
        summary = self.query_interface.get_system_status_summary(hours=1)
        self.get_logger().info(f'系统状态: {summary["system_logs"]["total"]}条系统日志, '
                             f'{summary["business_logs"]["total"]}条业务日志')

        # 搜索特定内容
        search_results = self.query_interface.search('data', hours=1)
        self.get_logger().info(f'搜索"data"结果: {len(search_results)}条匹配日志')


def main(args=None):
    """主函数"""
    rclpy.init(args=args)

    try:
        node = LoggingDemoNode()

        # 运行ROS2循环
        rclpy.spin(node)

    except KeyboardInterrupt:
        print('\n用户中断，正在关闭...')

    except Exception as e:
        print(f'节点运行错误: {e}')

    finally:
        # 清理
        if 'node' in locals():
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()