# L1恢复行为模块

图书馆机器人ROS2项目 - Epic 2错误处理与恢复机制

## 📋 概述

L1恢复行为模块实现了图书馆机器人的快速错误恢复功能，能够在5-10秒内自动处理轻微故障，确保系统持续运行而无需人工干预。

## 🎯 功能特性

### 核心恢复行为
- **RFID重新扫描**: 当RFID检测失败时自动重新扫描
- **重新定位**: 当导航偏差过大时执行原地旋转重新定位
- **目标重定义**: 当目标不可达时智能寻找替代目标

### 技术特点
- **快速恢复**: 所有L1恢复操作在10秒内完成
- **重试机制**: 最多重试3次，失败后自动升级到L2
- **参数化配置**: 完整的ROS2参数系统
- **BehaviorTree集成**: 使用BehaviorTree.CPP实现
- **详细日志**: 完整的恢复过程记录

## 📁 文件结构

```
src/libbot_tasks/
├── libbot_tasks/
│   ├── recovery_behaviors.py        # L1恢复行为主类
│   ├── behaviors/
│   │   └── recovery_nodes.xml       # BehaviorTree节点定义
│   └── config/
│       └── recovery_params.yaml     # 恢复参数配置
└── test/
    ├── test_l1_recovery.py          # 单元测试
    └── test_l1_recovery_integration.py # 集成测试
```

## 🚀 快速开始

### 1. 基本使用

```python
import rclpy
from rclpy.node import Node
from libbot_tasks.libbot_tasks.recovery_behaviors import L1RecoveryBehaviors

# 创建ROS2节点
rclpy.init()
node = Node('recovery_test_node')

# 创建L1恢复实例
recovery = L1RecoveryBehaviors(node)

# 执行RFID重新扫描
result = recovery.retry_rfid_scan("book_001", {'x': 1.0, 'y': 2.0})

# 执行重新定位
result = recovery.relocalize_robot()

# 执行目标重定义
alternative = recovery.redefine_target(original_goal)

# 清理资源
recovery.cleanup()
```

### 2. ROS2参数配置

```bash
# 启动时加载参数
ros2 run libbot_tasks l1_recovery_node --ros-args --params-file src/libbot_tasks/libbot_tasks/config/recovery_params.yaml
```

## ⚙️ 配置参数

### 基础参数
- `recovery.l1.max_retries`: 最大重试次数 (默认: 3)
- `recovery.l1.timeout_seconds`: 超时时间 (默认: 10秒)

### RFID重新扫描参数
- `recovery.l1.rfid_rescan.scan_duration`: 扫描持续时间 (默认: 5秒)
- `recovery.l1.rfid_rescan.required_confidence`: 置信度阈值 (默认: 0.8)

### 重新定位参数
- `recovery.l1.relocalization.rotation_speed`: 旋转速度 (默认: 0.3 rad/s)
- `recovery.l1.relocalization.total_rotation`: 总旋转角度 (默认: 6.28 rad = 360°)

### 目标重定义参数
- `recovery.l1.target_redefinition.search_radius`: 搜索半径 (默认: 2.0米)
- `recovery.l1.target_redefinition.max_alternatives`: 最大备选目标数 (默认: 5)

## 🧪 测试

### 运行单元测试

```bash
# 运行所有测试
python3 -m pytest src/libbot_tasks/test/test_l1_recovery.py -v

# 运行集成测试
python3 -m pytest src/libbot_tasks/test/test_l1_recovery_integration.py -v

# 运行所有测试并生成覆盖率报告
python3 -m pytest src/libbot_tasks/test/ --cov=libbot_tasks.libbot_tasks.recovery_behaviors --cov-report=html
```

### 测试场景

1. **RFID检测失败恢复测试** - 验证重新扫描功能
2. **定位丢失恢复测试** - 验证重新定位功能
3. **目标不可达恢复测试** - 验证目标重定义功能
4. **恢复超时处理测试** - 验证超时机制
5. **并发操作测试** - 验证多线程安全性

## 📊 性能指标

- **恢复时间**: < 10秒
- **重试次数**: ≤ 3次
- **内存占用**: < 10MB
- **CPU使用率**: < 5%
- **成功率**: > 85%

## 🔧 开发指南

### 扩展新的恢复行为

1. 在`recovery_behaviors.py`中添加新的恢复方法
2. 在`recovery_nodes.xml`中定义对应的BehaviorTree节点
3. 在`recovery_params.yaml`中添加必要的配置参数
4. 编写对应的单元测试和集成测试

### 调试技巧

1. **启用DEBUG日志**:
   ```yaml
   recovery.l1.logging.level: "DEBUG"
   recovery.l1.logging.enable_detailed_timing: true
   ```

2. **调整超时时间**:
   ```yaml
   recovery.l1.timeout_seconds: 15  # 延长超时时间便于调试
   ```

3. **使用ROS2命令行工具**:
   ```bash
   # 查看参数
   ros2 param list

   # 动态修改参数
   ros2 param set /recovery_node recovery.l1.max_retries 5

   # 查看日志
   ros2 topic echo /rosout
   ```

## 🔗 相关文档

- [Story 2-1: L1恢复行为实现](../stories/2-1-l1-recovery.md)
- [Story 2-2: L2恢复行为实现](../stories/2-2-l2-recovery.md)
- [Epic 2开发计划](../../docs/epic2_development_plan.md)
- [详细设计文档](../../docs/design_brainstorm_detailed.md#D2章节)

## 📝 版本历史

### v1.0.0 (2026-04-09)
- 初始版本发布
- 实现RFID重新扫描恢复
- 实现重新定位恢复
- 实现目标重定义恢复
- 完成完整的测试覆盖

## 🤝 贡献指南

1. 遵循ROS2和Python编码规范
2. 为新功能添加完整的测试覆盖
3. 更新相关文档
4. 确保所有测试通过

## 📄 许可证

本项目遵循项目主许可证。