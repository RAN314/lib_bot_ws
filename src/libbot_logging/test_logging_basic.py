#!/usr/bin/env python3
"""
LibBot日志系统基础测试
"""

import os
import sys
import time
import tempfile
import shutil

# 添加包路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from libbot_logging import HybridLogger, SQLiteLogger, LogBuffer
import json


def test_sqlite_logger():
    """测试SQLite日志功能"""
    print("测试SQLite日志...")

    # 创建临时数据库
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test.db')

    try:
        config = {'database_path': db_path, 'batch_size': 5}
        logger = SQLiteLogger(config)

        # 测试业务日志
        logger.log_operation('test_operation', {'param': 'value'}, 'success', 'TestComponent')
        logger.log_operation('another_operation', {'data': 123}, 'failed', 'TestComponent')

        # 手动刷新
        logger.flush()

        # 查询日志
        logs = logger.query_logs({'limit': 10})
        assert len(logs) >= 2, f"期望至少2条日志，实际得到{len(logs)}条"

        print("   ✓ SQLite日志测试通过")

    finally:
        shutil.rmtree(temp_dir)


def test_log_buffer():
    """测试日志缓冲区"""
    print("测试日志缓冲区...")

    config = {'max_size': 10, 'flush_interval': 1.0}
    buffer = LogBuffer(config)

    # 添加日志
    for i in range(5):
        buffer.add_log('system', 'INFO', f'Test message {i}', f'Component{i%2}')

    # 查询日志
    logs = buffer.query_logs({'limit': 10})
    assert len(logs) == 5, f"期望5条日志，实际得到{len(logs)}条"

    # 测试过滤器
    component_logs = buffer.query_logs({'component': 'Component0', 'limit': 10})
    assert len(component_logs) == 3, f"期望3条Component0日志，实际得到{len(component_logs)}条"

    print("   ✓ 日志缓冲区测试通过")


def test_hybrid_logger():
    """测试混合日志管理器"""
    print("测试混合日志管理器...")

    # 创建临时数据库
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test.db')

    try:
        config = {
            'sqlite': {'database_path': db_path, 'batch_size': 5},
            'buffer': {'max_size': 100, 'flush_interval': 1.0},
            'ros2': {'min_level': 'INFO'}
        }

        logger = HybridLogger(config)

        # 记录系统日志
        logger.log_system('INFO', 'System started', 'System')
        logger.log_system('ERROR', 'Something went wrong', 'TestComponent')

        # 记录业务日志
        logger.log_business('test_operation', {'test': 'data'}, 'success', 'TestComponent')

        # 查询日志
        logs = logger.query_logs(limit=10)

        print(f"   ✓ 混合日志管理器测试通过，共{len(logs)}条日志")

    finally:
        shutil.rmtree(temp_dir)


def main():
    """运行所有测试"""
    print("=== LibBot日志系统测试 ===\n")

    try:
        test_sqlite_logger()
        test_log_buffer()
        test_hybrid_logger()

        print("\n=== 所有测试通过！ ===")
        return 0

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())