# Story 6-1: RFID噪声模型实现

> **Epic**: #6 仿真真实性增强
> **Priority**: P0 (Critical)
> **Points**: 3
> **Status**: ready-for-dev
> **Platform**: ROS2 / Python
> **Dependencies**: Story 5-1 (Topic接口实现)

---

## 📋 用户故事 (User Story)

作为仿真系统开发者，
我希望RFID检测包含真实的噪声模型，
这样可以更准确地模拟真实环境下的检测行为。

---

## 🎯 验收标准 (Acceptance Criteria)

### 功能性要求
- [ ] 实现距离-概率检测曲线
- [ ] 实现15%漏检率模拟
- [ ] 实现误检率控制
- [ ] 支持四向独立噪声模型
- [ ] 可配置的噪声参数

### 性能要求
- [ ] 噪声计算延迟<1ms
- [ ] 不影响主检测性能
- [ ] 内存占用合理

### 代码质量
- [ ] 参数化噪声模型
- [ ] 详细的噪声统计
- [ ] 可重现的随机性

---

## 🔧 实现细节

### 文件清单
```
src/libbot_perception/libbot_perception/
├── rfid_simulator.py            # 新建 - RFID仿真器
├── noise_models.py             # 新建 - 噪声模型
└── config/
    └── rfid_noise_params.yaml   # 新建 - 噪声参数配置
```

### RFID仿真器

```python
# rfid_simulator.py

import rclpy
from rclpy.node import Node
import numpy as np
import math
import time
from typing import List, Dict, Tuple, Optional

from libbot_msgs.msg import RFIDScan
from geometry_msgs.msg import Point

class RFIDNoiseSimulator:
    """RFID噪声仿真器 - 模拟真实RFID检测行为"""
    
    def __init__(self, config: Dict = None):
        """初始化RFID噪声仿真器
        
        Args:
            config: 配置参数
        """
        self.config = config or self._get_default_config()
        self.noise_models = {}
        
        # 初始化四个方向的噪声模型
        self._init_noise_models()
        
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            'directions': ['front', 'back', 'left', 'right'],
            'base_detection_range': 0.5,
            'false_negative_rate': 0.15,
            'false_positive_rate': 0.05,
            'distance_decay_factor': 2.0,
            'angle_sensitivity': 0.8,
            'environment_noise': 0.1
        }
        
    def _init_noise_models(self):
        """初始化各个方向的噪声模型"""
        for direction in self.config['directions']:
            self.noise_models[direction] = RFIDDirectionNoiseModel(
                direction=direction,
                config=self.config
            )
            
    def simulate_detection(self, direction: str, tags_in_range: List[Dict], 
                          robot_pose: Point, timestamp: float) -> RFIDScan:
        """模拟RFID检测过程
        
        Args:
            direction: 检测方向
            tags_in_range: 范围内的标签列表
            robot_pose: 机器人位姿
            timestamp: 时间戳
            
        Returns:
            RFIDScan消息
        """
        if direction not in self.noise_models:
            raise ValueError(f"未知方向: {direction}")
            
        noise_model = self.noise_models[direction]
        
        # 执行噪声检测
        detected_tags = []
        signal_strengths = []
        
        for tag in tags_in_range:
            # 计算检测概率
            detection_prob = self._calculate_detection_probability(
                tag, robot_pose, direction
            )
            
            # 根据概率决定是否检测到
            if np.random.random() < detection_prob:
                detected_tags.append(tag['id'])
                
                # 计算信号强度
                strength = self._calculate_signal_strength(
                    tag, robot_pose, direction
                )
                signal_strengths.append(strength)
                
        # 添加误检（虚假检测）
        false_positives = self._generate_false_positives(direction)
        detected_tags.extend(false_positives)
        signal_strengths.extend([0.3] * len(false_positives))  # 虚假信号强度较低
        
        # 创建RFIDScan消息
        scan_msg = RFIDScan()
        scan_msg.header.stamp = timestamp
        scan_msg.header.frame_id = f"rfid_{direction}"
        
        scan_msg.direction = direction
        scan_msg.detected_tags = detected_tags
        scan_msg.signal_strengths = signal_strengths
        
        scan_msg.scan_range = self.config['base_detection_range']
        scan_msg.scan_angle = 90.0
        scan_msg.scan_timestamp = timestamp
        
        return scan_msg
        
    def _calculate_detection_probability(self, tag: Dict, robot_pose: Point, 
                                       direction: str) -> float:
        """计算检测概率
        
        基于距离、角度和环境因素的复合概率模型
        
        Args:
            tag: 标签信息
            robot_pose: 机器人位姿
            direction: 检测方向
            
        Returns:
            检测概率 (0.0-1.0)
        """
        # 1. 计算距离衰减
        distance = self._calculate_distance(tag['position'], robot_pose)
        distance_prob = self._distance_probability(distance)
        
        # 2. 计算角度影响
        angle_prob = self._angle_probability(tag['position'], robot_pose, direction)
        
        # 3. 环境噪声影响
        noise_factor = 1.0 - self.config['environment_noise']
        
        # 4. 基础漏检率
        base_success_rate = 1.0 - self.config['false_negative_rate']
        
        # 综合概率计算
        final_prob = (
            distance_prob * 
            angle_prob * 
            noise_factor * 
            base_success_rate
        )
        
        # 限制在合理范围内
        return max(0.0, min(1.0, final_prob))
        
    def _calculate_distance(self, tag_pos: Point, robot_pos: Point) -> float:
        """计算标签与机器人的距离"""
        dx = tag_pos.x - robot_pos.x
        dy = tag_pos.y - robot_pos.y
        dz = tag_pos.z - robot_pos.z
        
        return math.sqrt(dx*dx + dy*dy + dz*dz)
        
    def _distance_probability(self, distance: float) -> float:
        """基于距离的检测概率
        
        使用指数衰减模型: P = exp(-distance^2 / range^2)
        """
        range_limit = self.config['base_detection_range']
        
        if distance > range_limit:
            return 0.0
            
        # 指数衰减
        decay_factor = self.config['distance_decay_factor']
        normalized_distance = distance / range_limit
        
        return math.exp(-decay_factor * normalized_distance * normalized_distance)
        
    def _angle_probability(self, tag_pos: Point, robot_pos: Point, 
                          direction: str) -> float:
        """基于角度的检测概率
        
        考虑标签是否在传感器的有效角度范围内
        """
        # 计算机器人到标签的方向
        dx = tag_pos.x - robot_pos.x
        dy = tag_pos.y - robot_pos.y
        
        tag_angle = math.atan2(dy, dx)  # 标签相对于机器人的角度
        
        # 获取传感器方向角度
        sensor_angle = self._get_sensor_angle(direction)
        
        # 计算角度差
        angle_diff = abs(tag_angle - sensor_angle)
        # 归一化到0-π范围
        angle_diff = min(angle_diff, 2*math.pi - angle_diff)
        
        # 传感器视野范围（90度 = π/2弧度）
        fov = math.pi / 2
        
        if angle_diff > fov / 2:
            return 0.0
            
        # 角度敏感度影响
        sensitivity = self.config['angle_sensitivity']
        normalized_angle = (angle_diff / (fov / 2))
        
        return 1.0 - sensitivity * normalized_angle
        
    def _get_sensor_angle(self, direction: str) -> float:
        """获取传感器方向角度"""
        direction_angles = {
            'front': 0.0,           # 0度
            'right': -math.pi/2,    # -90度
            'back': math.pi,        # 180度
            'left': math.pi/2       # 90度
        }
        
        return direction_angles.get(direction, 0.0)
        
    def _calculate_signal_strength(self, tag: Dict, robot_pose: Point,
                                  direction: str) -> float:
        """计算信号强度
        
        基于距离、角度和随机噪声的信号强度模型
        """
        # 基础信号强度（距离衰减）
        distance = self._calculate_distance(tag['position'], robot_pose)
        base_strength = 1.0 / (1.0 + distance * 2.0)
        
        # 角度影响
        angle_factor = self._angle_probability(tag['position'], robot_pose, direction)
        
        # 随机噪声
        noise = np.random.normal(0, 0.1)  # 10%标准差
        
        # 综合计算
        strength = base_strength * angle_factor + noise
        
        # 限制在合理范围内
        return max(0.0, min(1.0, strength))
        
    def _generate_false_positives(self, direction: str) -> List[str]:
        """生成误检（虚假标签）
        
        模拟RFID系统中的误检情况
        """
        false_positives = []
        
        # 根据误检率决定是否生成虚假检测
        if np.random.random() < self.config['false_positive_rate']:
            # 生成1-2个虚假标签
            num_false = np.random.randint(1, 3)
            
            for i in range(num_false):
                false_id = f"false_tag_{np.random.randint(1000, 9999)}"
                false_positives.append(false_id)
                
        return false_positives
        
    def get_noise_statistics(self) -> Dict:
        """获取噪声统计信息"""
        stats = {}
        
        for direction, model in self.noise_models.items():
            stats[direction] = model.get_statistics()
            
        return stats
        
    def reset_statistics(self):
        """重置统计信息"""
        for model in self.noise_models.values():
            model.reset_statistics()


class RFIDDirectionNoiseModel:
    """单个方向的RFID噪声模型"""
    
    def __init__(self, direction: str, config: Dict):
        """初始化方向噪声模型
        
        Args:
            direction: 检测方向
            config: 配置参数
        """
        self.direction = direction
        self.config = config
        
        # 统计数据
        self.total_detections = 0
        self.successful_detections = 0
        self.false_positives = 0
        self.false_negatives = 0
        
        self.signal_strengths = []
        self.detection_probabilities = []
        
    def record_detection(self, expected: bool, actual: bool, 
                        signal_strength: float = 0.0, 
                        detection_prob: float = 0.0):
        """记录一次检测事件
        
        Args:
            expected: 预期是否检测到
            actual: 实际是否检测到
            signal_strength: 信号强度
            detection_prob: 检测概率
        """
        self.total_detections += 1
        
        if actual:
            self.successful_detections += 1
            self.signal_strengths.append(signal_strength)
            
        if expected and not actual:
            self.false_negatives += 1
        elif not expected and actual:
            self.false_positives += 1
            
        self.detection_probabilities.append(detection_prob)
        
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        if self.total_detections == 0:
            return {
                'direction': self.direction,
                'total_detections': 0,
                'success_rate': 0.0,
                'false_positive_rate': 0.0,
                'false_negative_rate': 0.0,
                'avg_signal_strength': 0.0,
                'avg_detection_probability': 0.0
            }
            
        success_rate = self.successful_detections / self.total_detections
        false_positive_rate = self.false_positives / self.total_detections
        false_negative_rate = self.false_negatives / self.total_detections
        
        avg_signal = np.mean(self.signal_strengths) if self.signal_strengths else 0.0
        avg_prob = np.mean(self.detection_probabilities) if self.detection_probabilities else 0.0
        
        return {
            'direction': self.direction,
            'total_detections': self.total_detections,
            'successful_detections': self.successful_detections,
            'false_positives': self.false_positives,
            'false_negatives': self.false_negatives,
            'success_rate': success_rate,
            'false_positive_rate': false_positive_rate,
            'false_negative_rate': false_negative_rate,
            'avg_signal_strength': avg_signal,
            'avg_detection_probability': avg_prob
        }
        
    def reset_statistics(self):
        """重置统计信息"""
        self.total_detections = 0
        self.successful_detections = 0
        self.false_positives = 0
        self.false_negatives = 0
        self.signal_strengths.clear()
        self.detection_probabilities.clear()
```

### 噪声参数配置

```yaml
# config/rfid_noise_params.yaml

rfid_noise:
  # 基础检测参数
  base_parameters:
    detection_range: 0.5                    # 基础检测范围(m)
    scan_angle: 90.0                        # 扫描角度(度)
    update_rate: 10.0                       # 更新频率(Hz)
    
  # 漏检率配置
  false_negative:
    base_rate: 0.15                         # 基础漏检率15%
    distance_factor: 1.5                    # 距离影响因子
    angle_factor: 0.8                       # 角度影响因子
    environmental_factor: 0.1               # 环境噪声因子
    
  # 误检率配置
  false_positive:
    base_rate: 0.05                         # 基础误检率5%
    max_false_tags: 2                       # 最大误检标签数
    min_signal_strength: 0.2                # 误检最小信号强度
    
  # 距离衰减模型
  distance_model:
    type: "exponential"                     # 指数衰减
    decay_factor: 2.0                       # 衰减因子
    max_range: 0.5                          # 最大检测范围
    min_probability: 0.1                    # 最小检测概率
    
  # 角度敏感度模型
  angle_model:
    type: "gaussian"                        # 高斯分布
    sensitivity: 0.8                        # 角度敏感度
    fov: 90.0                               # 视野角度
    center_weight: 1.0                      # 中心权重
    edge_weight: 0.3                        # 边缘权重
    
  # 信号强度模型
  signal_strength:
    base_factor: 1.0                        # 基础因子
    distance_decay: 2.0                     # 距离衰减
    noise_std: 0.1                          # 噪声标准差
    min_strength: 0.0                       # 最小信号强度
    max_strength: 1.0                       # 最大信号强度
    
  # 环境噪声配置
  environmental_noise:
    enable: true                            # 启用环境噪声
    base_level: 0.1                         # 基础噪声水平
    random_walk: 0.05                       # 随机游走因子
    temporal_correlation: 0.3               # 时间相关性
    
  # 方向特定配置
  direction_specific:
    front:
      range_multiplier: 1.0                 # 前向范围乘数
      angle_offset: 0.0                     # 角度偏移
      noise_bias: 0.0                       # 噪声偏置
      
    back:
      range_multiplier: 0.9                 # 后向范围稍小
      angle_offset: 0.0
      noise_bias: 0.05                      # 后向噪声稍大
      
    left:
      range_multiplier: 0.95                # 左向范围
      angle_offset: 0.0
      noise_bias: 0.02
      
    right:
      range_multiplier: 0.95                # 右向范围
      angle_offset: 0.0
      noise_bias: 0.02
      
  # 统计和监控
  statistics:
    enable_logging: true                    # 启用统计日志
    log_interval: 10.0                      # 日志间隔(秒)
    reset_on_start: true                    # 启动时重置统计
    
  # 调试配置
  debug:
    enable_detailed_logging: false          # 详细日志
    log_all_detections: false               # 记录所有检测
    fixed_random_seed: null                 # 固定随机种子(用于重现)
    
# ROS2参数声明
/**:
  ros__parameters:
    rfid_noise.base_parameters.detection_range: 0.5
    rfid_noise.base_parameters.scan_angle: 90.0
    rfid_noise.base_parameters.update_rate: 10.0
    rfid_noise.false_negative.base_rate: 0.15
    rfid_noise.false_positive.base_rate: 0.05
    rfid_noise.distance_model.decay_factor: 2.0
    rfid_noise.angle_model.sensitivity: 0.8
    rfid_noise.signal_strength.noise_std: 0.1
```

---

## ✅ 完成检查清单

- [ ] RFIDNoiseSimulator类实现
- [ ] RFIDDirectionNoiseModel类实现
- [ ] 距离-概率检测模型
- [ ] 角度敏感度模型
- [ ] 信号强度计算模型
- [ ] 误检和漏检模拟
- [ ] 噪声参数配置
- [ ] 统计信息收集
- [ ] 手动测试噪声模型

---

## 🔍 测试场景

### 测试1: 距离衰减测试
1. 在不同距离放置标签
2. 验证检测概率随距离衰减
3. 验证最大检测范围

### 测试2: 角度敏感度测试
1. 在不同角度放置标签
2. 验证中心区域检测率更高
3. 验证视野边缘检测率降低

### 测试3: 噪声统计测试
1. 运行大量检测事件
2. 验证漏检率接近15%
3. 验证误检率接近5%

### 测试4: 信号强度测试
1. 验证信号强度在合理范围
2. 验证距离对信号强度的影响
3. 验证随机噪声的存在

---

## 📚 相关文档

- [Story 6-2: 动态障碍物实现](./6-2-dynamic-obstacles.md) - 动态障碍物
- [Story 6-3: Gazebo Actor配置实现](./6-3-gazebo-actor.md) - Gazebo Actor
- [Story 6-4: 错架/缺失模拟实现](./6-4-misplace-simulation.md) - 错架模拟
- [docs/design_brainstorm_detailed.md#D6章节] - 仿真真实性详细设计

---

## 💡 实现提示

1. **真实性**: 噪声模型要基于真实RFID特性
2. **可配置性**: 所有参数都应该可配置
3. **性能**: 噪声计算要高效，不影响主循环
4. **统计**: 详细的统计数据用于调试和验证
5. **重现性**: 支持固定随机种子用于测试

---
