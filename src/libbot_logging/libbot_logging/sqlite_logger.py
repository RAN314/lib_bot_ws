#!/usr/bin/env python3
"""
SQLite业务日志存储

负责将业务操作日志持久化存储到SQLite数据库，提供高效的查询功能。
"""

import sqlite3
import json
import time
import threading
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import os
import logging
from pathlib import Path


class SQLiteLogger:
    """SQLite业务日志管理器"""

    def __init__(self, config: Dict):
        """
        初始化SQLite日志管理器

        Args:
            config: SQLite配置字典
        """
        self.db_path = config.get('database_path', 'library.db')
        self.batch_size = config.get('batch_size', 100)
        self.max_log_age = config.get('max_log_age', 30)  # 天

        # 确保数据库目录存在
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else '.', exist_ok=True)

        self._lock = threading.RLock()
        self._init_database()

        # 批量写入队列
        self._write_queue = []
        self._queue_lock = threading.Lock()

        # 日志轮转器
        self.log_rotator = None
        self._init_log_rotation(config)

    def _init_database(self):
        """初始化数据库表结构"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()

                # 创建日志表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        log_type TEXT NOT NULL,
                        level TEXT NOT NULL,
                        message TEXT NOT NULL,
                        component TEXT,
                        details TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # 创建索引以提高查询性能
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_log_type ON logs(log_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_level ON logs(level)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_component ON logs(component)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON logs(created_at)')

                conn.commit()

            finally:
                conn.close()

    def log_operation(self, operation_type: str, details: dict, result: str = "success",
                     component: str = None):
        """
        业务操作日志记录

        Args:
            operation_type: 操作类型
            details: 操作详情（字典格式）
            result: 操作结果 (success/failed/warning)
            component: 组件名称
        """
        log_entry = {
            'timestamp': time.time(),
            'log_type': 'business',
            'level': 'INFO' if result == 'success' else 'ERROR',
            'message': f"Operation: {operation_type}, Result: {result}",
            'component': component or operation_type,
            'details': json.dumps(details, ensure_ascii=False)
        }

        self._add_to_queue(log_entry)

    def log_system_entry(self, timestamp: float, level: str, message: str,
                        component: str = None, details: dict = None):
        """
        系统日志条目记录

        Args:
            timestamp: 时间戳
            level: 日志级别
            message: 消息内容
            component: 组件名称
            details: 详细信息
        """
        log_entry = {
            'timestamp': timestamp,
            'log_type': 'system',
            'level': level,
            'message': message,
            'component': component,
            'details': json.dumps(details, ensure_ascii=False) if details else None
        }

        self._add_to_queue(log_entry)

    def _add_to_queue(self, log_entry: Dict):
        """添加日志到写入队列"""
        with self._queue_lock:
            self._write_queue.append(log_entry)

            # 如果队列达到批量大小，执行写入
            if len(self._write_queue) >= self.batch_size:
                self._flush_queue()

    def _flush_queue(self):
        """刷新队列到数据库"""
        with self._queue_lock:
            if not self._write_queue:
                return

            queue_to_flush = self._write_queue.copy()
            self._write_queue.clear()

        self._bulk_insert(queue_to_flush)

    def flush(self):
        """手动刷新队列"""
        self._flush_queue()

    def _bulk_insert(self, log_entries: List[Dict]):
        """批量插入日志条目"""
        if not log_entries:
            return

        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()

                insert_sql = '''
                    INSERT INTO logs (timestamp, log_type, level, message, component, details)
                    VALUES (?, ?, ?, ?, ?, ?)
                '''

                data = []
                for entry in log_entries:
                    data.append((
                        entry['timestamp'],
                        entry['log_type'],
                        entry['level'],
                        entry['message'],
                        entry.get('component'),
                        entry.get('details')
                    ))

                cursor.executemany(insert_sql, data)
                conn.commit()

            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()

    def _insert_log_direct(self, log_entry: Dict):
        """直接插入单条日志（紧急日志使用）"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()

                insert_sql = '''
                    INSERT INTO logs (timestamp, log_type, level, message, component, details)
                    VALUES (?, ?, ?, ?, ?, ?)
                '''

                cursor.execute(insert_sql, (
                    log_entry['timestamp'],
                    log_entry['log_type'],
                    log_entry['level'],
                    log_entry['message'],
                    log_entry.get('component'),
                    log_entry.get('details')
                ))

                conn.commit()

            finally:
                conn.close()

    def query_logs(self, filters: Dict) -> List[Dict]:
        """
        多维度日志查询

        Args:
            filters: 查询过滤器
                - log_type: 日志类型
                - level: 日志级别
                - component: 组件名称
                - start_time: 开始时间戳
                - end_time: 结束时间戳
                - limit: 返回结果数量限制
                - search_text: 搜索文本

        Returns:
            日志条目列表
        """
        query, params = self._build_query(filters)

        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, params)

                rows = cursor.fetchall()
                return [dict(row) for row in rows]

            finally:
                conn.close()

    def _build_query(self, filters: Dict) -> tuple:
        """构建查询SQL"""
        base_query = "SELECT * FROM logs WHERE 1=1"
        params = []

        # 日志类型过滤
        if filters.get('log_type') is not None:
            base_query += " AND log_type = ?"
            params.append(filters['log_type'])

        # 日志级别过滤
        if filters.get('level') is not None:
            base_query += " AND level = ?"
            params.append(filters['level'])

        # 组件过滤
        if filters.get('component') is not None:
            base_query += " AND component = ?"
            params.append(filters['component'])

        # 时间范围过滤
        if filters.get('start_time') is not None:
            base_query += " AND timestamp >= ?"
            params.append(float(filters['start_time']))

        if filters.get('end_time') is not None:
            base_query += " AND timestamp <= ?"
            params.append(float(filters['end_time']))

        # 文本搜索
        if filters.get('search_text'):
            base_query += " AND (message LIKE ? OR details LIKE ?)"
            search_pattern = f"%{filters['search_text']}%"
            params.extend([search_pattern, search_pattern])

        # 排序和限制
        base_query += " ORDER BY timestamp DESC"

        if filters.get('limit') is not None:
            base_query += " LIMIT ?"
            params.append(int(filters['limit']))

        return base_query, params

    def cleanup_old_logs(self, days: int = None):
        """
        清理旧日志

        Args:
            days: 保留天数，默认使用配置中的max_log_age
        """
        days = days or self.max_log_age
        cutoff_time = time.time() - (days * 24 * 3600)

        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM logs WHERE timestamp < ?", (cutoff_time,))
                deleted_count = cursor.rowcount
                conn.commit()
                return deleted_count

            finally:
                conn.close()

    def get_statistics(self) -> Dict:
        """获取日志统计信息"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()

                # 总日志数
                cursor.execute("SELECT COUNT(*) FROM logs")
                total_logs = cursor.fetchone()[0]

                # 按类型统计
                cursor.execute("SELECT log_type, COUNT(*) FROM logs GROUP BY log_type")
                type_stats = dict(cursor.fetchall())

                # 按级别统计
                cursor.execute("SELECT level, COUNT(*) FROM logs GROUP BY level")
                level_stats = dict(cursor.fetchall())

                # 数据库文件大小
                db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0

                return {
                    'total_logs': total_logs,
                    'type_breakdown': type_stats,
                    'level_breakdown': level_stats,
                    'database_size_bytes': db_size,
                    'queue_size': len(self._write_queue)
                }

            finally:
                conn.close()

    def close(self):
        """关闭日志管理器，确保所有日志都被写入"""
        self.flush()

        # 停止日志轮转
        if self.log_rotator:
            self.log_rotator.stop_rotation()

    def _init_log_rotation(self, config: Dict):
        """初始化日志轮转"""
        try:
            # 导入LogRotator
            from .log_rotator import LogRotator

            # 创建轮转配置
            rotation_config = {
                'ros2_log_dir': config.get('ros2_log_dir', '/var/log/ros'),
                'database_path': self.db_path,
                'check_interval': config.get('rotation_check_interval', 3600),
                'enable_compression': config.get('enable_compression', True),
                'storage_monitoring': {
                    'warning_threshold': config.get('storage_warning_threshold', 80),
                    'critical_threshold': config.get('storage_critical_threshold', 90),
                    'check_interval': config.get('storage_check_interval', 300)
                }
            }

            # 创建LogRotator实例
            self.log_rotator = LogRotator(rotation_config)
            self.logger = logging.getLogger(__name__)

            self.logger.info(f"日志轮转器初始化完成，数据库路径: {self.db_path}")

        except Exception as e:
            self.logger = logging.getLogger(__name__)
            self.logger.warning(f"日志轮转器初始化失败: {str(e)}，将继续运行但不启用自动轮转")
            self.log_rotator = None

    def start_log_rotation(self):
        """启动日志轮转"""
        if self.log_rotator:
            try:
                self.log_rotator.start_rotation()
                self.logger.info("日志轮转已启动")
            except Exception as e:
                self.logger.error(f"启动日志轮转失败: {str(e)}")

    def stop_log_rotation(self):
        """停止日志轮转"""
        if self.log_rotator:
            try:
                self.log_rotator.stop_rotation()
                self.logger.info("日志轮转已停止")
            except Exception as e:
                self.logger.error(f"停止日志轮转失败: {str(e)}")

    def manual_rotate_logs(self, log_type: str = 'sqlite_logs'):
        """手动触发日志轮转

        Args:
            log_type: 日志类型 (sqlite_logs/ros2_logs/all)
        """
        if self.log_rotator:
            try:
                self.log_rotator.manual_rotate(log_type)
                self.logger.info(f"手动轮转完成: {log_type}")
            except Exception as e:
                self.logger.error(f"手动轮转失败: {str(e)}")

    def manual_cleanup_logs(self, log_type: str = 'sqlite_logs'):
        """手动触发日志清理

        Args:
            log_type: 日志类型 (sqlite_logs/ros2_logs/all)
        """
        if self.log_rotator:
            try:
                self.log_rotator.manual_cleanup(log_type)
                self.logger.info(f"手动清理完成: {log_type}")
            except Exception as e:
                self.logger.error(f"手动清理失败: {str(e)}")

    def get_storage_info(self) -> Dict:
        """获取存储信息"""
        if self.log_rotator and hasattr(self.log_rotator, 'storage_monitor'):
            try:
                return self.log_rotator.storage_monitor.get_storage_usage()
            except Exception as e:
                self.logger.error(f"获取存储信息失败: {str(e)}")
                return {}
        return {}