# Story 2-3: 错误检测机制实现

> **Epic**: #2 错误处理与恢复机制
> **Priority**: P0 (Critical)
> **Points**: 3
> **Status**: ready-for-dev
> **Platform**: ROS2 / Python
> **Dependencies**: Story 2-1 (L1恢复行为实现), Story 2-2 (L2恢复行为实现)

---

## 📋 用户故事 (User Story)

作为图书馆机器人系统操作员，
我希望系统能够自动检测各种故障和异常情况，
这样可以及时触发相应的恢复机制，保证系统稳定运行。

---

## 🎯 验收标准 (Acceptance Criteria)

### 功能性要求
- [ ] 实现定位误差检测机制
- [ ] 实现路径规划失败检测
- [ ] 实现机器人卡住检测
- [ ] 实现RFID检测异常识别
- [ ] 实现系统健康状态监控
- [ ] 错误分类和严重程度分级
- [ ] 自动触发相应的恢复机制

### 性能要求
- [ ] 检测延迟不超过1秒
- [ ] 误报率低于5%
- [ ] 检测覆盖率100%

### 代码质量
- [ ] 模块化错误检测器设计
- [ ] 可配置的阈值参数
- [ ] 详细的错误日志记录

---

## 🔧 实现细节

### 文件清单
```
src/libbot_tasks/libbot_tasks/
├── error_detector.py            # 新建 - 错误检测主类
├── detectors/
│   ├── localization_detector.py # 新建 - 定位错误检测
│   ├── navigation_detector.py   # 新建 - 导航错误检测
│   ├── perception_detector.py   # 新建 - 感知错误检测
│   └── system_detector.py       # 新建 - 系统健康检测
└── config/
    └── error_detection_params.yaml # 新建 - 检测参数配置
```

### ErrorDetector主类

```python
# error_detector.py

import rclpy
from rclpy.node import Node
from typing import Dict, List, Optional
import time
import threading

class ErrorDetector:
    """错误检测机制主类 - 统一管理和协调各类错误检测"""
    
    def __init__(self, node: Node):
        """初始化错误检测器
        
        Args:
            node: ROS2节点实例
        """
        self.node = node
        self.detectors = {}
        self.error_callbacks = []
        self.is_running = False
        self.detection_thread = None
        
        # 初始化各类检测器
        self._init_detectors()
        
    def _init_detectors(self):
        """初始化所有错误检测器"""
        from .detectors.localization_detector import LocalizationErrorDetector
        from .detectors.navigation_detector import NavigationErrorDetector
        from .detectors.perception_detector import PerceptionErrorDetector
        from .detectors.system_detector import SystemHealthDetector
        
        self.detectors = {
            'localization': LocalizationErrorDetector(self.node),
            'navigation': NavigationErrorDetector(self.node),
            'perception': PerceptionErrorDetector(self.node),
            'system': SystemHealthDetector(self.node)
        }
        
    def register_error_callback(self, callback):
        """注册错误回调函数
        
        Args:
            callback: 回调函数，接收错误信息字典
        """
        self.error_callbacks.append(callback)
        
    def start_detection(self):
        """启动错误检测"""
        if self.is_running:
            return
            
        self.is_running = True
        self.detection_thread = threading.Thread(
            target=self._detection_loop,
            daemon=True
        )
        self.detection_thread.start()
        
        self.node.get_logger().info("错误检测器启动")
        
    def stop_detection(self):
        """停止错误检测"""
        self.is_running = False
        if self.detection_thread:
            self.detection_thread.join(timeout=2.0)
        self.node.get_logger().info("错误检测器停止")
        
    def _detection_loop(self):
        """检测主循环"""
        while self.is_running and rclpy.ok():
            try:
                self._run_all_detections()
                time.sleep(0.1)  # 10Hz检测频率
            except Exception as e:
                self.node.get_logger().error(f"检测循环错误: {str(e)}")
                
    def _run_all_detections(self):
        """运行所有检测器"""
        for detector_name, detector in self.detectors.items():
            try:
                errors = detector.detect()
                for error in errors:
                    self._handle_error(detector_name, error)
            except Exception as e:
                self.node.get_logger().error(
                    f"检测器 {detector_name} 运行错误: {str(e)}"
                )
                
    def _handle_error(self, detector_type: str, error_info: Dict):
        """处理检测到的错误
        
        Args:
            detector_type: 检测器类型
            error_info: 错误信息
        """
        # 完善错误信息
        error_info['detector_type'] = detector_type
        error_info['timestamp'] = time.time()
        error_info['error_id'] = f"{detector_type}_{int(time.time() * 1000)}"
        
        # 错误分类和严重程度分级
        error_info = self._classify_error(error_info)
        
        # 记录错误日志
        self._log_error(error_info)
        
        # 调用所有注册的回调函数
        for callback in self.error_callbacks:
            try:
                callback(error_info)
            except Exception as e:
                self.node.get_logger().error(
                    f"错误回调执行失败: {str(e)}"
                )
                
    def _classify_error(self, error_info: Dict) -> Dict:
        """错误分类和严重程度分级
        
        错误严重程度分级：
        - Fatal: 系统级故障，需要立即停机
        - Critical: 关键功能故障，需要L3恢复
        - Error: 功能错误，需要L2恢复
        - Warning: 轻微问题，需要L1恢复
        
        Args:
            error_info: 错误信息
            
        Returns:
            完善后的错误信息
        """
        error_type = error_info.get('error_type', 'unknown')
        
        # 根据错误类型分类
        severity_mapping = {
            # 定位相关错误
            'localization_lost': 'Critical',
            'localization_drift': 'Error',
            'low_localization_confidence': 'Warning',
            
            # 导航相关错误
            'navigation_stuck': 'Error',
            'path_planning_failed': 'Error',
            'collision_imminent': 'Critical',
            'goal_unreachable': 'Error',
            
            # 感知相关错误
            'rfid_detection_failed': 'Warning',
            'sensor_timeout': 'Error',
            'perception_low_confidence': 'Warning',
            
            # 系统相关错误
            'node_crash': 'Fatal',
            'memory_exhausted': 'Critical',
            'cpu_overload': 'Error',
            'communication_timeout': 'Error'
        }
        
        error_info['severity'] = severity_mapping.get(error_type, 'Warning')
        error_info['recovery_level'] = self._get_recovery_level(error_info['severity'])
        
        return error_info
        
    def _get_recovery_level(self, severity: str) -> str:
        """根据严重程度确定恢复级别"""
        recovery_mapping = {
            'Fatal': 'L3',
            'Critical': 'L3',
            'Error': 'L2',
            'Warning': 'L1'
        }
        return recovery_mapping.get(severity, 'L1')
        
    def _log_error(self, error_info: Dict):
        """记录错误日志"""
        severity = error_info.get('severity', 'Warning')
        error_type = error_info.get('error_type', 'unknown')
        message = error_info.get('message', 'No message')
        
        log_message = (
            f"错误检测 [{severity}] {error_type}: {message} "
            f"(ID: {error_info.get('error_id', 'unknown')})"
        )
        
        if severity == 'Fatal':
            self.node.get_logger().fatal(log_message)
        elif severity == 'Critical':
            self.node.get_logger().error(log_message)
        elif severity == 'Error':
            self.node.get_logger().warn(log_message)
        else:
            self.node.get_logger().info(log_message)
            
    def get_detector_status(self) -> Dict:
        """获取所有检测器状态"""
        status = {}
        for name, detector in self.detectors.items():
            status[name] = detector.get_status()
        return status
        
    def reset_detector(self, detector_name: str):
        """重置指定检测器"""
        if detector_name in self.detectors:
            self.detectors[detector_name].reset()
            self.node.get_logger().info(f"检测器 {detector_name} 已重置")
        else:
            self.node.get_logger().warn(f"未知检测器: {detector_name}")
```

### 定位错误检测器

```python
# detectors/localization_detector.py

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped, Odometry
from nav_msgs.msg import OccupancyGrid
import numpy as np
import time

class LocalizationErrorDetector:
    """定位错误检测器 - 检测AMCL定位相关问题"""
    
    def __init__(self, node: Node):
        """初始化定位错误检测器"""
        self.node = node
        self.pose_covariance_threshold = 0.5  # 协方差阈值
        self.drift_distance_threshold = 0.3   # 漂移距离阈值
        self.last_pose = None
        self.last_pose_time = None
        self.pose_history = []  # 位姿历史记录
        self.max_history_size = 10
        
        # 订阅相关Topic
        self.pose_sub = node.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self._pose_callback,
            10
        )
        
        self.odom_sub = node.create_subscription(
            Odometry,
            '/odom',
            self._odom_callback,
            10
        )
        
    def detect(self) -> list:
        """执行定位错误检测
        
        Returns:
            检测到的错误列表
        """
        errors = []
        
        # 检测定位协方差过大
        errors.extend(self._check_covariance())
        
        # 检测定位漂移
        errors.extend(self._check_localization_drift())
        
        # 检测定位丢失
        errors.extend(self._check_localization_lost())
        
        return errors
        
    def _pose_callback(self, msg: PoseWithCovarianceStamped):
        """位姿消息回调"""
        current_time = time.time()
        
        # 更新位姿历史
        pose_info = {
            'timestamp': current_time,
            'position': msg.pose.pose.position,
            'covariance': msg.pose.covariance,
            'confidence': self._calculate_confidence(msg.pose.covariance)
        }
        
        self.pose_history.append(pose_info)
        
        # 保持历史记录大小
        if len(self.pose_history) > self.max_history_size:
            self.pose_history.pop(0)
            
        self.last_pose = pose_info
        self.last_pose_time = current_time
        
    def _odom_callback(self, msg: Odometry):
        """里程计消息回调"""
        # 用于与定位结果对比，检测漂移
        pass
        
    def _check_covariance(self) -> list:
        """检查定位协方差是否过大"""
        errors = []
        
        if not self.last_pose:
            return errors
            
        # 计算位置协方差（取x,y方向的方差）
        position_variance = (
            self.last_pose['covariance'][0] +  # x方向方差
            self.last_pose['covariance'][7]    # y方向方差
        )
        
        if position_variance > self.pose_covariance_threshold:
            errors.append({
                'error_type': 'localization_high_covariance',
                'message': f'定位协方差过大: {position_variance:.3f}',
                'covariance': position_variance,
                'threshold': self.pose_covariance_threshold
            })
            
        return errors
        
    def _check_localization_drift(self) -> list:
        """检查定位漂移"""
        errors = []
        
        if len(self.pose_history) < 2:
            return errors
            
        # 计算最近两个位姿之间的距离
        recent = self.pose_history[-1]
        previous = self.pose_history[-2]
        
        time_diff = recent['timestamp'] - previous['timestamp']
        if time_diff == 0:
            return errors
            
        # 计算位移
        dx = recent['position'].x - previous['position'].x
        dy = recent['position'].y - previous['position'].y
        distance = np.sqrt(dx*dx + dy*dy)
        
        # 计算速度
        velocity = distance / time_diff
        
        # 如果速度异常大，可能是定位漂移
        if velocity > 2.0:  # 2m/s阈值
            errors.append({
                'error_type': 'localization_drift',
                'message': f'检测到定位漂移: 速度 {velocity:.2f} m/s',
                'velocity': velocity,
                'distance': distance,
                'time_diff': time_diff
            })
            
        return errors
        
    def _check_localization_lost(self) -> list:
        """检查定位是否丢失"""
        errors = []
        
        if not self.last_pose_time:
            return errors
            
        # 如果超过5秒没有收到定位更新，认为定位丢失
        current_time = time.time()
        time_since_last_pose = current_time - self.last_pose_time
        
        if time_since_last_pose > 5.0:
            errors.append({
                'error_type': 'localization_lost',
                'message': f'定位丢失: {time_since_last_pose:.1f} 秒无更新',
                'time_since_update': time_since_last_pose
            })
            
        return errors
        
    def _calculate_confidence(self, covariance: list) -> float:
        """计算定位置信度 (0.0-1.0)"""
        # 基于协方差计算置信度
        position_variance = covariance[0] + covariance[7]  # x,y方向方差和
        
        # 方差越小，置信度越高
        confidence = 1.0 / (1.0 + position_variance)
        return min(max(confidence, 0.0), 1.0)  # 限制在0-1范围内
        
    def get_status(self) -> dict:
        """获取检测器状态"""
        status = {
            'last_pose_time': self.last_pose_time,
            'history_size': len(self.pose_history),
            'last_confidence': self.last_pose['confidence'] if self.last_pose else 0.0
        }
        return status
        
    def reset(self):
        """重置检测器"""
        self.last_pose = None
        self.last_pose_time = None
        self.pose_history.clear()
```

### 配置文件

```yaml
# config/error_detection_params.yaml

detection:
  # 检测频率
  detection_frequency: 10.0          # Hz
  
  # 定位检测参数
  localization:
    covariance_threshold: 0.5         # 协方差阈值
    drift_velocity_threshold: 2.0     # 漂移速度阈值(m/s)
    lost_timeout: 5.0                 # 定位丢失超时(秒)
    history_size: 10                  # 历史记录大小
    
  # 导航检测参数
  navigation:
    stuck_timeout: 30.0              # 卡住超时(秒)
    planning_timeout: 10.0            # 规划超时(秒)
    collision_distance_threshold: 0.3 # 碰撞距离阈值(m)
    goal_unreachable_timeout: 60.0    # 目标不可达超时(秒)
    
  # 感知检测参数
  perception:
    rfid_timeout: 5.0                # RFID检测超时(秒)
    detection_confidence_threshold: 0.7 # 检测置信度阈值
    sensor_health_check_interval: 2.0 # 传感器健康检查间隔(秒)
    
  # 系统检测参数
  system:
    node_health_timeout: 10.0        # 节点健康超时(秒)
    memory_usage_threshold: 0.9      # 内存使用率阈值
    cpu_usage_threshold: 0.8         # CPU使用率阈值
    communication_timeout: 2.0       # 通信超时(秒)

# ROS2参数声明
/**:
  ros__parameters:
    detection.detection_frequency: 10.0
    detection.localization.covariance_threshold: 0.5
    detection.localization.drift_velocity_threshold: 2.0
    detection.localization.lost_timeout: 5.0
    detection.localization.history_size: 10
    detection.navigation.stuck_timeout: 30.0
    detection.navigation.planning_timeout: 10.0
    detection.navigation.collision_distance_threshold: 0.3
    detection.navigation.goal_unreachable_timeout: 60.0
    detection.perception.rfid_timeout: 5.0
    detection.perception.detection_confidence_threshold: 0.7
    detection.perception.sensor_health_check_interval: 2.0
    detection.system.node_health_timeout: 10.0
    detection.system.memory_usage_threshold: 0.9
    detection.system.cpu_usage_threshold: 0.8
    detection.system.communication_timeout: 2.0
```

---

## ✅ 完成检查清单

- [ ] ErrorDetector主类实现并测试
- [ ] 定位错误检测器实现
- [ ] 导航错误检测器实现
- [ ] 感知错误检测器实现
- [ ] 系统健康检测器实现
- [ ] 配置文件参数合理
- [ ] 错误分类机制正确
- [ ] 回调系统集成正确
- [ ] 检测器状态监控功能
- [ ] 手动测试错误检测流程

---

## 🔍 测试场景

### 测试1: 定位错误检测
1. 模拟AMCL定位协方差过大
2. 验证检测到高协方差错误
3. 验证错误分类为Error级别

### 测试2: 导航卡住检测
1. 模拟机器人卡住情况
2. 验证检测到navigation_stuck错误
3. 验证自动触发L2恢复

### 测试3: 系统健康检测
1. 模拟节点通信超时
2. 验证检测到系统错误
3. 验证错误回调正确执行

### 测试4: 错误分类验证
1. 触发不同类型的错误
2. 验证错误严重程度分级正确
3. 验证相应的恢复级别匹配

---

## 📚 相关文档

- [Story 2-1: L1恢复行为实现](./2-1-l1-recovery.md) - L1恢复
- [Story 2-2: L2恢复行为实现](./2-2-l2-recovery.md) - L2恢复
- [Story 2-4: 与Behavior Tree集成](./2-4-bt-integration.md) - BT集成
- [docs/design_brainstorm_detailed.md#D2章节] - 错误处理详细设计

---

## 💡 实现提示

1. **检测器模块化**: 每个检测器负责特定类型的错误检测
2. **性能优化**: 检测频率可配置，避免过度消耗CPU
3. **误报控制**: 设置合理的阈值，避免频繁误报
4. **状态管理**: 保持检测器状态，便于调试和监控
5. **回调机制**: 支持多个错误处理模块注册回调

---
