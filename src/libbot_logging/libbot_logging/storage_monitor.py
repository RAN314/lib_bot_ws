#!/usr/bin/env python3
"""
存储空间监控模块
提供详细的存储空间监控、分析和告警功能
"""

import os
import time
import threading
import logging
import shutil
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json


@dataclass
class StorageThreshold:
    """存储阈值配置"""
    warning_threshold: float = 80.0  # 80%
    critical_threshold: float = 90.0  # 90%
    emergency_threshold: float = 95.0  # 95%


@dataclass
class StorageAlert:
    """存储告警信息"""
    timestamp: datetime
    level: str  # warning/critical/emergency
    message: str
    usage_percent: float
    free_space_gb: float


@dataclass
class PartitionInfo:
    """分区信息"""
    device: str
    mountpoint: str
    fstype: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    usage_percent: float


class StorageMonitor:
    """
    存储空间监控器

    提供完整的存储空间监控功能：
    - 实时磁盘使用监控
    - 分区级别详细分析
    - 智能告警系统
    - 历史趋势分析
    - 自动清理建议
    """

    def __init__(self, config: Dict[str, Any]):
        """初始化存储监控器

        Args:
            config: 监控配置
        """
        self.config = config
        self.is_running = False
        self.monitor_thread = None
        self.monitor_lock = threading.RLock()

        # 日志设置
        self.logger = logging.getLogger(__name__)

        # 阈值配置
        threshold_config = config.get('thresholds', {})
        self.thresholds = StorageThreshold(
            warning_threshold=threshold_config.get('warning', 80.0),
            critical_threshold=threshold_config.get('critical', 90.0),
            emergency_threshold=threshold_config.get('emergency', 95.0)
        )

        # 监控配置
        self.check_interval = config.get('check_interval', 300)  # 5分钟
        self.monitor_partitions = config.get('monitor_partitions', ['/'])
        self.enable_history = config.get('enable_history', True)
        self.history_retention_days = config.get('history_retention_days', 30)

        # 历史数据存储
        self.usage_history: List[Dict[str, Any]] = []
        self.alert_history: List[StorageAlert] = []
        self.history_lock = threading.RLock()

        # 告警配置
        self.alert_cooldown = config.get('alert_cooldown', 3600)  # 1小时
        self.last_alert_time: Dict[str, datetime] = {}

        # 监控的分区信息
        self.partitions: List[PartitionInfo] = []
        self._discover_partitions()

    def start_monitoring(self):
        """启动存储监控"""
        with self.monitor_lock:
            if self.is_running:
                return

            self.is_running = True

            # 启动监控线程
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True,
                name="StorageMonitorThread"
            )
            self.monitor_thread.start()

            self.logger.info(
                f"存储监控启动，检查间隔: {self.check_interval}秒，"
                f"监控分区: {self.monitor_partitions}"
            )

    def stop_monitoring(self):
        """停止存储监控"""
        with self.monitor_lock:
            self.is_running = False

            if self.monitor_thread:
                self.monitor_thread.join(timeout=5.0)

            self.logger.info("存储监控停止")

    def get_storage_usage(self) -> Dict[str, Any]:
        """获取存储使用情况

        Returns:
            存储使用信息
        """
        try:
            usage_data = {
                'timestamp': datetime.now().isoformat(),
                'partitions': {},
                'overall': self._get_overall_usage(),
                'partitions_detail': []
            }

            # 获取每个分区的详细信息
            for partition in self.partitions:
                try:
                    usage = shutil.disk_usage(partition.mountpoint)
                    partition_usage = {
                        'mountpoint': partition.mountpoint,
                        'device': partition.device,
                        'fstype': partition.fstype,
                        'total_bytes': usage.total,
                        'used_bytes': usage.used,
                        'free_bytes': usage.free,
                        'usage_percent': (usage.used / usage.total) * 100 if usage.total > 0 else 0,
                        'total_gb': usage.total / (1024**3),
                        'used_gb': usage.used / (1024**3),
                        'free_gb': usage.free / (1024**3)
                    }

                    usage_data['partitions'][partition.mountpoint] = partition_usage
                    usage_data['partitions_detail'].append(partition_usage)

                except Exception as e:
                    self.logger.error(f"获取分区 {partition.mountpoint} 使用信息失败: {str(e)}")

            return usage_data

        except Exception as e:
            self.logger.error(f"获取存储使用信息失败: {str(e)}")
            return {
                'timestamp': datetime.now().isoformat(),
                'partitions': {},
                'overall': {},
                'partitions_detail': [],
                'error': str(e)
            }

    def get_detailed_analysis(self) -> Dict[str, Any]:
        """获取详细存储分析

        Returns:
            详细分析报告
        """
        try:
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'storage_usage': self.get_storage_usage(),
                'trends': self._analyze_trends(),
                'alerts': self._get_recent_alerts(),
                'recommendations': self._generate_recommendations(),
                'partition_health': self._analyze_partition_health()
            }

            return analysis

        except Exception as e:
            self.logger.error(f"生成详细分析失败: {str(e)}")
            return {'error': str(e)}

    def _monitor_loop(self):
        """监控主循环"""
        while self.is_running:
            try:
                # 检查存储使用
                usage_data = self.get_storage_usage()

                # 记录历史数据
                if self.enable_history:
                    self._record_history(usage_data)

                # 检查告警条件
                self._check_alerts(usage_data)

                # 清理过期历史数据
                self._cleanup_old_history()

                # 等待下一个检查周期
                for _ in range(min(self.check_interval, 60)):
                    if not self.is_running:
                        break
                    time.sleep(1)

            except Exception as e:
                self.logger.error(f"存储监控循环错误: {str(e)}")
                time.sleep(60)

    def _discover_partitions(self):
        """发现监控分区"""
        try:
            # 获取所有挂载点
            partitions = psutil.disk_partitions(all=False)

            for partition in partitions:
                # 只监控指定的分区
                if partition.mountpoint in self.monitor_partitions:
                    try:
                        usage = shutil.disk_usage(partition.mountpoint)
                        partition_info = PartitionInfo(
                            device=partition.device,
                            mountpoint=partition.mountpoint,
                            fstype=partition.fstype,
                            total_bytes=usage.total,
                            used_bytes=usage.used,
                            free_bytes=usage.free,
                            usage_percent=(usage.used / usage.total) * 100 if usage.total > 0 else 0
                        )
                        self.partitions.append(partition_info)
                    except Exception as e:
                        self.logger.warning(f"无法获取分区 {partition.mountpoint} 信息: {str(e)}")

            self.logger.info(f"发现 {len(self.partitions)} 个监控分区")

        except Exception as e:
            self.logger.error(f"发现分区失败: {str(e)}")

    def _get_overall_usage(self) -> Dict[str, Any]:
        """获取整体存储使用情况"""
        try:
            total_bytes = sum(p.total_bytes for p in self.partitions)
            used_bytes = sum(p.used_bytes for p in self.partitions)
            free_bytes = sum(p.free_bytes for p in self.partitions)

            return {
                'total_bytes': total_bytes,
                'used_bytes': used_bytes,
                'free_bytes': free_bytes,
                'usage_percent': (used_bytes / total_bytes) * 100 if total_bytes > 0 else 0,
                'total_gb': total_bytes / (1024**3),
                'used_gb': used_bytes / (1024**3),
                'free_gb': free_bytes / (1024**3)
            }

        except Exception as e:
            self.logger.error(f"计算整体使用情况失败: {str(e)}")
            return {}

    def _check_alerts(self, usage_data: Dict[str, Any]):
        """检查告警条件"""
        try:
            current_time = datetime.now()

            for partition_data in usage_data.get('partitions_detail', []):
                mountpoint = partition_data['mountpoint']
                usage_percent = partition_data['usage_percent']

                # 检查是否需要告警
                alert_level = None
                if usage_percent >= self.thresholds.emergency_threshold:
                    alert_level = 'emergency'
                elif usage_percent >= self.thresholds.critical_threshold:
                    alert_level = 'critical'
                elif usage_percent >= self.thresholds.warning_threshold:
                    alert_level = 'warning'

                if alert_level:
                    # 检查告警冷却时间
                    last_alert = self.last_alert_time.get(mountpoint)
                    if not last_alert or (current_time - last_alert).total_seconds() >= self.alert_cooldown:
                        self._trigger_alert(
                            level=alert_level,
                            mountpoint=mountpoint,
                            usage_percent=usage_percent,
                            free_gb=partition_data['free_gb']
                        )
                        self.last_alert_time[mountpoint] = current_time

        except Exception as e:
            self.logger.error(f"检查告警条件失败: {str(e)}")

    def _trigger_alert(self, level: str, mountpoint: str, usage_percent: float, free_gb: float):
        """触发存储告警"""
        try:
            alert = StorageAlert(
                timestamp=datetime.now(),
                level=level,
                message=f"分区 {mountpoint} 存储使用率 {usage_percent:.1f}%，剩余空间 {free_gb:.2f}GB",
                usage_percent=usage_percent,
                free_space_gb=free_gb
            )

            # 添加到历史告警
            with self.history_lock:
                self.alert_history.append(alert)

            # 记录告警日志
            if level == 'emergency':
                self.logger.critical(alert.message)
            elif level == 'critical':
                self.logger.error(alert.message)
            else:
                self.logger.warning(alert.message)

        except Exception as e:
            self.logger.error(f"触发告警失败: {str(e)}")

    def _record_history(self, usage_data: Dict[str, Any]):
        """记录历史数据"""
        try:
            with self.history_lock:
                self.usage_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'data': usage_data
                })

        except Exception as e:
            self.logger.error(f"记录历史数据失败: {str(e)}")

    def _cleanup_old_history(self):
        """清理过期历史数据"""
        try:
            cutoff_time = datetime.now() - timedelta(days=self.history_retention_days)

            with self.history_lock:
                # 清理使用历史
                self.usage_history = [
                    record for record in self.usage_history
                    if datetime.fromisoformat(record['timestamp']) > cutoff_time
                ]

                # 清理告警历史
                self.alert_history = [
                    alert for alert in self.alert_history
                    if alert.timestamp > cutoff_time
                ]

        except Exception as e:
            self.logger.error(f"清理历史数据失败: {str(e)}")

    def _analyze_trends(self) -> Dict[str, Any]:
        """分析存储使用趋势"""
        try:
            with self.history_lock:
                if len(self.usage_history) < 2:
                    return {'status': 'insufficient_data'}

                # 计算最近24小时的使用趋势
                recent_data = [
                    record for record in self.usage_history
                    if datetime.fromisoformat(record['timestamp']) > datetime.now() - timedelta(hours=24)
                ]

                if len(recent_data) < 2:
                    return {'status': 'insufficient_recent_data'}

                # 分析趋势
                trends = {}
                for mountpoint in self.monitor_partitions:
                    if mountpoint in recent_data[0]['data']['partitions']:
                        usage_values = [
                            record['data']['partitions'][mountpoint]['usage_percent']
                            for record in recent_data
                            if mountpoint in record['data']['partitions']
                        ]

                        if len(usage_values) >= 2:
                            trend_direction = 'increasing' if usage_values[-1] > usage_values[0] else 'decreasing'
                            trend_rate = (usage_values[-1] - usage_values[0]) / len(usage_values)

                            trends[mountpoint] = {
                                'direction': trend_direction,
                                'rate_per_check': trend_rate,
                                'current_usage': usage_values[-1],
                                'projected_24h': usage_values[-1] + (trend_rate * 24)
                            }

                return trends

        except Exception as e:
            self.logger.error(f"分析趋势失败: {str(e)}")
            return {'error': str(e)}

    def _get_recent_alerts(self) -> List[Dict[str, Any]]:
        """获取最近告警"""
        try:
            with self.history_lock:
                recent_alerts = [
                    alert for alert in self.alert_history
                    if alert.timestamp > datetime.now() - timedelta(hours=24)
                ]

                return [
                    {
                        'timestamp': alert.timestamp.isoformat(),
                        'level': alert.level,
                        'message': alert.message,
                        'usage_percent': alert.usage_percent,
                        'free_space_gb': alert.free_space_gb
                    }
                    for alert in recent_alerts[-10:]  # 最近10条
                ]

        except Exception as e:
            self.logger.error(f"获取最近告警失败: {str(e)}")
            return []

    def _generate_recommendations(self) -> List[str]:
        """生成存储建议"""
        try:
            recommendations = []
            usage_data = self.get_storage_usage()

            for partition_data in usage_data.get('partitions_detail', []):
                usage_percent = partition_data['usage_percent']
                mountpoint = partition_data['mountpoint']

                if usage_percent >= self.thresholds.emergency_threshold:
                    recommendations.append(
                        f"紧急: {mountpoint} 存储使用率超过{usage_percent:.1f}%，建议立即清理或扩容"
                    )
                elif usage_percent >= self.thresholds.critical_threshold:
                    recommendations.append(
                        f"警告: {mountpoint} 存储使用率{usage_percent:.1f}%，建议启动自动清理"
                    )
                elif usage_percent >= self.thresholds.warning_threshold:
                    recommendations.append(
                        f"注意: {mountpoint} 存储使用率{usage_percent:.1f}%，建议监控趋势"
                    )

            # 检查趋势
            trends = self._analyze_trends()
            for mountpoint, trend in trends.items():
                if isinstance(trend, dict) and trend.get('direction') == 'increasing':
                    projected = trend.get('projected_24h', 0)
                    if projected > self.thresholds.warning_threshold:
                        recommendations.append(
                            f"预测: {mountpoint} 24小时后可能达到{projected:.1f}%使用率"
                        )

            return recommendations

        except Exception as e:
            self.logger.error(f"生成建议失败: {str(e)}")
            return []

    def _analyze_partition_health(self) -> Dict[str, str]:
        """分析分区健康状态"""
        try:
            health_status = {}
            usage_data = self.get_storage_usage()

            for partition_data in usage_data.get('partitions_detail', []):
                mountpoint = partition_data['mountpoint']
                usage_percent = partition_data['usage_percent']

                if usage_percent >= self.thresholds.emergency_threshold:
                    health_status[mountpoint] = 'CRITICAL'
                elif usage_percent >= self.thresholds.critical_threshold:
                    health_status[mountpoint] = 'WARNING'
                elif usage_percent >= self.thresholds.warning_threshold:
                    health_status[mountpoint] = 'CAUTION'
                else:
                    health_status[mountpoint] = 'HEALTHY'

            return health_status

        except Exception as e:
            self.logger.error(f"分析分区健康状态失败: {str(e)}")
            return {}

    def export_report(self, file_path: str) -> bool:
        """导出存储报告

        Args:
            file_path: 导出文件路径

        Returns:
            是否成功
        """
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'monitor_config': self.config,
                'current_usage': self.get_storage_usage(),
                'detailed_analysis': self.get_detailed_analysis(),
                'recent_alerts': self._get_recent_alerts(),
                'recommendations': self._generate_recommendations()
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            self.logger.info(f"存储报告已导出到: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"导出存储报告失败: {str(e)}")
            return False