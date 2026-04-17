#!/usr/bin/env python3
"""
LibBot混合日志系统使用示例
"""

import time
import json
from libbot_logging import HybridLogger, QueryInterface
import yaml


def load_config():
    """加载配置文件"""
    with open('libbot_logging/config/logging_config.yaml', 'r') as f:
        return yaml.safe_load(f)


def main():
    """主要演示函数"""
    print("=== LibBot混合日志系统演示 ===\n")

    # 1. 初始化日志系统
    print("1. 初始化日志系统...")
    config = load_config()
    logger = HybridLogger(config)
    query_interface = QueryInterface(logger)

    print("   ✓ 混合日志管理器已创建")
    print("   ✓ ROS2日志处理器已配置")
    print("   ✓ SQLite日志存储已准备")
    print("   ✓ 日志缓冲区已启动\n")

    # 2. 记录系统日志
    print("2. 记录系统日志...")
    logger.log_system('INFO', '系统启动完成', 'System')
    logger.log_system('DEBUG', '初始化传感器', 'Perception')
    logger.log_system('WARN', '网络连接不稳定', 'Communication')
    logger.log_system('ERROR', '数据库连接失败', 'Database')
    print("   ✓ 系统日志已记录\n")

    # 3. 记录业务日志
    print("3. 记录业务日志...")
    logger.log_business(
        operation='book_search',
        details={
            'book_id': 'B001',
            'title': '机器人学导论',
            'search_method': 'rfid'
        },
        result='success',
        component='BookManager'
    )

    logger.log_business(
        operation='navigation',
        details={
            'destination': 'A区-3层-12架',
            'path_length': 45.6,
            'estimated_time': 120
        },
        result='success',
        component='Navigation'
    )

    logger.log_business(
        operation='book_pickup',
        details={
            'book_id': 'B001',
            'position': {'x': 12.5, 'y': 3.2, 'z': 1.1},
            'gripper_status': 'success'
        },
        result='failed',
        component='Manipulator'
    )
    print("   ✓ 业务日志已记录\n")

    # 4. 等待一会儿，让日志写入
    print("4. 等待日志处理...")
    time.sleep(2)
    logger.flush_buffer()
    print("   ✓ 缓冲区已刷新\n")

    # 5. 查询演示
    print("5. 日志查询演示...")

    # 查询所有错误日志
    print("   5.1 查询错误日志:")
    errors = query_interface.get_recent_errors(hours=1)
    for error in errors[:3]:  # 只显示前3条
        print(f"     - [{error['level']}] {error['component']}: {error['message']}")

    # 搜索特定内容
    print("   5.2 搜索'book'相关日志:")
    book_logs = query_interface.search('book', hours=1)
    for log in book_logs[:3]:
        print(f"     - [{log['log_type']}] {log['component']}: {log['message']}")

    # 获取系统状态摘要
    print("   5.3 系统状态摘要:")
    summary = query_interface.get_system_status_summary(hours=1)
    print(f"     - 系统日志: {summary['system_logs']['total']} 条")
    print(f"     - 业务日志: {summary['business_logs']['total']} 条")
    print(f"     - 成功率: {summary['business_logs']['success_rate']:.1f}%")
    print()

    # 6. 统计信息
    print("6. 系统统计信息:")
    stats = logger.get_statistics()
    buffer_stats = stats['buffer_stats']
    sqlite_stats = stats['sqlite_stats']

    print(f"   - 缓冲区使用率: {buffer_stats['utilization']:.1%}")
    print(f"   - 总日志数: {sqlite_stats['total_logs']}")
    print(f"   - 数据库大小: {sqlite_stats['database_size_bytes']} bytes")
    print(f"   - 队列大小: {sqlite_stats['queue_size']}")
    print()

    print("=== 演示完成 ===")


if __name__ == '__main__':
    main()