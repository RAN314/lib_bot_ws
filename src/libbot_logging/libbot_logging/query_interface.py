#!/usr/bin/env python3
"""
日志查询接口

提供统一的日志查询接口，支持复杂的搜索和过滤功能。
"""

import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class QueryInterface:
    """日志查询接口"""

    def __init__(self, hybrid_logger):
        """
        初始化查询接口

        Args:
            hybrid_logger: HybridLogger实例
        """
        self.logger = hybrid_logger

    def search(self, query: str, log_type: str = None, level: str = None,
               component: str = None, hours: int = 24) -> List[Dict]:
        """
        综合搜索日志

        Args:
            query: 搜索关键词
            log_type: 日志类型过滤
            level: 日志级别过滤
            component: 组件过滤
            hours: 搜索时间范围（小时）

        Returns:
            匹配的日志条目列表
        """
        end_time = time.time()
        start_time = end_time - (hours * 3600)

        filters = {
            'search_text': query,
            'log_type': log_type,
            'level': level,
            'component': component,
            'start_time': start_time,
            'end_time': end_time,
            'limit': 100
        }

        return self.logger.sqlite_logger.query_logs(filters)

    def get_recent_errors(self, hours: int = 1) -> List[Dict]:
        """
        获取最近的错误日志

        Args:
            hours: 时间范围（小时）

        Returns:
            错误日志列表
        """
        end_time = time.time()
        start_time = end_time - (hours * 3600)

        filters = {
            'level': 'ERROR',
            'start_time': start_time,
            'end_time': end_time,
            'limit': 50
        }

        return self.logger.sqlite_logger.query_logs(filters)

    def get_component_logs(self, component: str, hours: int = 24) -> List[Dict]:
        """
        获取指定组件的日志

        Args:
            component: 组件名称
            hours: 时间范围（小时）

        Returns:
            组件日志列表
        """
        end_time = time.time()
        start_time = end_time - (hours * 3600)

        filters = {
            'component': component,
            'start_time': start_time,
            'end_time': end_time,
            'limit': 100
        }

        return self.logger.sqlite_logger.query_logs(filters)

    def get_performance_logs(self, operation: str = None) -> List[Dict]:
        """
        获取性能相关的业务日志

        Args:
            operation: 操作类型过滤

        Returns:
            性能日志列表
        """
        end_time = time.time()
        start_time = end_time - (24 * 3600)  # 最近24小时

        filters = {
            'log_type': 'business',
            'start_time': start_time,
            'end_time': end_time,
            'limit': 100
        }

        logs = self.logger.query_logs(**filters)

        # 过滤性能相关的日志
        performance_logs = []
        for log in logs:
            details = log.get('details', '')
            if operation and operation in details:
                performance_logs.append(log)
            elif not operation and ('duration' in details or 'time' in details):
                performance_logs.append(log)

        return performance_logs

    def get_system_status_summary(self, hours: int = 1) -> Dict:
        """
        获取系统状态摘要

        Args:
            hours: 时间范围（小时）

        Returns:
            系统状态摘要
        """
        end_time = time.time()
        start_time = end_time - (hours * 3600)

        # 获取各类日志统计
        system_logs = self.logger.query_logs(
            log_type='system',
            start_time=start_time,
            end_time=end_time,
            limit=1000
        )

        business_logs = self.logger.query_logs(
            log_type='business',
            start_time=start_time,
            end_time=end_time,
            limit=1000
        )

        # 统计信息
        summary = {
            'time_range': {
                'start': datetime.fromtimestamp(start_time).isoformat(),
                'end': datetime.fromtimestamp(end_time).isoformat(),
                'hours': hours
            },
            'system_logs': {
                'total': len(system_logs),
                'by_level': {},
                'by_component': {}
            },
            'business_logs': {
                'total': len(business_logs),
                'success_rate': 0,
                'by_operation': {}
            }
        }

        # 系统日志统计
        for log in system_logs:
            level = log.get('level', 'UNKNOWN')
            component = log.get('component', 'unknown')

            summary['system_logs']['by_level'][level] = summary['system_logs']['by_level'].get(level, 0) + 1
            summary['system_logs']['by_component'][component] = summary['system_logs']['by_component'].get(component, 0) + 1

        # 业务日志统计
        success_count = 0
        for log in business_logs:
            details = log.get('details', '{}')
            try:
                details_dict = eval(details) if isinstance(details, str) else details
                operation = details_dict.get('operation', 'unknown')
                result = log.get('level', 'INFO')

                summary['business_logs']['by_operation'][operation] = summary['business_logs']['by_operation'].get(operation, 0) + 1

                if result == 'INFO':
                    success_count += 1
            except:
                pass

        if len(business_logs) > 0:
            summary['business_logs']['success_rate'] = success_count / len(business_logs) * 100

        return summary

    def export_logs(self, filters: Dict, format_type: str = 'json') -> str:
        """
        导出日志

        Args:
            filters: 导出过滤器
            format_type: 导出格式 (json/csv)

        Returns:
            格式化后的日志数据
        """
        logs = self.logger.query_logs(**filters)

        if format_type.lower() == 'json':
            import json
            return json.dumps(logs, indent=2, ensure_ascii=False)

        elif format_type.lower() == 'csv':
            if not logs:
                return ""

            # 获取所有可能的字段
            fields = set()
            for log in logs:
                fields.update(log.keys())
            fields = sorted(list(fields))

            # 生成CSV
            import csv
            import io

            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=fields)
            writer.writeheader()
            writer.writerows(logs)

            return output.getvalue()

        else:
            raise ValueError(f"不支持的导出格式: {format_type}")

    def get_error_trends(self, days: int = 7) -> Dict:
        """
        获取错误趋势分析

        Args:
            days: 分析天数

        Returns:
            错误趋势数据
        """
        end_time = time.time()
        start_time = end_time - (days * 24 * 3600)

        # 获取错误日志
        error_logs = self.logger.query_logs(
            level='ERROR',
            start_time=start_time,
            end_time=end_time,
            limit=10000
        )

        # 按天统计
        daily_errors = {}
        component_errors = {}

        for log in error_logs:
            timestamp = log.get('timestamp', 0)
            date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
            component = log.get('component', 'unknown')

            daily_errors[date] = daily_errors.get(date, 0) + 1
            component_errors[component] = component_errors.get(component, 0) + 1

        return {
            'period': {
                'start': datetime.fromtimestamp(start_time).isoformat(),
                'end': datetime.fromtimestamp(end_time).isoformat(),
                'days': days
            },
            'total_errors': len(error_logs),
            'daily_trend': daily_errors,
            'component_breakdown': component_errors,
            'average_daily': len(error_logs) / days if days > 0 else 0
        }

    def find_anomalies(self, hours: int = 24) -> List[Dict]:
        """
        查找异常日志模式

        Args:
            hours: 分析时间范围

        Returns:
            异常日志列表
        """
        end_time = time.time()
        start_time = end_time - (hours * 3600)

        # 获取所有日志
        all_logs = self.logger.query_logs(
            start_time=start_time,
            end_time=end_time,
            limit=5000
        )

        anomalies = []

        # 检测高频错误
        error_count = {}
        for log in all_logs:
            if log.get('level') == 'ERROR':
                component = log.get('component', 'unknown')
                error_count[component] = error_count.get(component, 0) + 1

        # 标记高频错误组件
        for log in all_logs:
            if log.get('level') == 'ERROR':
                component = log.get('component', 'unknown')
                if error_count.get(component, 0) > 5:  # 超过5次错误视为异常
                    log['anomaly_type'] = 'high_frequency_error'
                    log['error_count'] = error_count[component]
                    anomalies.append(log)

        return anomalies