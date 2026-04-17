#!/usr/bin/env python3
"""
简单测试，逐步诊断问题
"""

import time
import os
import yaml
from libbot_logging import HybridLogger


def step_by_step_test():
    print("=== 逐步测试 ===")

    # 步骤1: 初始化
    print("步骤1: 初始化日志系统...")
    config = {
        'sqlite': {
            'database_path': 'test_simple.db',
            'batch_size': 1  # 设置为1，立即写入
        },
        'buffer': {
            'max_size': 10,
            'flush_interval': 1.0
        },
        'ros2': {
            'min_level': 'INFO'
        }
    }

    logger = HybridLogger(config)
    print("✓ 初始化完成")

    # 步骤2: 记录一条业务日志
    print("\n步骤2: 记录业务日志...")
    logger.log_business(
        operation='simple_test',
        details={'test': 'data'},
        result='success',
        component='Test'
    )
    print("✓ 业务日志已记录")

    # 步骤3: 立即刷新
    print("\n步骤3: 刷新SQLite...")
    logger.sqlite_logger.flush()
    print("✓ SQLite已刷新")

    # 步骤4: 记录系统日志
    print("\n步骤4: 记录系统日志...")
    logger.log_system('INFO', 'Simple test', 'Test')
    print("✓ 系统日志已记录")

    # 步骤5: 刷新缓冲区
    print("\n步骤5: 刷新缓冲区...")
    logger.flush_buffer()
    print("✓ 缓冲区已刷新")

    # 步骤6: 查询
    print("\n步骤6: 查询日志...")
    logs = logger.sqlite_logger.query_logs({'limit': 5})
    print(f"✓ 查询完成，找到{len(logs)}条日志")

    print("\n=== 测试完成 ===")


if __name__ == '__main__':
    step_by_step_test()