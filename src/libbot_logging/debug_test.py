#!/usr/bin/env python3
"""
调试测试，避免批量写入问题
"""

import time
import os
import tempfile
from libbot_logging import SQLiteLogger


def debug_sqlite_only():
    print("=== SQLite调试测试 ===")

    # 创建临时数据库
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'debug.db')

    try:
        print(f"数据库路径: {db_path}")

        # 创建SQLiteLogger，禁用批量写入
        config = {
            'database_path': db_path,
            'batch_size': 1000,  # 很大的批量，不会自动触发
        }

        logger = SQLiteLogger(config)
        print("✓ SQLiteLogger创建成功")

        # 测试直接写入
        print("\n测试直接写入...")
        logger._insert_log_direct({
            'timestamp': time.time(),
            'log_type': 'test',
            'level': 'INFO',
            'message': 'Direct test message',
            'component': 'TestComponent',
            'details': '{"test": true}'
        })
        print("✓ 直接写入成功")

        # 测试查询
        print("\n测试查询...")
        logs = logger.query_logs({'limit': 10})
        print(f"✓ 查询成功，找到{len(logs)}条日志")

        # 显示日志内容
        for log in logs:
            print(f"  - {log.get('level')}: {log.get('message')}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理
        import shutil
        shutil.rmtree(temp_dir)
        print(f"\n清理完成: {temp_dir}")


if __name__ == '__main__':
    debug_sqlite_only()