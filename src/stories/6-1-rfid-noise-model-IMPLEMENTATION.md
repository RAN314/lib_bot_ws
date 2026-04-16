# Story 6-1: RFID噪声模型实现 - 详细实施计划

## 📋 故事概述

作为仿真系统开发工程师，
我希望实现真实的RFID传感器噪声模型，
这样可以模拟真实环境中RFID检测的不确定性，提高仿真的真实性。

## 🎯 验收标准

### 功能性要求
- [ ] 实现距离-检测概率曲线模型
- [ ] 实现15%的基础漏检率
- [ ] 支持多路径效应模拟
- [ ] 可配置的噪声参数
- [ ] 与Gazebo传感器系统集成

### 性能要求
- [ ] 噪声计算延迟 < 1ms
- [ ] 支持100+ RFID标签同时模拟
- [ ] 内存占用 < 10MB
- [ ] 不影响主仿真性能

### 代码质量
- [ ] 模块化设计，易于配置
- [ ] 完整的参数验证
- [ ] 详细的日志记录
- [ ] 单元测试覆盖

## 🔧 技术实现细节

### 文件结构
```
src/libbot_simulation/
├── libbot_simulation/
│   ├── __init__.py
│   ├── rfid_noise_model.py      # 新建 - RFID噪声模型核心
│   ├── rfid_sensor_plugin.py    # 新建 - Gazebo传感器插件
│   └── config/
│       └── rfid_config.yaml     # 新建 - RFID配置文件
├── test/
│   └── test_rfid_noise.py       # 新建 - 噪声模型测试
├── launch/
│   └── rfid_simulation.launch.py # 新建 - 仿真启动文件
└── worlds/
    └── library_rfid.world       # 新建 - 带RFID的图书馆世界
```

### RFID噪声模型类设计

```python
# rfid_noise_model.py

import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

@dataclass
class RFIDTag:
    """RFID标签定义"""
    id: str
    position: tuple  # (x, y, z)
    power: float      # 标签功率
    enabled: bool    # 是否激活

@dataclass
class DetectionResult:
    """检测结果"""
    tag_id: str
    detected: bool
    signal_strength: float
    distance: float
    confidence: float

class RFIDNoiseModel:
    """RFID噪声模型"""
    
    def __init__(self, config: Dict):
        """
        初始化RFID噪声模型
        
        Args:
            config: 配置参数
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 基础参数
        self.base_miss_rate = config.get('base_miss_rate', 0.15)  # 15%漏检率
        self.max_detection_range = config.get('max_detection_range', 3.0)  # 3米
        self.noise_std = config.get('noise_std', 0.1)  # 噪声标准差
        
        # 距离-概率曲线参数
        self.distance_curve = config.get('distance_curve', {
            'optimal_range': 1.0,    # 最佳检测距离1米
            'falloff_rate': 2.0,     # 衰减率
            'min_probability': 0.1   # 最小检测概率
        })
        
        self.tags: Dict[str, RFIDTag] = {}
        
    def add_tag(self, tag: RFIDTag):
        """添加RFID标签"""
        self.tags[tag.id] = tag
        
    def remove_tag(self, tag_id: str):
        """移除RFID标签"""
        if tag_id in self.tags:
            del self.tags[tag_id]
            
    def calculate_detection_probability(self, distance: float) -> float:
        """
        计算给定距离的检测概率
        
        Args:
            distance: 距离（米）
            
        Returns:
            检测概率 (0.0-1.0)
        """
        if distance > self.max_detection_range:
            return 0.0
            
        # 距离-概率曲线计算
        optimal_range = self.distance_curve['optimal_range']
        falloff_rate = self.distance_curve['falloff_rate']
        min_prob = self.distance_curve['min_probability']
        
        if distance <= optimal_range:
            # 近距离：接近100%检测率
            probability = 1.0 - (distance / optimal_range) * 0.1
        else:
            # 远距离：指数衰减
            excess_distance = distance - optimal_range
            decay = np.exp(-falloff_rate * excess_distance)
            probability = max(min_prob, decay)
            
        # 添加基础漏检率
        probability *= (1.0 - self.base_miss_rate)
        
        return max(0.0, min(1.0, probability))
        
    def simulate_detection(self, sensor_position: tuple, 
                          sensor_orientation: tuple) -> List[DetectionResult]:
        """
        模拟RFID检测
        
        Args:
            sensor_position: 传感器位置 (x, y, z)
            sensor_orientation: 传感器朝向 (roll, pitch, yaw)
            
        Returns:
            检测结果列表
        """
        results = []
        
        for tag_id, tag in self.tags.items():
            if not tag.enabled:
                continue
                
            # 计算距离
            distance = self._calculate_distance(sensor_position, tag.position)
            
            # 计算检测概率
            detection_prob = self.calculate_detection_probability(distance)
            
            # 添加多路径效应
            multipath_factor = self._calculate_multipath_effect(
                sensor_position, tag.position, sensor_orientation
            )
            detection_prob *= multipath_factor
            
            # 随机检测
            detected = np.random.random() < detection_prob
            
            # 计算信号强度
            signal_strength = self._calculate_signal_strength(distance, detected)
            
            # 计算置信度
            confidence = detection_prob if detected else (1.0 - detection_prob)
            
            result = DetectionResult(
                tag_id=tag_id,
                detected=detected,
                signal_strength=signal_strength,
                distance=distance,
                confidence=confidence
            )
            
            results.append(result)
            
        return results
        
    def _calculate_distance(self, pos1: tuple, pos2: tuple) -> float:
        """计算两点间距离"""
        return np.sqrt(sum((a - b) ** 2 for a, b in zip(pos1, pos2)))
        
    def _calculate_multipath_effect(self, sensor_pos: tuple, 
                                   tag_pos: tuple, 
                                   orientation: tuple) -> float:
        """
        计算多路径效应影响因子
        
        模拟信号反射、遮挡等因素
        """
        # 简化的多路径模型
        distance = self._calculate_distance(sensor_pos, tag_pos)
        
        # 距离越远，多路径效应越明显
        multipath_factor = 1.0 - (distance / self.max_detection_range) * 0.3
        
        # 添加随机波动
        noise = np.random.normal(0, self.noise_std)
        multipath_factor += noise
        
        return max(0.1, min(1.0, multipath_factor))
        
    def _calculate_signal_strength(self, distance: float, detected: bool) -> float:
        """
        计算信号强度
        
        Args:
            distance: 距离
            detected: 是否检测到
            
        Returns:
            信号强度 (-100到0 dBm)
        """
        if not detected:
            return -100.0  # 未检测到时返回极弱信号
            
        # 距离衰减模型
        base_strength = -30.0  # 1米处的信号强度
        path_loss = 20 * np.log10(distance)  # 路径损耗
        
        signal_strength = base_strength + path_loss
        
        # 添加噪声
        noise = np.random.normal(0, 2.0)  # 2dB标准差
        signal_strength += noise
        
        return max(-100.0, min(0.0, signal_strength))
```

### Gazebo传感器插件

```python
# rfid_sensor_plugin.py

import os
import sys
import rclpy
from rclpy.node import Node
import gz.msgs as gz_msgs
import gz.transport as gz_transport
from typing import Dict, List

from .rfid_noise_model import RFIDNoiseModel, RFIDTag

class RFIDSensorPlugin:
    """Gazebo RFID传感器插件"""
    
    def __init__(self):
        """初始化插件"""
        self.node = None
        self.rfid_model = None
        self.sensor_topic = "/rfid/scan"
        
    def configure(self, _entity, _sdf, _register_update_callback, _node):
        """配置插件"""
        self.node = _node
        
        # 创建ROS2节点
        plugin_name = f"rfid_sensor_{_entity}"
        self.ros_node = Node(plugin_name)
        
        # 创建RFID噪声模型
        config = self._load_config()
        self.rfid_model = RFIDNoiseModel(config)
        
        # 设置发布者
        self.publisher = self.ros_node.create_publisher(
            RFIDScanMsg, self.sensor_topic, 10
        )
        
        # 加载RFID标签
        self._load_rfid_tags(_sdf)
        
        self.ros_node.get_logger().info(f"RFID传感器插件已配置: {plugin_name}")
        
    def update(self, _msg, _time):
        """更新回调"""
        # 获取传感器位置和朝向
        sensor_pose = self._get_sensor_pose(_msg)
        
        # 模拟RFID检测
        detections = self.rfid_model.simulate_detection(
            sensor_pose['position'],
            sensor_pose['orientation']
        )
        
        # 发布检测结果
        self._publish_detections(detections)
        
    def _load_config(self) -> Dict:
        """加载配置文件"""
        # 简化的配置加载
        return {
            'base_miss_rate': 0.15,
            'max_detection_range': 3.0,
            'noise_std': 0.1,
            'distance_curve': {
                'optimal_range': 1.0,
                'falloff_rate': 2.0,
                'min_probability': 0.1
            }
        }
        
    def _load_rfid_tags(self, sdf):
        """从SDF加载RFID标签"""
        # 解析SDF中的RFID标签定义
        # 这里需要根据实际的SDF结构来实现
        pass
        
    def _get_sensor_pose(self, msg) -> Dict:
        """获取传感器位姿"""
        # 从Gazebo消息中提取位置和朝向
        # 返回格式: {'position': (x,y,z), 'orientation': (r,p,y)}
        pass
        
    def _publish_detections(self, detections: List):
        """发布检测结果"""
        # 创建ROS2消息并发布
        pass
```

### 配置文件

```yaml
# config/rfid_config.yaml

rfid_noise_model:
  # 基础参数
  base_miss_rate: 0.15           # 15%基础漏检率
  max_detection_range: 3.0       # 最大检测距离（米）
  noise_std: 0.1                 # 噪声标准差
  
  # 距离-概率曲线
  distance_curve:
    optimal_range: 1.0            # 最佳检测距离（米）
    falloff_rate: 2.0             # 衰减率
    min_probability: 0.1          # 最小检测概率
  
  # 信号强度模型
  signal_model:
    base_strength: -30.0          # 1米处信号强度(dBm)
    path_loss_exponent: 2.0       # 路径损耗指数
    noise_std: 2.0                # 信号强度噪声
  
  # 多路径效应
  multipath:
    enabled: true
    max_attenuation: 0.3          # 最大衰减因子
    
# Gazebo插件配置
gazebo_plugin:
  update_rate: 10.0              # 更新频率(Hz)
  sensor_topic: "/rfid/scan"      # 发布主题
  
# 标签配置
tags:
  # 示例标签定义
  - id: "book_001"
    position: [1.0, 2.0, 0.5]
    power: 1.0
    enabled: true
  - id: "book_002" 
    position: [2.0, 3.0, 0.5]
    power: 1.0
    enabled: true
```

## 📅 实施计划

### 第1天：环境评估和基础架构

**上午 (9:00-12:00)**
1. **环境检查**
   ```bash
   # 检查Gazebo安装
   gazebo --version
   
   # 检查ROS2环境
   printenv | grep ROS
   
   # 查找现有机器人模型
   find /home/lhl/lib_bot_ws -name "*.urdf" -o -name "*.sdf"
   ```

2. **项目结构创建**
   ```bash
   mkdir -p src/libbot_simulation/libbot_simulation
   mkdir -p src/libbot_simulation/libbot_simulation/config
   mkdir -p src/libbot_simulation/test
   mkdir -p src/libbot_simulation/launch
   mkdir -p src/libbot_simulation/worlds
   ```

**下午 (14:00-17:00)**
1. **RFID噪声模型基础类**
   - 创建 `rfid_noise_model.py`
   - 实现基础数据结构和参数
   - 编写距离-概率计算函数

**产出**: 基础RFID噪声模型类，环境评估报告

### 第2天：核心算法实现

**上午 (9:00-12:00)**
1. **完善噪声模型**
   - 实现多路径效应计算
   - 实现信号强度计算
   - 添加随机噪声生成

2. **参数验证**
   - 验证距离-概率曲线的合理性
   - 测试不同距离下的检测概率
   - 调整参数达到15%漏检率

**下午 (14:00-17:00)**
1. **单元测试编写**
   - 创建 `test_rfid_noise.py`
   - 测试距离计算
   - 测试概率计算
   - 测试检测模拟

**产出**: 完整的RFID噪声模型，单元测试

### 第3天：Gazebo插件开发

**上午 (9:00-12:00)**
1. **插件基础结构**
   - 创建 `rfid_sensor_plugin.py`
   - 实现插件接口
   - 集成RFID噪声模型

2. **ROS2集成**
   - 创建ROS2节点
   - 设置消息发布者
   - 实现检测数据发布

**下午 (14:00-17:00)**
1. **配置文件**
   - 创建 `rfid_config.yaml`
   - 实现配置加载
   - 参数验证和默认值

**产出**: Gazebo传感器插件，配置文件

### 第4天：仿真环境集成

**上午 (9:00-12:00)**
1. **世界文件创建**
   - 创建 `library_rfid.world`
   - 添加RFID标签定义
   - 配置传感器插件

2. **启动文件**
   - 创建 `rfid_simulation.launch.py`
   - 配置ROS2节点
   - 设置仿真参数

**下午 (14:00-17:00)**
1. **集成测试**
   - 启动仿真环境
   - 验证RFID检测
   - 调试和优化

**产出**: 完整的仿真环境，集成测试报告

### 第5天：测试和优化

**全天 (9:00-17:00)**
1. **性能测试**
   - 测试100+标签的模拟性能
   - 测量计算延迟
   - 优化算法效率

2. **真实性验证**
   - 验证检测概率分布
   - 验证信号强度变化
   - 调整参数提高真实性

3. **文档完善**
   - 更新README
   - 编写使用指南
   - 记录测试结果

**产出**: 性能测试报告，用户文档，优化后的系统

## 🧪 测试方案

### 单元测试
```python
# test_rfid_noise.py

def test_distance_probability_curve():
    """测试距离-概率曲线"""
    model = RFIDNoiseModel(config)
    
    # 测试不同距离的概率
    assert model.calculate_detection_probability(0.5) > 0.8  # 近距离高概率
    assert model.calculate_detection_probability(1.0) > 0.7  # 最佳距离
    assert model.calculate_detection_probability(2.0) < 0.5  # 中距离降低
    assert model.calculate_detection_probability(3.0) < 0.2  # 远距离低概率
    assert model.calculate_detection_probability(5.0) == 0.0  # 超出范围

def test_base_miss_rate():
    """测试基础漏检率"""
    model = RFIDNoiseModel({'base_miss_rate': 0.15})
    
    # 在最佳距离进行大量测试
    detections = []
    for _ in range(1000):
        result = model.simulate_detection((0,0,0), (0,0,0))
        if result:
            detections.append(result[0].detected)
    
    detection_rate = sum(detections) / len(detections)
    assert 0.80 < detection_rate < 0.90  # 考虑15%漏检率后的期望值
```

### 集成测试
```python
# test_integration.py

def test_gazebo_integration():
    """测试Gazebo集成"""
    # 启动仿真环境
    # 验证RFID检测数据发布
    # 检查数据格式和频率
    pass
```

## 📊 预期成果

### 代码产出
- ✅ `rfid_noise_model.py` - 完整的噪声模型
- ✅ `rfid_sensor_plugin.py` - Gazebo传感器插件
- ✅ `rfid_config.yaml` - 配置文件
- ✅ `test_rfid_noise.py` - 单元测试
- ✅ `library_rfid.world` - 仿真世界
- ✅ `rfid_simulation.launch.py` - 启动文件

### 文档产出
- ✅ 环境评估报告
- ✅ 设计文档
- ✅ 用户指南
- ✅ 测试报告

### 功能特性
- ✅ 真实的RFID噪声模拟
- ✅ 可配置的参数系统
- ✅ 与Gazebo无缝集成
- ✅ 完整的测试覆盖

## 🎯 成功标准

1. **功能完整**: 所有验收标准达成
2. **性能达标**: 满足性能要求
3. **真实性强**: 模拟效果接近真实RFID
4. **易于使用**: 配置简单，文档完整
5. **可扩展**: 支持后续功能扩展

**RFID噪声模型实现完成后，将为图书馆机器人提供真实的RFID检测仿真基础！** 📡