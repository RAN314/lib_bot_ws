#!/usr/bin/env python3
"""
修复版本的持久化演示
"""

import time
import os
import yaml
from libbot_logging import HybridLogger, QueryInterface


def main():
    print("=== LibBot日志系统持久化演示（修复版） ===\n")

    # 使用当前目录的数据库
    config = {
        'sqlite': {
            'database_path': 'fixed_demo_logs.db',
            'batch_size': 100  # 增大批量大小，避免自动触发
        },
        'buffer': {
            'max_size': 100,
            'flush_interval': 2.0
        },
        'ros2': {
            'min_level': 'INFO'
        }
    }

    # 初始化日志系统
    print("1. 初始化日志系统...")
    logger = HybridLogger(config)
    query_interface = QueryInterface(logger)
    print("   ✓ 日志系统已初始化\n")

    # 记录一些日志
    print("2. 记录日志...")

    # 业务日志（直接写入SQLite队列）
    for i in range(3):  # 减少日志数量，避免触发批量写入
        print(f"   记录业务日志 {i+1}/3...")
        logger.log_business(
            operation=f'operation_{i}',
            details={
                'iteration': i,
                'data': f'test_data_{i}',
                'timestamp': time.time()
            },
            result='success' if i % 2 == 0 else 'failed',
            component='DemoComponent'
        )
        print(f"   ✓ 业务日志 {i+1} 已记录")

    # 立即刷新SQLite队列
    print("   刷新SQLite队列...")
    logger.sqlite_logger.flush()
    print("   ✓ SQLite队列已刷新")

    # 系统日志（写入缓冲区）
    print("   记录系统日志...")
    logger.log_system('INFO', '演示程序启动', 'Demo')
    logger.log_system('DEBUG', '调试信息', 'Demo')
    logger.log_system('WARN', '警告信息', 'Demo')
    logger.log_system('ERROR', '错误信息', 'Demo')
    print("   ✓ 系统日志已记录\n")

    print("   ✓ 所有日志已记录\n")

    # 等待并刷新
    print("3. 刷新缓冲区...")
    time.sleep(0.5)  # 减少等待时间
    logger.flush_buffer()
    print("   ✓ 缓冲区已刷新\n")

    # 查询日志
    print("4. 查询日志...")

    # 查询所有日志
    all_logs = query_interface.logger.sqlite_logger.query_logs({'limit': 20})
    print(f"   总日志数: {len(all_logs)}")

    # 显示前几条日志
    for i, log in enumerate(all_logs[:5]):
        print(f"   {i+1}. [{log.get('level', 'UNKNOWN')}] {log.get('component', 'unknown')}: {log.get('message', '')}")

    print()

    # 查询错误日志
    print("5. 查询错误日志...")
    error_logs = query_interface.get_recent_errors(hours=1)
    print(f"   错误日志数: {len(error_logs)}")

    # 搜索日志
    print("6. 搜索日志...")
    search_results = query_interface.search('operation', hours=1)
    print(f"   搜索'operation'结果: {len(search_results)}条")

    # 系统状态
    print("7. 系统状态...")
    summary = query_interface.get_system_status_summary(hours=1)
    print(f"   系统日志: {summary['system_logs']['total']}条")
    print(f"   业务日志: {summary['business_logs']['total']}条")
    print(f"   成功率: {summary['business_logs']['success_rate']:.1f}%")

    # 统计信息
    print("\n8. 统计信息...")
    stats = logger.get_statistics()
    print(f"   缓冲区使用率: {stats['buffer_stats']['utilization']:.1%}")
    print(f"   数据库总日志: {stats['sqlite_stats']['total_logs']}条")
    print(f"   数据库大小: {stats['sqlite_stats']['database_size_bytes']} bytes")

    print("\n=== 演示完成 ===")
    print(f"数据库文件: {config['sqlite']['database_path']}")


if __name__ == '__main__':
    main()