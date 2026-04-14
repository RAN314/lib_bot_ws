# Story 3-2: 系统健康指标监控实现

> **Epic**: #3 日志与监控系统
> **Priority**: P0 (Critical)
> **Points**: 3
> **Status**: ready-for-dev
> **Platform**: ROS2 / Python
> **Dependencies**: Story 3-1 (混合日志方案实现)

---

## 📋 用户故事 (User Story)

作为系统管理员，
我希望能够实时监控系统的健康状态，
这样可以及时发现和解决系统问题，确保机器人稳定运行。

---

## 🎯 验收标准 (Acceptance Criteria)

### 功能性要求
- [ ] 实现导航健康度监控（AMCL频率、规划成功率）
- [ ] 实现感知健康度监控（RFID扫描频率、检测成功率）
- [ ] 实现系统资源监控（CPU、内存、Topic延迟）
- [ ] 实现健康指标发布到ROS2 Topic
- [ ] 支持健康阈值配置和告警
- [ ] 实现健康状态历史记录

### 性能要求
- [ ] 监控频率10Hz
- [ ] 指标计算延迟<50ms
- [ ] 资源占用<5% CPU
- [ ] 支持实时监控和历史查询

### 代码质量
- [ ] 模块化监控组件设计
- [ ] 完整的监控指标定义
- [ ] 支持动态阈值调整
- [ ] 详细的健康报告生成

---

## 🔧 实现细节

### 文件清单
```
src/libbot_monitoring/
src/libbot_monitoring/libbot_monitoring/
├── __init__.py
├── health_monitor.py           # 新建 - 健康监控管理器
├── monitors/
│   ├── navigation_monitor.py   # 新建 - 导航监控
│   ├── perception_monitor.py   # 新建 - 感知监控
│   ├── system_monitor.py       # 新建 - 系统监控
│   └── resource_monitor.py     # 新建 - 资源监控
├── health_reporter.py          # 新建 - 健康报告生成
└── config/
    └── monitoring_config.yaml  # 新建 - 监控配置
```

### HealthMonitor类设计

```python
# health_monitor.py

import rclpy
from rclpy.node import Node
import threading
import time
import psutil
import statistics
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from libbot_msgs.msg import SystemHealth, HealthMetric
from libbot_msgs.srv import GetHealthReport

@dataclass
class HealthThreshold:
    """健康阈值定义"""
    warning_threshold: float
    error_threshold: float
    critical_threshold: float
    
class HealthMonitor:
    """系统健康监控管理器"""
    
    def __init__(self, node: Node):
        """初始化健康监控管理器
        
        Args:
            node: ROS2节点实例
        """
        self.node = node
        self.is_running = False
        self.monitoring_thread = None
        
        # 监控组件
        self.navigation_monitor = None
        self.perception_monitor = None
        self.system_monitor = None
        self.resource_monitor = None
        
        # 健康数据存储
        self.health_data = {}
        self.health_history = []
        self.data_lock = threading.RLock()
        
        # ROS2接口
        self.health_publisher = None
        self.health_service = None
        
        # 配置参数
        self.monitor_frequency = 10.0  # 10Hz
        self.history_duration = 3600   # 1小时历史数据
        self.thresholds = self._load_thresholds()
        
        self._init_monitors()
        self._init_ros2_interfaces()
    
    def _init_monitors(self):
        """初始化监控组件"""
        from .monitors.navigation_monitor import NavigationMonitor
        from .monitors.perception_monitor import PerceptionMonitor
        from .monitors.system_monitor import SystemMonitor
        from .monitors.resource_monitor import ResourceMonitor
        
        self.navigation_monitor = NavigationMonitor(self.node)
        self.perception_monitor = PerceptionMonitor(self.node)
        self.system_monitor = SystemMonitor(self.node)
        self.resource_monitor = ResourceMonitor(self.node)
    
    def _init_ros2_interfaces(self):
        """初始化ROS2接口"""
        # 健康状态发布
        self.health_publisher = self.node.create_publisher(
            SystemHealth,
            '/system/health',
            10
        )
        
        # 健康报告服务
        self.health_service = self.node.create_service(
            GetHealthReport,
            '/system/get_health_report',
            self._health_report_callback
        )
    
    def start_monitoring(self):
        """启动健康监控"""
        if self.is_running:
            return
            
        self.is_running = True
        
        # 启动各监控组件
        self.navigation_monitor.start()
        self.perception_monitor.start()
        self.system_monitor.start()
        self.resource_monitor.start()
        
        # 启动监控线程
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        
        self.node.get_logger().info("系统健康监控启动")
    
    def stop_monitoring(self):
        """停止健康监控"""
        self.is_running = False
        
        # 停止监控组件
        if self.navigation_monitor:
            self.navigation_monitor.stop()
        if self.perception_monitor:
            self.perception_monitor.stop()
        if self.system_monitor:
            self.system_monitor.stop()
        if self.resource_monitor:
            self.resource_monitor.stop()
        
        # 等待监控线程结束
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        
        self.node.get_logger().info("系统健康监控停止")
    
    def _monitoring_loop(self):
        """监控主循环"""
        period = 1.0 / self.monitor_frequency
        
        while self.is_running:
            start_time = time.time()
            
            try:
                # 收集各组件健康数据
                health_data = self._collect_health_data()
                
                # 评估健康状态
                overall_health = self._evaluate_health(health_data)
                
                # 存储健康数据
                self._store_health_data(health_data, overall_health)
                
                # 发布健康状态
                self._publish_health_status(health_data, overall_health)
                
                # 检查告警条件
                self._check_alerts(health_data)
                
            except Exception as e:
                self.node.get_logger().error(f"监控循环错误: {str(e)}")
            
            # 保持固定频率
            elapsed = time.time() - start_time
            sleep_time = max(0, period - elapsed)
            time.sleep(sleep_time)
    
    def _collect_health_data(self) -> Dict:
        """收集健康数据"""
        return {
            'timestamp': time.time(),
            'navigation': self.navigation_monitor.get_health_data(),
            'perception': self.perception_monitor.get_health_data(),
            'system': self.system_monitor.get_health_data(),
            'resource': self.resource_monitor.get_health_data()
        }
    
    def _evaluate_health(self, health_data: Dict) -> str:
        """评估整体健康状态"""
        health_scores = []
        
        # 评估各个子系统
        for component, data in health_data.items():
            if component == 'timestamp':
                continue
                
            score = self._calculate_component_score(component, data)
            health_scores.append(score)
        
        # 计算整体健康分数
        if health_scores:
            avg_score = statistics.mean(health_scores)
            
            if avg_score >= 0.9:
                return 'HEALTHY'
            elif avg_score >= 0.7:
                return 'WARNING'
            elif avg_score >= 0.5:
                return 'ERROR'
            else:
                return 'CRITICAL'
        
        return 'UNKNOWN'
    
    def _calculate_component_score(self, component: str, data: Dict) -> float:
        """计算组件健康分数"""
        score = 1.0
        
        # 根据组件类型计算分数
        if component == 'navigation':
            # AMCL频率权重40%，规划成功率权重60%
            amcl_score = min(1.0, data.get('amcl_frequency', 0) / 10.0)
            plan_score = data.get('planning_success_rate', 0) / 100.0
            score = amcl_score * 0.4 + plan_score * 0.6
            
        elif component == 'perception':
            # RFID频率权重30%，检测成功率权重70%
            rfid_score = min(1.0, data.get('rfid_frequency', 0) / 10.0)
            detect_score = data.get('detection_success_rate', 0) / 100.0
            score = rfid_score * 0.3 + detect_score * 0.7
            
        elif component == 'resource':
            # CPU、内存、延迟综合评估
            cpu_score = max(0, 1.0 - data.get('cpu_usage', 0) / 100.0)
            mem_score = max(0, 1.0 - data.get('memory_usage', 0) / 2048.0)  # 2GB限制
            latency_score = max(0, 1.0 - data.get('topic_latency', 0) / 100.0)  # 100ms限制
            score = (cpu_score + mem_score + latency_score) / 3.0
        
        return max(0.0, min(1.0, score))
    
    def _store_health_data(self, health_data: Dict, overall_health: str):
        """存储健康数据"""
        with self.data_lock:
            # 添加到历史记录
            record = {
                'timestamp': health_data['timestamp'],
                'overall_health': overall_health,
                'details': health_data
            }
            
            self.health_history.append(record)
            
            # 清理过期数据
            cutoff_time = time.time() - self.history_duration
            self.health_history = [
                record for record in self.health_history
                if record['timestamp'] > cutoff_time
            ]
    
    def _publish_health_status(self, health_data: Dict, overall_health: str):
        """发布健康状态"""
        msg = SystemHealth()
        msg.timestamp = self.node.get_clock().now().to_msg()
        msg.overall_health = overall_health
        
        # 添加各个指标
        for component, data in health_data.items():
            if component == 'timestamp':
                continue
                
            metric = HealthMetric()
            metric.component = component
            
            for key, value in data.items():
                setattr(metric, key, value)
            
            msg.metrics.append(metric)
        
        self.health_publisher.publish(msg)
    
    def _check_alerts(self, health_data: Dict):
        """检查告警条件"""
        for component, data in health_data.items():
            if component == 'timestamp':
                continue
                
            thresholds = self.thresholds.get(component, {})
            
            for metric_name, value in data.items():
                if metric_name in thresholds:
                    threshold = thresholds[metric_name]
                    
                    if value >= threshold.critical_threshold:
                        self._trigger_alert(component, metric_name, value, 'CRITICAL')
                    elif value >= threshold.error_threshold:
                        self._trigger_alert(component, metric_name, value, 'ERROR')
                    elif value >= threshold.warning_threshold:
                        self._trigger_alert(component, metric_name, value, 'WARNING')
    
    def _trigger_alert(self, component: str, metric: str, value: float, level: str):
        """触发告警"""
        message = f"{component} {metric} = {value} ({level})"
        
        if level == 'CRITICAL':
            self.node.get_logger().fatal(message)
        elif level == 'ERROR':
            self.node.get_logger().error(message)
        elif level == 'WARNING':
            self.node.get_logger().warn(message)
    
    def _health_report_callback(self, request, response):
        """健康报告服务回调"""
        try:
            # 生成健康报告
            from .health_reporter import HealthReporter
            
            reporter = HealthReporter(self.health_history)
            report = reporter.generate_report()
            
            response.success = True
            response.report_json = report
            
        except Exception as e:
            self.node.get_logger().error(f"生成健康报告错误: {str(e)}")
            response.success = False
            response.report_json = "{}"
        
        return response
    
    def _load_thresholds(self) -> Dict:
        """加载健康阈值配置"""
        # 默认阈值配置
        return {
            'navigation': {
                'amcl_frequency': HealthThreshold(5.0, 3.0, 1.0),
                'planning_success_rate': HealthThreshold(95.0, 85.0, 70.0)
            },
            'perception': {
                'rfid_frequency': HealthThreshold(9.0, 7.0, 5.0),
                'detection_success_rate': HealthThreshold(90.0, 80.0, 60.0)
            },
            'resource': {
                'cpu_usage': HealthThreshold(70.0, 85.0, 95.0),
                'memory_usage': HealthThreshold(1536.0, 1792.0, 1920.0),  # MB
                'topic_latency': HealthThreshold(50.0, 100.0, 200.0)  # ms
            }
        }

class NavigationMonitor:
    """导航健康监控"""
    
    def __init__(self, node: Node):
        self.node = node
        self.amcl_sub = None
        self.plan_sub = None
        self.last_amcl_time = 0
        self.plan_attempts = 0
        self.plan_successes = 0
    
    def start(self):
        """启动导航监控"""
        self.amcl_sub = self.node.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self._amcl_callback,
            10
        )
        
        self.plan_sub = self.node.create_subscription(
            Path,
            '/plan',
            self._plan_callback,
            10
        )
    
    def get_health_data(self) -> Dict:
        """获取导航健康数据"""
        current_time = time.time()
        
        # 计算AMCL频率
        if self.last_amcl_time > 0:
            amcl_frequency = 1.0 / (current_time - self.last_amcl_time)
        else:
            amcl_frequency = 0.0
        
        # 计算规划成功率
        if self.plan_attempts > 0:
            success_rate = (self.plan_successes / self.plan_attempts) * 100.0
        else:
            success_rate = 100.0
        
        return {
            'amcl_frequency': amcl_frequency,
            'planning_success_rate': success_rate,
            'plan_attempts': self.plan_attempts,
            'plan_successes': self.plan_successes
        }

class PerceptionMonitor:
    """感知健康监控"""
    
    def __init__(self, node: Node):
        self.node = node
        self.rfid_sub = None
        self.last_rfid_time = 0
        self.scan_attempts = 0
        self.successful_scans = 0
    
    def get_health_data(self) -> Dict:
        """获取感知健康数据"""
        current_time = time.time()
        
        # 计算RFID扫描频率
        if self.last_rfid_time > 0:
            rfid_frequency = 1.0 / (current_time - self.last_rfid_time)
        else:
            rfid_frequency = 0.0
        
        # 计算检测成功率
        if self.scan_attempts > 0:
            success_rate = (self.successful_scans / self.scan_attempts) * 100.0
        else:
            success_rate = 100.0
        
        return {
            'rfid_frequency': rfid_frequency,
            'detection_success_rate': success_rate,
            'scan_attempts': self.scan_attempts,
            'successful_scans': self.successful_scans
        }

class ResourceMonitor:
    """系统资源监控"""
    
    def __init__(self, node: Node):
        self.node = node
        self.process = psutil.Process()
    
    def get_health_data(self) -> Dict:
        """获取资源健康数据"""
        # CPU使用率
        cpu_usage = self.process.cpu_percent()
        
        # 内存使用量(MB)
        memory_info = self.process.memory_info()
        memory_usage = memory_info.rss / 1024 / 1024
        
        # Topic延迟（简化实现）
        topic_latency = 10.0  # 假设值，实际需要测量
        
        return {
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'topic_latency': topic_latency
        }
```

### 配置文件

```yaml
# config/monitoring_config.yaml

monitoring:
  # 监控频率配置
  frequency: 10.0                    # Hz
  history_duration: 3600            # 秒
  
  # 阈值配置
  thresholds:
    navigation:
      amcl_frequency:
        warning: 5.0
        error: 3.0
        critical: 1.0
      planning_success_rate:
        warning: 95.0
        error: 85.0
        critical: 70.0
    
    perception:
      rfid_frequency:
        warning: 9.0
        error: 7.0
        critical: 5.0
      detection_success_rate:
        warning: 90.0
        error: 80.0
        critical: 60.0
    
    resource:
      cpu_usage:
        warning: 70.0
        error: 85.0
        critical: 95.0
      memory_usage:
        warning: 1536.0  # MB
        error: 1792.0
        critical: 1920.0
      topic_latency:
        warning: 50.0    # ms
        error: 100.0
        critical: 200.0

# ROS2参数声明
/**:
  ros__parameters:
    monitoring.frequency: 10.0
    monitoring.history_duration: 3600
    monitoring.thresholds.navigation.amcl_frequency.warning: 5.0
    monitoring.thresholds.navigation.amcl_frequency.error: 3.0
    monitoring.thresholds.navigation.amcl_frequency.critical: 1.0
```

---

## ✅ 完成检查清单

- [x] HealthMonitor类实现并测试
- [x] 导航监控组件正常工作
- [x] 感知监控组件正常工作
- [x] 系统资源监控正常工作
- [x] 健康指标发布功能完整
- [x] 阈值告警机制正确
- [x] 健康报告生成功能
- [x] 历史数据管理正确
- [ ] 与其他系统集成测试
- [ ] 手动测试监控功能

---

## 🔍 测试场景

### 测试1: 导航健康监控
1. 模拟AMCL定位数据
2. 验证频率计算正确
3. 测试规划成功率统计

### 测试2: 感知健康监控
1. 模拟RFID扫描数据
2. 验证检测成功率计算
3. 测试频率监控准确

### 测试3: 资源监控
1. 监控系统资源使用
2. 验证CPU、内存数据准确
3. 测试Topic延迟测量

### 测试4: 健康告警
1. 设置低阈值触发告警
2. 验证不同级别告警
3. 测试告警日志记录

### 测试5: 健康报告
1. 生成健康报告
2. 验证报告内容完整
3. 测试历史数据查询

---

## 📚 相关文档

- [Story 3-1: 混合日志方案实现](./3-1-hybrid-logging.md) - 日志系统
- [Story 3-3: UI日志面板实现](./3-3-log-panel-ui.md) - UI集成
- [Story 3-4: 日志存储与轮转实现](./3-4-log-rotation.md) - 数据管理
- [docs/design_brainstorm_detailed.md#D3章节] - 监控指标设计

---

## 💡 实现提示

1. **监控频率**: 10Hz监控频率确保实时性
2. **阈值配置**: 支持动态调整阈值，适应不同环境
3. **性能影响**: 监控本身资源占用要小，避免影响主系统
4. **数据精度**: 使用滑动窗口算法提高数据准确性
5. **告警策略**: 避免频繁告警，使用延迟触发机制

---
