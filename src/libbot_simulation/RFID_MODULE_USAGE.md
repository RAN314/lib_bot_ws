# RFID仿真模块使用说明

## 📋 模块概述

RFID仿真模块为图书馆机器人提供了完整的RFID检测能力仿真，包括：
- **四向RFID传感器** - 前、后、左、右四个方向的独立检测
- **真实噪声模型** - 模拟距离衰减、漏检率、误检率等真实特性
- **ROS2接口** - 完整的Topic发布和参数配置
- **Gazebo集成** - 可与仿真环境无缝集成

---

## 🚀 快速开始

### 1. 独立测试RFID传感器

```bash
# 启动RFID传感器节点进行测试
ros2 run libbot_simulation rfid_sensor_node

# 在另一个终端运行测试
ros2 run libbot_simulation test_rfid_simulation
```

### 2. 启动完整RFID仿真

```bash
# 启动带RFID的仿真环境
ros2 launch libbot_simulation rfid_simulation.launch.py

# 或使用测试模式（较低频率）
ros2 launch libbot_simulation rfid_simulation.launch.py use_sim_time:=true gui:=true
```

### 3. 与现有系统集成

```bash
# 启动Nav2导航+RFID仿真
ros2 launch libbot_simulation library_nav2_simulation.launch.py
ros2 launch libbot_simulation rfid_simulation.launch.py
```

---

## 📡 Topic接口

### 发布的话题

#### RFID扫描数据
```
/rfid/scan/front     [libbot_msgs/RFIDScan] - 前方RFID扫描
/rfid/scan/back      [libbot_msgs/RFIDScan] - 后方RFID扫描
/rfid/scan/left      [libbot_msgs/RFIDScan] - 左方RFID扫描
/rfid/scan/right     [libbot_msgs/RFIDScan] - 右方RFID扫描
```

#### RFIDScan消息格式
```protobuf
std_msgs/Header header
string antenna_position        # 天线位置: front, back, left, right
string[] detected_book_ids     # 检测到的图书ID列表
float32[] signal_strengths     # 对应信号强度 (0-1)
float32 detection_range        # 检测范围（米）
bool is_moving                 # 机器人是否正在移动
```

### 订阅的话题

```
/robot_pose          [geometry_msgs/Pose] - 机器人位姿（用于检测计算）
/amcl_pose           [geometry_msgs/PoseWithCovarianceStamped] - AMCL定位结果（remap后使用）
```

---

## ⚙️ 配置参数

### 配置文件位置
```
src/libbot_simulation/config/rfid_config.yaml
```

### 主要配置项

#### 噪声模型参数
```yaml
rfid_noise_model:
  base_detection_range: 0.5      # 基础检测范围(米)
  false_negative_rate: 0.15      # 漏检率15%
  false_positive_rate: 0.05      # 误检率5%
  scan_frequency: 10.0           # 扫描频率(Hz)
  distance_decay_factor: 2.0     # 距离衰减因子
  angle_sensitivity: 0.8         # 角度敏感度
```

#### 传感器参数
```yaml
rfid_sensor:
  scan_frequency: 10.0           # 扫描频率
  directions:                    # 检测方向
    - front
    - back
    - left
    - right
  publish_frame_id: "rfid_sensor" # TF坐标系
```

#### 天线配置
```yaml
antennas:
  front:
    position: [0.15, 0.0, 0.1]   # 相对于机器人中心的位置
    orientation: 0.0              # 朝向角度
    gain: 1.0                     # 天线增益
```

---

## 🎯 检测特性

### 距离-概率曲线
- **0-0.2米**: 检测概率 > 90%
- **0.2-0.4米**: 检测概率 70-90%
- **0.4-0.5米**: 检测概率 30-70%
- **>0.5米**: 检测概率 < 30%

### 方向特性
- **前方**: 最佳性能 (基准)
- **后方**: 性能降低10%
- **左右**: 性能降低5%

### 噪声特性
- **漏检率**: 15% (即使标签在范围内也可能检测不到)
- **误检率**: 5% (可能检测到不存在的标签)
- **信号强度**: 随距离衰减，添加随机噪声

---

## 🔧 与现有系统集成

### 1. 错误恢复系统

RFID仿真模块与L1/L2恢复系统完全集成：

```python
# L1 RFID重新扫描恢复
from libbot_tasks import L1RecoveryBehaviors

l1_recovery = L1RecoveryBehaviors(node)
success = l1_recovery.retry_rfid_scan(book_id, position)
```

**UI控制**: 使用左侧面板的"📡 RFID重扫"按钮手动触发恢复

### 2. 健康监控系统

RFID数据自动集成到健康监控：

```python
# 感知监控自动订阅RFID话题
from libbot_monitoring import PerceptionMonitor

monitor = PerceptionMonitor(node)
health_data = monitor.get_health_data()
# 包含: rfid_frequency, detection_success_rate等
```

**监控指标**:
- RFID扫描频率 (期望: 10Hz)
- 检测成功率 (期望: >85%)
- 各方向独立统计

### 3. 日志系统

所有RFID操作自动记录：

```python
from libbot_logging import HybridLogger

logger = HybridLogger()
logger.log_system('INFO', 'RFID扫描开始', 'rfid_sensor')
logger.log_business('rfid_detection', 
                   {'book_id': 'B001', 'direction': 'front'}, 
                   'success', 
                   'rfid_sensor')
```

---

## 📊 诊断和调试

### 获取诊断信息

```python
# 在RFID传感器节点中
diagnostic_info = rfid_node.get_diagnostic_info()
print(f"节点状态: {diagnostic_info['node_status']}")
print(f"扫描频率: {diagnostic_info['scan_frequency']}")
print(f"统计信息: {diagnostic_info['statistics']}")
```

### 重置统计信息

```python
rfid_node.reset_statistics()
```

### 日志级别控制

```bash
# 设置调试日志
ros2 run libbot_simulation rfid_sensor_node --ros-args --log-level DEBUG

# 或在配置文件中设置
debug:
  log_level: "DEBUG"
```

---

## 🧪 测试场景

### 1. 基础功能测试

```bash
# 运行完整测试套件
ros2 run libbot_simulation test_rfid_simulation
```

**测试内容**:
- 噪声模型检测率验证
- 传感器节点通信测试
- 四向检测完整性
- 性能基准测试

### 2. 集成测试

```bash
# 启动仿真环境
ros2 launch libbot_simulation rfid_simulation.launch.py

# 在RVIZ中观察:
# - RFID检测区域
# - 标签位置
# - 实时检测数据
```

### 3. 性能测试

```bash
# 使用性能测试配置
ros2 launch libbot_simulation rfid_simulation.launch.py \
    ros2_params_file:=/path/to/performance_test_params.yaml
```

---

## 🎮 手动测试

### 使用ROS2命令行

```bash
# 查看RFID话题
ros2 topic list | grep rfid

# 查看扫描数据
ros2 topic echo /rfid/scan/front

# 发布测试位姿
ros2 topic pub /robot_pose geometry_msgs/Pose "position: {x: 1.0, y: 2.0, z: 0.0}"
```

### 使用rqt工具

```bash
# 启动rqt监控话题
rqt

# 添加Topic监控插件
# 选择 /rfid/scan/* 话题观察数据流
```

---

## 📈 性能优化

### 调整扫描频率

```yaml
# 降低频率以减少CPU使用
rfid_sensor:
  scan_frequency: 5.0    # 从10Hz降低到5Hz
```

### 优化检测范围

```yaml
# 减小检测范围以提高性能
rfid_noise_model:
  base_detection_range: 0.3    # 从0.5米减小到0.3米
```

### 减少发布数据量

```yaml
# 降低发布频率
rfid_sensor:
  publish_frequency: 5.0    # 独立于扫描频率
```

---

## 🐛 故障排除

### 常见问题

#### 1. 无RFID数据发布
**检查**:
- RFID传感器节点是否正常运行
- 机器人位姿话题是否正常
- 配置参数是否正确

**解决**:
```bash
# 检查节点状态
ros2 node list
ros2 node info /rfid_sensor_node

# 检查话题
ros2 topic list | grep rfid
ros2 topic hz /rfid/scan/front
```

#### 2. 检测率异常
**检查**:
- 机器人与标签的距离
- 噪声模型参数设置
- 环境干扰配置

**解决**:
```yaml
# 调整噪声参数
rfid_noise_model:
  false_negative_rate: 0.10    # 降低漏检率
  environment_noise: 0.05       # 降低环境噪声
```

#### 3. 性能问题
**检查**:
- CPU使用率
- 内存占用
- 话题发布频率

**解决**:
```yaml
# 优化性能参数
rfid_sensor:
  scan_frequency: 5.0          # 降低频率

debug:
  detailed_statistics: false   # 关闭详细统计
```

---

## 📚 API参考

### RFIDNoiseSimulator类

```python
from libbot_simulation.rfid_noise_model import RFIDNoiseSimulator

# 创建模拟器
simulator = RFIDNoiseSimulator(config)

# 执行检测
results = simulator.simulate_detection(
    direction='front',
    tags_in_range=tags,
    robot_pose=(x, y, theta),
    robot_orientation=orientation,
    timestamp=time.time()
)

# 获取统计
stats = simulator.get_statistics()
```

### RFIDSensorNode类

```python
from libbot_simulation.rfid_sensor_node import RFIDSensorNode

# 创建传感器节点
node = RFIDSensorNode(config_file='rfid_config.yaml')

# 获取诊断信息
diagnostic = node.get_diagnostic_info()

# 重置统计
node.reset_statistics()
```

---

## 🎯 最佳实践

### 1. 配置建议
- **仿真环境**: 使用默认参数
- **性能测试**: 降低扫描频率和检测范围
- **真实模拟**: 启用所有噪声特性

### 2. 集成建议
- 与AMCL定位集成时使用`/amcl_pose`话题
- 与错误恢复系统集成时配置合适的超时时间
- 与健康监控集成时关注检测成功率指标

### 3. 调试建议
- 使用RVIZ可视化RFID检测区域
- 监控各方向的独立统计数据
- 定期检查诊断信息

---

**版本**: 1.0.0
**最后更新**: 2026年4月17日
**适用分支**: rfid_sim_integration