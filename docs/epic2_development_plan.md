# Epic 2 开发计划总结：错误处理与恢复机制

## 📋 文档概述

本文档总结了Epic 2（错误处理与恢复机制）的完整开发计划，包括技术架构、实施步骤、接口设计和开发前的准备工作。

---

## 🎯 Epic 2 目标

实现图书馆机器人系统的三层错误处理与恢复机制：
- **L1快速恢复**：任务内部处理，5-10秒恢复时间
- **L2状态重置**：任务层面重置，30-40秒恢复时间  
- **L3系统重置**：系统级重置（Phase 2+实现）

---

## 📦 核心功能包：libbot_tasks

### **包职责**
`libbot_tasks`包将作为任务管理层，负责：
1. **错误检测与监控** - 实时检测系统各种故障
2. **恢复策略执行** - 执行L1/L2恢复行为
3. **行为树管理** - 协调所有行为树的执行
4. **任务管理** - FindBook等核心任务实现

### **与其他包的协作关系**

| 包名 | 职责 | 与Epic 2的关系 |
|------|------|---------------|
| `libbot_navigation` | 导航基础设施（Nav2、AMCL） | 被调用：寻路、重定位、代价地图管理 |
| `libbot_perception` | 感知基础设施（RFID、激光雷达） | 被监控：传感器健康状态检测 |
| `libbot_msgs` | ROS2消息定义 | 使用：SystemHealth、RFIDScan等消息 |
| `libbot_ui` | 用户界面 | 提供：错误状态显示和用户反馈 |

---

## 🏗️ 技术架构：双层设计

### **1. 决策层（Behavior Tree）**
- XML配置的行为树定义
- 可视化调试支持（Groot工具）
- 反应式决策逻辑
- 10Hz执行频率

### **2. 算法层（Python实现）**
- 错误检测算法
- 恢复策略实现
- ROS2接口调用
- 性能优化

### **架构优势**
- **关注点分离**：决策逻辑与算法实现解耦
- **可维护性**：行为树可热重载，算法可独立优化
- **可测试性**：两层可分别进行单元测试
- **可配置性**：参数化设计，支持动态调整

---

## 📚 四个故事实施计划

### **Story 2-3: 错误检测机制**（第1周）
**核心组件：**
- `ErrorDetector`主类
- `LocalizationErrorDetector`定位错误检测
- `NavigationErrorDetector`导航错误检测
- `PerceptionErrorDetector`感知错误检测
- `SystemHealthDetector`系统健康监控

**技术特点：**
- 10Hz检测频率
- 四级严重程度分类（Warning/Error/Critical/Fatal）
- 自动映射到恢复级别（L1/L2/L3）
- ROS2参数配置

### **Story 2-1: L1恢复行为**（第2周）
**恢复策略：**
- **RFID重新扫描**：检测失败时重试扫描
- **重新定位**：360度旋转恢复AMCL定位
- **目标重定义**：寻找替代目标位置

**性能目标：**
- 恢复时间≤10秒
- 成功率≥80%（轻微故障）
- 最多重试3次

### **Story 2-2: L2恢复行为**（第3周）
**恢复策略：**
- **代价地图清除**：重置导航障碍物并重新规划
- **任务状态重置**：保存上下文→重置→恢复上下文
- **组件重启**：选择性重启ROS2节点
- **返回Home重置**：返回原点并完全重新初始化

**性能目标：**
- 恢复时间≤40秒
- 100%状态保持
- 失败后升级到L3

### **Story 2-4: 行为树集成**（第4周）
**核心组件：**
- `BTManagerNode`行为树管理器
- XML行为树定义（主树、恢复树、FindBook树）
- 自定义BT节点（错误检测、恢复动作）
- Groot可视化支持

**集成特点：**
- 10Hz执行频率
- 支持热重载更新
- 并行系统健康检查
- 反应式回退策略

---

## 🔌 导航接口调用设计

### **Epic 2会调用的导航接口**

#### **Action接口调用**
```python
# 寻路接口
self.nav_client = ActionClient(self.node, NavigateToPose, '/navigate_to_pose')

# 地图保存接口  
self.map_saver_client = ActionClient(self.node, SaveMap, '/map_saver')
```

#### **Service接口调用**
```python
# 代价地图清除
clear_costmap_client = self.node.create_client(ClearCostmap3D, '/clear_costmap')

# 全局重定位
global_loc_client = self.node.create_client(Relocalize, '/global_localization')
```

#### **Topic订阅监控**
```python
# 激光雷达数据监控
self.node.create_subscription(LaserScan, '/scan', self.lidar_cb, 10)

# 定位状态监控
self.node.create_subscription(PoseWithCovarianceStamped, '/amcl_pose', self.pose_cb, 10)

# 导航状态监控
self.node.create_subscription(Path, '/plan', self.path_cb, 10)
```

### **Epic 2不会实现的雷达功能**
- ❌ 激光雷达驱动配置
- ❌ 基础SLAM/AMCL算法
- ❌ 代价地图生成核心算法
- ❌ 路径规划算法
- ❌ 避障算法核心逻辑

### **Epic 2会实现的雷达相关功能**
- ✅ 激光雷达传感器健康监控
- ✅ 定位质量错误检测
- ✅ 导航异常状态识别
- ✅ 基于雷达状态的恢复决策

---

## 🛠️ 开发前准备工作

### **1. 功能包创建**
```bash
ros2 pkg create libbot_tasks --build-type ament_python
```

### **2. 依赖安装**
```bash
sudo apt install -y ros-humble-behaviortree-cpp
sudo apt install libzmq3-dev cmake build-essential
pip3 install behaviortree-cpp
```

### **3. 包依赖配置**
在`libbot_tasks/package.xml`中添加：
```xml
<depend>behaviortree-cpp-v3</depend>
<depend>libbot_msgs</depend>
<depend>nav2_msgs</depend>
```

### **4. 推荐项目结构**
```
libbot_tasks/
├── libbot_tasks/
│   ├── __init__.py
│   ├── error_detector.py          # Story 2-3
│   ├── detectors/                 # 各类检测器
│   ├── l1_recovery_behaviors.py   # Story 2-1
│   ├── l2_recovery_behaviors.py   # Story 2-2
│   ├── bt_manager_node.py         # Story 2-4
│   ├── bt_nodes/                  # 自定义BT节点
│   ├── behaviors/                 # XML行为树文件
│   └── config/                    # 配置文件
├── launch/
│   └── error_recovery.launch.py
├── package.xml
├── setup.py
└── setup.cfg
```

---

## 📊 资源需求与时间规划

### **工作量分配**
- **总工时**：160小时（4周）
- **第1周**：错误检测机制（40小时）
- **第2周**：L1恢复行为（40小时）
- **第3周**：L2恢复行为（40小时）
- **第4周**：行为树集成（40小时）

### **成功指标**

#### **功能要求**
- ✅ 4类错误100%检测覆盖率
- ✅ L1恢复成功率≥80%
- ✅ L2恢复成功率≥90%
- ✅ 正确的升级链（L1→L2→L3）

#### **性能要求**
- ✅ 检测延迟≤1秒
- ✅ 恢复时间目标达成
- ✅ 误报率<5%
- ✅ 恢复期间系统稳定性保持

---

## 🧪 测试策略

### **单元测试**
- 错误检测器验证（模拟数据）
- 恢复行为测试（控制场景）
- BT节点执行验证

### **集成测试**
- 端到端错误检测→恢复工作流
- ROS2参数配置验证
- 多线程执行安全性

### **系统测试**
- 导航失败恢复场景
- RFID检测失败处理
- 系统资源耗尽恢复
- 并发错误处理

---

## 🔄 开发里程碑

| 时间 | 里程碑 | 交付物 |
|------|--------|--------|
| 第1周结束 | 错误检测框架完成 | ErrorDetector + 4个检测器 |
| 第2周结束 | L1恢复 + 基础BT集成 | L1RecoveryBehaviors + 基础行为树 |
| 第3周结束 | L2恢复 + 完整BT集成 | L2RecoveryBehaviors + 完整行为树 |
| 第4周结束 | 系统测试完成 | 完整的错误处理系统 |

---

## 📝 最佳实践建议

### **开发建议**
1. **从简单开始**：先实现基础错误检测，再逐步增加复杂性
2. **参数化设计**：所有阈值、超时、重试次数都通过ROS2参数配置
3. **详细日志**：记录完整的恢复过程，便于调试
4. **单元测试优先**：每个组件都要有充分的测试覆盖

### **架构优势**
- **决策逻辑清晰**：行为树可视化展示执行路径
- **算法可复用**：同一算法可被不同决策路径调用
- **易于扩展**：添加新错误类型不影响现有架构
- **便于调试**：可单独测试决策逻辑或算法实现

---

## 📚 相关文档

- [design_brainstorm_detailed.md#D2章节](../docs/design_brainstorm_detailed.md) - 错误处理详细设计
- [phase1_implementation_plan.md](../docs/phase1_implementation_plan.md) - 项目整体实施计划
- [src/stories/2-1-l1-recovery.md](../src/stories/2-1-l1-recovery.md) - L1恢复详细需求
- [src/stories/2-2-l2-recovery.md](../src/stories/2-2-l2-recovery.md) - L2恢复详细需求
- [src/stories/2-3-error-detection.md](../src/stories/2-3-error-detection.md) - 错误检测详细需求
- [src/stories/2-4-bt-integration.md](../src/stories/2-4-bt-integration.md) - 行为树集成详细需求

---

**文档版本：** 1.0  
**最后更新：** 2026年4月8日  
**状态：** 已完成规划，准备开始实施