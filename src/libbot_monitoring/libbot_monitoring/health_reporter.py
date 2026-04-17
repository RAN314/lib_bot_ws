# health_reporter.py

import time
import statistics
from typing import Dict, List
from datetime import datetime, timedelta


class HealthReporter:
    """健康报告生成器"""

    def __init__(self, health_history: List[Dict]):
        self.health_history = health_history

    def generate_report(self, duration_seconds: int = 0) -> Dict:
        """生成健康报告

        Args:
            duration_seconds: 报告覆盖的时间范围(秒)，0表示所有历史数据

        Returns:
            健康报告字典
        """
        current_time = time.time()

        # 过滤时间范围
        if duration_seconds > 0:
            cutoff_time = current_time - duration_seconds
            filtered_history = [
                record for record in self.health_history
                if record['timestamp'] >= cutoff_time
            ]
        else:
            filtered_history = self.health_history

        if not filtered_history:
            return self._generate_empty_report()

        # 生成报告
        report = {
            'report_metadata': self._generate_metadata(filtered_history, duration_seconds),
            'overall_health': self._analyze_overall_health(filtered_history),
            'component_analysis': self._analyze_components(filtered_history),
            'trends': self._analyze_trends(filtered_history),
            'alerts': self._analyze_alerts(filtered_history),
            'recommendations': self._generate_recommendations(filtered_history)
        }

        return report

    def _generate_metadata(self, history: List[Dict], duration_seconds: int) -> Dict:
        """生成报告元数据"""
        if not history:
            return {}

        start_time = datetime.fromtimestamp(history[0]['timestamp'])
        end_time = datetime.fromtimestamp(history[-1]['timestamp'])

        return {
            'generated_at': datetime.now().isoformat(),
            'report_duration_seconds': duration_seconds,
            'data_start_time': start_time.isoformat(),
            'data_end_time': end_time.isoformat(),
            'total_records': len(history),
            'monitoring_period_hours': (history[-1]['timestamp'] - history[0]['timestamp']) / 3600
        }

    def _analyze_overall_health(self, history: List[Dict]) -> Dict:
        """分析整体健康状态"""
        if not history:
            return {}

        health_states = [record['overall_health'] for record in history]
        state_counts = {}

        for state in ['HEALTHY', 'WARNING', 'ERROR', 'CRITICAL', 'UNKNOWN']:
            count = health_states.count(state)
            state_counts[state] = {
                'count': count,
                'percentage': (count / len(health_states)) * 100 if health_states else 0
            }

        # 当前状态
        current_state = history[-1]['overall_health'] if history else 'UNKNOWN'

        # 状态持续时间
        state_durations = self._calculate_state_durations(history)

        return {
            'current_state': current_state,
            'state_distribution': state_counts,
            'state_durations': state_durations,
            'total_measurements': len(history)
        }

    def _analyze_components(self, history: List[Dict]) -> Dict:
        """分析各个组件的健康状态"""
        if not history:
            return {}

        components = ['navigation', 'perception', 'system', 'resource']
        component_analysis = {}

        for component in components:
            component_data = []

            for record in history:
                details = record.get('details', {})
                if component in details:
                    component_data.append(details[component])

            if component_data:
                component_analysis[component] = self._analyze_component_data(component, component_data)

        return component_analysis

    def _analyze_component_data(self, component: str, data: List[Dict]) -> Dict:
        """分析单个组件的数据"""
        if not data:
            return {}

        # 收集所有指标
        all_metrics = set()
        for record in data:
            all_metrics.update(record.keys())

        metrics_analysis = {}

        for metric in all_metrics:
            if metric in ['current_time', 'timestamp']:
                continue

            values = [record.get(metric, 0) for record in data if metric in record]

            if values:
                metrics_analysis[metric] = {
                    'current_value': values[-1],
                    'average': statistics.mean(values),
                    'minimum': min(values),
                    'maximum': max(values),
                    'std_deviation': statistics.stdev(values) if len(values) > 1 else 0,
                    'trend': self._calculate_trend(values)
                }

        return {
            'metrics': metrics_analysis,
            'sample_count': len(data),
            'latest_data': data[-1] if data else {}
        }

    def _analyze_trends(self, history: List[Dict]) -> Dict:
        """分析健康趋势"""
        if len(history) < 2:
            return {}

        # 将历史数据分成几个时间段分析趋势
        segment_size = max(1, len(history) // 4)  # 分成4个时间段
        segments = []

        for i in range(0, len(history), segment_size):
            segment = history[i:i + segment_size]
            if segment:
                segments.append(segment)

        trends = {
            'overall_trend': self._calculate_overall_trend(history),
            'segment_analysis': []
        }

        for i, segment in enumerate(segments):
            if segment:
                segment_analysis = {
                    'segment': i + 1,
                    'start_time': datetime.fromtimestamp(segment[0]['timestamp']).isoformat(),
                    'end_time': datetime.fromtimestamp(segment[-1]['timestamp']).isoformat(),
                    'avg_health_state': self._calculate_average_health_state(segment),
                    'record_count': len(segment)
                }
                trends['segment_analysis'].append(segment_analysis)

        return trends

    def _analyze_alerts(self, history: List[Dict]) -> Dict:
        """分析告警情况"""
        # 这里可以基于历史数据中的异常值来识别潜在的告警
        # 目前返回基本结构
        return {
            'alert_summary': {
                'total_alerts': 0,  # 需要从日志或其他来源获取
                'critical_alerts': 0,
                'error_alerts': 0,
                'warning_alerts': 0
            },
            'recent_alerts': []  # 需要从日志系统获取
        }

    def _generate_recommendations(self, history: List[Dict]) -> List[str]:
        """生成健康建议"""
        recommendations = []

        if not history:
            return ["暂无足够数据生成建议"]

        # 基于整体健康状态生成建议
        current_state = history[-1]['overall_health']

        if current_state == 'CRITICAL':
            recommendations.append("系统处于严重状态，建议立即检查并修复问题")
        elif current_state == 'ERROR':
            recommendations.append("系统存在错误，建议尽快排查并解决")
        elif current_state == 'WARNING':
            recommendations.append("系统存在警告，建议关注并预防潜在问题")

        # 基于趋势分析生成建议
        overall_trend = self._calculate_overall_trend(history)
        if overall_trend == 'degrading':
            recommendations.append("系统健康状态呈下降趋势，建议进行预防性维护")
        elif overall_trend == 'improving':
            recommendations.append("系统健康状态正在改善，继续保持当前维护策略")

        if not recommendations:
            recommendations.append("系统运行状态良好，建议继续监控")

        return recommendations

    def _calculate_state_durations(self, history: List[Dict]) -> Dict:
        """计算各状态的持续时间"""
        if len(history) < 2:
            return {}

        state_durations = {}
        current_state = history[0]['overall_health']
        current_start = history[0]['timestamp']

        for i in range(1, len(history)):
            if history[i]['overall_health'] != current_state:
                duration = history[i]['timestamp'] - current_start
                if current_state not in state_durations:
                    state_durations[current_state] = 0
                state_durations[current_state] += duration

                current_state = history[i]['overall_health']
                current_start = history[i]['timestamp']

        # 计算最后一个状态的持续时间
        if history:
            duration = history[-1]['timestamp'] - current_start
            if current_state not in state_durations:
                state_durations[current_state] = 0
            state_durations[current_state] += duration

        return state_durations

    def _calculate_trend(self, values: List[float]) -> str:
        """计算趋势"""
        if len(values) < 2:
            return 'stable'

        # 简单线性趋势分析
        first_half_avg = statistics.mean(values[:len(values)//2])
        second_half_avg = statistics.mean(values[len(values)//2:])

        change_percent = ((second_half_avg - first_half_avg) / first_half_avg) * 100 if first_half_avg != 0 else 0

        if change_percent > 10:
            return 'improving'
        elif change_percent < -10:
            return 'degrading'
        else:
            return 'stable'

    def _calculate_overall_trend(self, history: List[Dict]) -> str:
        """计算整体趋势"""
        if len(history) < 2:
            return 'unknown'

        # 基于健康状态评分计算趋势
        state_scores = {'HEALTHY': 4, 'WARNING': 3, 'ERROR': 2, 'CRITICAL': 1, 'UNKNOWN': 0}
        scores = [state_scores.get(record['overall_health'], 0) for record in history]

        return self._calculate_trend(scores)

    def _calculate_average_health_state(self, segment: List[Dict]) -> str:
        """计算平均健康状态"""
        if not segment:
            return 'UNKNOWN'

        state_scores = {'HEALTHY': 4, 'WARNING': 3, 'ERROR': 2, 'CRITICAL': 1, 'UNKNOWN': 0}
        scores = [state_scores.get(record['overall_health'], 0) for record in segment]
        avg_score = statistics.mean(scores)

        for state, score in state_scores.items():
            if avg_score >= score - 0.5:
                return state

        return 'UNKNOWN'

    def _generate_empty_report(self) -> Dict:
        """生成空报告"""
        return {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'message': 'No health data available for the specified time range'
            },
            'overall_health': {},
            'component_analysis': {},
            'trends': {},
            'alerts': {},
            'recommendations': ['No data available for analysis']
        }
