#!/usr/bin/env python3
"""
日志轮转管理器
实现ROS2日志和SQLite业务日志的自动轮转、压缩和清理
"""

import os
import time
import gzip
import shutil
import threading
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio
from concurrent.futures import ThreadPoolExecutor


@dataclass
class RotationPolicy:
    """轮转策略配置"""
    retention_days: int
    max_file_size: int  # 字节
    compress_after_days: int
    backup_count: int


class LogRotator:
    """日志轮转管理器"""

    def __init__(self, config: Dict[str, Any]):
        """初始化日志轮转管理器

        Args:
            config: 轮转配置
        """
        self.config = config
        self.is_running = False
        self.rotation_thread = None
        self.cleanup_lock = threading.RLock()
        self.executor = ThreadPoolExecutor(max_workers=2)

        # 设置日志
        self.logger = logging.getLogger(__name__)

        # 轮转策略配置
        self.rotation_policies = {
            'ros2_logs': RotationPolicy(
                retention_days=config.get('ros2_logs', {}).get('retention_days', 7),
                max_file_size=config.get('ros2_logs', {}).get('max_file_size', 100 * 1024 * 1024),  # 100MB
                compress_after_days=config.get('ros2_logs', {}).get('compress_after_days', 3),
                backup_count=config.get('ros2_logs', {}).get('backup_count', 5)
            ),
            'sqlite_logs': RotationPolicy(
                retention_days=config.get('sqlite_logs', {}).get('retention_days', 30),
                max_file_size=config.get('sqlite_logs', {}).get('max_db_size', 500 * 1024 * 1024),  # 500MB
                compress_after_days=config.get('sqlite_logs', {}).get('compress_after_days', 7),
                backup_count=config.get('sqlite_logs', {}).get('backup_count', 10)
            )
        }

        # 存储监控
        self.storage_monitor = StorageMonitor(config.get('storage_monitoring', {}))

        # ROS2日志目录
        self.ros2_log_dir = Path(config.get('ros2_log_dir', '/var/log/ros'))

        # SQLite数据库路径
        self.db_path = Path(config.get('database_path', 'library.db'))

    def start_rotation(self):
        """启动自动轮转"""
        if self.is_running:
            return

        self.is_running = True

        # 启动轮转线程
        self.rotation_thread = threading.Thread(
            target=self._rotation_loop,
            daemon=True,
            name="LogRotatorThread"
        )
        self.rotation_thread.start()

        # 启动存储监控
        self.storage_monitor.start_monitoring()

        # 连接存储监控信号
        self.storage_monitor.cleanup_needed.connect(self._on_storage_cleanup_needed)

        self.logger.info("日志轮转管理器启动")

    def stop_rotation(self):
        """停止自动轮转"""
        self.is_running = False

        if self.rotation_thread:
            self.rotation_thread.join(timeout=5.0)

        self.storage_monitor.stop_monitoring()
        self.executor.shutdown(wait=True)

        self.logger.info("日志轮转管理器停止")

    def manual_rotate(self, log_type: str = 'all'):
        """手动触发轮转

        Args:
            log_type: 日志类型 (ros2_logs/sqlite_logs/all)
        """
        try:
            with self.cleanup_lock:
                if log_type in ['ros2_logs', 'all']:
                    self._rotate_ros2_logs()

                if log_type in ['sqlite_logs', 'all']:
                    self._rotate_sqlite_logs()

                self.logger.info(f"手动轮转完成: {log_type}")

        except Exception as e:
            self.logger.error(f"手动轮转失败: {str(e)}")
            raise

    def manual_cleanup(self, log_type: str = 'all'):
        """手动触发清理

        Args:
            log_type: 日志类型
        """
        try:
            with self.cleanup_lock:
                if log_type in ['ros2_logs', 'all']:
                    self._cleanup_ros2_logs()

                if log_type in ['sqlite_logs', 'all']:
                    self._cleanup_sqlite_logs()

                self.logger.info(f"手动清理完成: {log_type}")

        except Exception as e:
            self.logger.error(f"手动清理失败: {str(e)}")
            raise

    def _rotation_loop(self):
        """轮转主循环"""
        check_interval = self.config.get('check_interval', 3600)  # 默认1小时检查一次

        while self.is_running:
            try:
                # 检查是否需要轮转
                self._check_rotation_needed()

                # 检查存储空间
                self._check_storage_space()

                # 等待下一个检查周期
                for _ in range(min(check_interval, 60)):  # 最多等待60秒检查一次运行状态
                    if not self.is_running:
                        break
                    time.sleep(1)

            except Exception as e:
                self.logger.error(f"轮转循环错误: {str(e)}")
                time.sleep(60)  # 错误后等待1分钟

    def _check_rotation_needed(self):
        """检查是否需要轮转"""
        try:
            # ROS2日志轮转检查
            self._check_ros2_rotation()

            # SQLite日志轮转检查
            self._check_sqlite_rotation()

        except Exception as e:
            self.logger.error(f"轮转检查错误: {str(e)}")

    def _check_ros2_rotation(self):
        """检查ROS2日志轮转"""
        try:
            if not self.ros2_log_dir.exists():
                return

            # 查找ROS2日志文件
            for log_file in self.ros2_log_dir.glob('*.log*'):
                if self._should_rotate_file(log_file, 'ros2_logs'):
                    # 异步执行轮转避免阻塞
                    self.executor.submit(self._rotate_single_ros2_file, log_file)
                    break

        except Exception as e:
            self.logger.error(f"ROS2日志轮转检查错误: {str(e)}")

    def _check_sqlite_rotation(self):
        """检查SQLite日志轮转"""
        try:
            if not self.db_path.exists():
                return

            # 检查数据库大小
            db_size = self.db_path.stat().st_size
            policy = self.rotation_policies['sqlite_logs']

            if db_size > policy.max_file_size:
                self.executor.submit(self._rotate_sqlite_logs)

        except Exception as e:
            self.logger.error(f"SQLite日志轮转检查错误: {str(e)}")

    def _should_rotate_file(self, file_path: Path, log_type: str) -> bool:
        """检查文件是否需要轮转

        Args:
            file_path: 文件路径
            log_type: 日志类型

        Returns:
            是否需要轮转
        """
        try:
            policy = self.rotation_policies[log_type]

            # 检查文件大小
            file_size = file_path.stat().st_size
            if file_size > policy.max_file_size:
                return True

            # 检查文件时间（超过1天）
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            cutoff_time = datetime.now() - timedelta(days=1)

            if file_mtime < cutoff_time:
                return True

            return False

        except Exception as e:
            self.logger.error(f"检查文件轮转错误: {str(e)}")
            return False

    def _rotate_single_ros2_file(self, log_file: Path):
        """轮转单个ROS2日志文件"""
        try:
            # 创建备份文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{log_file.stem}_{timestamp}{log_file.suffix}"
            backup_path = log_file.parent / backup_name

            # 重命名文件
            log_file.rename(backup_path)

            # 压缩旧文件
            if self.config.get('enable_compression', True):
                compressed_path = self._compress_file_async(backup_path)
                if compressed_path:
                    backup_path.unlink()  # 删除未压缩文件

            self.logger.info(f"ROS2日志轮转: {log_file} -> {backup_name}")

        except Exception as e:
            self.logger.error(f"ROS2文件轮转错误 {log_file}: {str(e)}")

    def _rotate_ros2_logs(self):
        """轮转ROS2日志"""
        try:
            if not self.ros2_log_dir.exists():
                return

            # 查找需要轮转的日志文件
            for log_file in self.ros2_log_dir.glob('*.log*'):
                if self._should_rotate_file(log_file, 'ros2_logs'):
                    self._rotate_single_ros2_file(log_file)

            # 清理过期文件
            self._cleanup_ros2_logs()

        except Exception as e:
            self.logger.error(f"ROS2日志轮转错误: {str(e)}")

    def _rotate_sqlite_logs(self):
        """轮转SQLite日志"""
        try:
            if not self.db_path.exists():
                return

            # 创建数据库备份
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = self.db_path.parent / f"{self.db_path.stem}_backup_{timestamp}{self.db_path.suffix}"

            # 备份数据库
            shutil.copy2(self.db_path, backup_path)

            # 清理旧数据
            self._cleanup_old_sqlite_data()

            # 压缩数据库
            self._vacuum_database()

            # 压缩备份文件
            if self.config.get('enable_compression', True):
                compressed_path = self._compress_file_async(backup_path)
                if compressed_path:
                    backup_path.unlink()

            self.logger.info(f"SQLite日志轮转完成: {backup_path}")

        except Exception as e:
            self.logger.error(f"SQLite日志轮转错误: {str(e)}")

    def _cleanup_ros2_logs(self):
        """清理ROS2过期日志"""
        try:
            if not self.ros2_log_dir.exists():
                return

            policy = self.rotation_policies['ros2_logs']
            cutoff_time = datetime.now() - timedelta(days=policy.retention_days)

            # 清理过期文件
            for log_file in self.ros2_log_dir.glob('*.log*'):
                try:
                    file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)

                    if file_mtime < cutoff_time:
                        log_file.unlink()
                        self.logger.info(f"清理过期ROS2日志: {log_file}")
                except Exception as e:
                    self.logger.warning(f"清理ROS2日志失败 {log_file}: {str(e)}")

        except Exception as e:
            self.logger.error(f"清理ROS2日志错误: {str(e)}")

    def _cleanup_sqlite_logs(self):
        """清理SQLite过期日志"""
        try:
            if not self.db_path.exists():
                return

            policy = self.rotation_policies['sqlite_logs']

            # 清理过期数据
            deleted_count = self._cleanup_old_sqlite_data()

            # 压缩数据库
            self._vacuum_database()

            self.logger.info(f"SQLite日志清理完成，删除{deleted_count}条记录")

        except Exception as e:
            self.logger.error(f"清理SQLite日志错误: {str(e)}")

    def _cleanup_old_sqlite_data(self) -> int:
        """清理SQLite中的过期数据

        Returns:
            删除的记录数
        """
        try:
            policy = self.rotation_policies['sqlite_logs']
            cutoff_time = datetime.now() - timedelta(days=policy.retention_days)
            cutoff_timestamp = cutoff_time.timestamp()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 清理过期日志
            cursor.execute(
                "DELETE FROM logs WHERE timestamp < ?",
                (cutoff_timestamp,)
            )
            deleted_count = cursor.rowcount

            conn.commit()
            conn.close()

            return deleted_count

        except Exception as e:
            self.logger.error(f"清理SQLite数据错误: {str(e)}")
            return 0

    def _vacuum_database(self):
        """压缩SQLite数据库"""
        try:
            if not self.db_path.exists():
                return

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 执行VACUUM操作
            cursor.execute("VACUUM")

            conn.commit()
            conn.close()

            self.logger.info("SQLite数据库压缩完成")

        except Exception as e:
            self.logger.error(f"数据库压缩错误: {str(e)}")

    def _compress_file_async(self, file_path: Path) -> Optional[Path]:
        """异步压缩文件

        Args:
            file_path: 要压缩的文件

        Returns:
            压缩后的文件路径，失败返回None
        """
        try:
            compressed_path = file_path.with_suffix(file_path.suffix + '.gz')

            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            return compressed_path

        except Exception as e:
            self.logger.error(f"压缩文件错误 {file_path}: {str(e)}")
            return None

    def _check_storage_space(self):
        """检查存储空间"""
        try:
            # 获取存储使用情况
            usage = self.storage_monitor.get_storage_usage()

            # 检查是否需要告警
            warning_threshold = self.config.get('storage_monitoring', {}).get('warning_threshold', 80)
            if usage['usage_percent'] > warning_threshold:
                self.logger.warning(
                    f"存储空间告警: {usage['usage_percent']:.1f}% 已使用"
                )

            # 检查是否需要自动清理
            critical_threshold = self.config.get('storage_monitoring', {}).get('critical_threshold', 90)
            if usage['usage_percent'] > critical_threshold:
                self.logger.warning("存储空间严重不足，触发自动清理")
                self.manual_cleanup('all')

        except Exception as e:
            self.logger.error(f"存储空间检查错误: {str(e)}")

    def _on_storage_cleanup_needed(self, urgency: str):
        """存储空间清理信号处理器"""
        try:
            self.logger.info(f"收到存储空间清理请求，紧急程度: {urgency}")

            if urgency == 'critical':
                # 紧急清理所有日志
                self.manual_cleanup('all')
            elif urgency == 'warning':
                # 只清理过期的ROS2日志
                self._cleanup_ros2_logs()

        except Exception as e:
            self.logger.error(f"存储空间清理错误: {str(e)}")


class StorageMonitor:
    """存储空间监控"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_running = False
        self.monitor_thread = None
        self.check_interval = config.get('check_interval', 300)  # 5分钟

        # 信号定义（简化实现）
        self.cleanup_needed = type('Signal', (), {'connect': lambda self, callback: None})()

    def start_monitoring(self):
        """启动存储监控"""
        if self.is_running:
            return

        self.is_running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="StorageMonitorThread"
        )
        self.monitor_thread.start()

    def stop_monitoring(self):
        """停止存储监控"""
        self.is_running = False

        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)

    def get_storage_usage(self) -> Dict[str, Any]:
        """获取存储使用情况

        Returns:
            存储使用信息
        """
        try:
            import shutil

            # 获取磁盘使用情况
            disk_usage = shutil.disk_usage('/')

            total = disk_usage.total
            used = disk_usage.used
            free = disk_usage.free

            usage_percent = (used / total) * 100 if total > 0 else 0

            return {
                'total_bytes': total,
                'used_bytes': used,
                'free_bytes': free,
                'usage_percent': usage_percent,
                'total_gb': total / (1024**3),
                'used_gb': used / (1024**3),
                'free_gb': free / (1024**3)
            }

        except Exception as e:
            logging.getLogger(__name__).error(f"获取存储使用错误: {str(e)}")
            return {
                'total_bytes': 0,
                'used_bytes': 0,
                'free_bytes': 0,
                'usage_percent': 0,
                'total_gb': 0,
                'used_gb': 0,
                'free_gb': 0
            }

    def _monitor_loop(self):
        """监控循环"""
        while self.is_running:
            try:
                # 检查存储使用
                usage = self.get_storage_usage()

                # 检查阈值
                warning_threshold = self.config.get('warning_threshold', 80)
                critical_threshold = self.config.get('critical_threshold', 90)

                if usage['usage_percent'] > critical_threshold:
                    self._trigger_cleanup('critical')
                elif usage['usage_percent'] > warning_threshold:
                    self._trigger_cleanup('warning')

                # 等待下一个检查周期
                for _ in range(min(self.check_interval, 60)):
                    if not self.is_running:
                        break
                    time.sleep(1)

            except Exception as e:
                logging.getLogger(__name__).error(f"存储监控错误: {str(e)}")
                time.sleep(60)

    def _trigger_cleanup(self, urgency: str):
        """触发清理操作"""
        # 这里应该发出信号，简化实现直接记录日志
        logging.getLogger(__name__).warning(
            f"存储空间{urgency}告警，需要清理操作"
        )