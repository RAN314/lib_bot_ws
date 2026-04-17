#!/usr/bin/env python3
"""
日志缓冲区管理

提供内存中的日志缓冲功能，支持高性能写入和实时查询。
"""

import time
import threading
from collections import deque
from typing import Dict, List, Optional
from datetime import datetime


class LogBuffer:
    """日志缓冲区管理器"""

    def __init__(self, config: Dict):
        """
        初始化日志缓冲区

        Args:
            config: 缓冲区配置
        """
        self.max_size = config.get('max_size', 1000)  # 最大缓冲条目数
        self.flush_interval = config.get('flush_interval', 5.0)  # 自动刷新间隔（秒）

        # 使用双端队列实现循环缓冲区
        self._buffer = deque(maxlen=self.max_size)
        self._lock = threading.RLock()

        # 统计信息
        self._stats = {
            'total_added': 0,
            'total_flushed': 0,
            'overwritten': 0,
            'last_flush_time': time.time()
        }

        # 启动自动刷新线程
        self._flush_timer = None
        self._start_auto_flush()

    def add_log(self, log_type: str, level: str, message: str, component: str = None,
                timestamp: float = None):
        """
        添加日志到缓冲区

        Args:
            log_type: 日志类型 (system/business)
            level: 日志级别
            message: 日志消息
            component: 组件名称
            timestamp: 时间戳，默认为当前时间
        """
        with self._lock:
            timestamp = timestamp or time.time()

            log_entry = {
                'id': self._stats['total_added'] + 1,
                'timestamp': timestamp,
                'log_type': log_type,
                'level': level,
                'message': message,
                'component': component,
                'created_at': datetime.fromtimestamp(timestamp).isoformat()
            }

            # 检查是否因为缓冲区满而覆盖了旧日志
            if len(self._buffer) == self._buffer.maxlen:
                self._stats['overwritten'] += 1

            self._buffer.append(log_entry)
            self._stats['total_added'] += 1

    def query_logs(self, filters: Dict) -> List[Dict]:
        """
        从缓冲区查询日志

        Args:
            filters: 查询过滤器

        Returns:
            匹配的日志条目列表
        """
        with self._lock:
            logs = list(self._buffer)

        # 应用过滤器
        filtered_logs = []
        for log in logs:
            if self._matches_filters(log, filters):
                filtered_logs.append(log)

        # 按时间戳排序（最新的在前）
        filtered_logs.sort(key=lambda x: x['timestamp'], reverse=True)

        # 应用数量限制
        limit = filters.get('limit', 100)
        return filtered_logs[:limit]

    def _matches_filters(self, log_entry: Dict, filters: Dict) -> bool:
        """检查日志条目是否匹配过滤器"""
        # 日志类型过滤
        if filters.get('log_type') and log_entry['log_type'] != filters['log_type']:
            return False

        # 日志级别过滤
        if filters.get('level') and log_entry['level'] != filters['level']:
            return False

        # 组件过滤
        if filters.get('component') and log_entry.get('component') != filters['component']:
            return False

        # 时间范围过滤
        if filters.get('start_time') and log_entry['timestamp'] < filters['start_time']:
            return False

        if filters.get('end_time') and log_entry['timestamp'] > filters['end_time']:
            return False

        # 文本搜索
        if filters.get('search_text'):
            search_text = filters['search_text'].lower()
            message_match = search_text in log_entry['message'].lower()
            component_match = (log_entry.get('component') and
                             search_text in log_entry['component'].lower())

            if not (message_match or component_match):
                return False

        return True

    def flush_to_sqlite(self, sqlite_logger):
        """
        将缓冲区内容刷新到SQLite存储

        Args:
            sqlite_logger: SQLiteLogger实例
        """
        with self._lock:
            if not self._buffer:
                return

            # 复制当前缓冲区内容
            logs_to_flush = list(self._buffer)

            # 清空缓冲区
            self._buffer.clear()

            # 更新统计信息
            self._stats['total_flushed'] += len(logs_to_flush)
            self._stats['last_flush_time'] = time.time()

        # 写入SQLite（在锁外执行，避免长时间持有锁）
        for log_entry in logs_to_flush:
            try:
                sqlite_logger.log_system_entry(
                    timestamp=log_entry['timestamp'],
                    level=log_entry['level'],
                    message=log_entry['message'],
                    component=log_entry.get('component')
                )
            except Exception as e:
                # 如果写入失败，重新添加回缓冲区
                with self._lock:
                    self._buffer.append(log_entry)
                raise e

    def get_recent_logs(self, count: int = 100) -> List[Dict]:
        """
        获取最近的日志条目

        Args:
            count: 返回的日志数量

        Returns:
            最近的日志条目列表
        """
        with self._lock:
            logs = list(self._buffer)

        # 按时间戳排序（最新的在前）
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        return logs[:count]

    def clear(self):
        """清空缓冲区"""
        with self._lock:
            self._buffer.clear()

    def get_statistics(self) -> Dict:
        """获取缓冲区统计信息"""
        with self._lock:
            return {
                'current_size': len(self._buffer),
                'max_size': self._buffer.maxlen,
                'total_added': self._stats['total_added'],
                'total_flushed': self._stats['total_flushed'],
                'overwritten': self._stats['overwritten'],
                'utilization': len(self._buffer) / self._buffer.maxlen if self._buffer.maxlen > 0 else 0,
                'last_flush_time': self._stats['last_flush_time']
            }

    def _start_auto_flush(self):
        """启动自动刷新定时器"""
        def auto_flush():
            while True:
                time.sleep(self.flush_interval)
                try:
                    # 这里需要外部调用flush_to_sqlite，因为无法在这里访问sqlite_logger
                    pass
                except Exception as e:
                    # 记录错误但继续运行
                    pass

        # 注意：自动刷新需要外部管理，因为需要sqlite_logger引用
        # 这里只是预留接口

    def trigger_auto_flush(self, sqlite_logger):
        """触发自动刷新检查"""
        current_time = time.time()
        if current_time - self._stats['last_flush_time'] >= self.flush_interval:
            if len(self._buffer) > 0:
                self.flush_to_sqlite(sqlite_logger)

    def search_logs(self, search_text: str, limit: int = 50) -> List[Dict]:
        """
        在缓冲区中搜索日志

        Args:
            search_text: 搜索文本
            limit: 返回结果数量限制

        Returns:
            匹配的日志条目列表
        """
        filters = {
            'search_text': search_text,
            'limit': limit
        }
        return self.query_logs(filters)

    def get_logs_by_level(self, level: str, limit: int = 50) -> List[Dict]:
        """
        获取指定级别的日志

        Args:
            level: 日志级别
            limit: 返回结果数量限制

        Returns:
            匹配的日志条目列表
        """
        filters = {
            'level': level,
            'limit': limit
        }
        return self.query_logs(filters)

    def get_logs_by_component(self, component: str, limit: int = 50) -> List[Dict]:
        """
        获取指定组件的日志

        Args:
            component: 组件名称
            limit: 返回结果数量限制

        Returns:
            匹配的日志条目列表
        """
        filters = {
            'component': component,
            'limit': limit
        }
        return self.query_logs(filters)