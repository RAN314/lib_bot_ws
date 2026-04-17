# LibBot健康监控系统

## 📋 概述

LibBot健康监控系统是图书馆机器人ROS2项目的重要组成部分，提供实时系统健康监控、告警和报告功能。

## 🎯 核心功能

- **实时监控**: 10Hz监控频率，实时收集系统健康数据
- **多维度监控**: 导航、感知、系统资源全方位监控
- **智能告警**: 基于阈值的智能告警机制
- **历史记录**: 1小时历史数据存储和分析
- **健康报告**: 详细的健康状态报告生成

## 🏗️ 系统架构

```
┌─────────────────────────────────────────┐
│           HealthMonitor                  │
│         (健康监控管理器)                 │
└─────────────────────────────────────────┘
           │
           ├─────────────────┬─────────────────┬─────────────────┐
           ▼                 ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Navigation      │ │ Perception      │ │ System          │ │ Resource        │
│ Monitor         │ │ Monitor         │ │ Monitor         │ │ Monitor         │
│ - AMCL频率      │ │ - RFID频率      │ │ - 节点状态      │ │ - CPU使用率     │
│ - 规划成功率    │ │ - 检测成功率    │ │ - 话题状态      │ │ - 内存使用      │
└─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────────────┘
           │                 │                 │                 │
           └─────────────────┼─────────────────┼─────────────────┘
                             ▼
                    ┌─────────────────┐
                    │ HealthReporter  │
                    │ (健康报告生成)  │
                    └─────────────────┘
```

## 🚀 快速开始

### 启动健康监控

```bash
# 启动演示节点
ros2 run libbot_monitoring health_monitor_demo
```

### 查看健康状态

```bash
# 查看健康状态话题
ros2 topic echo /system/health

# 获取健康报告
ros2 service call /system/get_health_report libbot_msgs/srv/GetHealthReport "{duration_seconds: 300}"
```

## 📊 监控指标

### 导航监控
- **AMCL频率**: 定位更新频率 (Hz)
- **规划成功率**: 路径规划成功百分比 (%)

### 感知监控
- **RFID频率**: RFID扫描频率 (Hz)
- **检测成功率**: RFID检测成功百分比 (%)

### 资源监控
- **CPU使用率**: 进程CPU占用百分比 (%)
- **内存使用**: 进程内存使用量 (MB)
- **话题延迟**: ROS2话题通信延迟 (ms)

## ⚙️ 配置参数

### 监控频率
```yaml
monitoring.frequency: 10.0  # Hz
```

### 阈值配置
```yaml
monitoring.thresholds:
  navigation:
    amcl_frequency:
      warning: 5.0
      error: 3.0
      critical: 1.0
  perception:
    rfid_frequency:
      warning: 9.0
      error: 7.0
      critical: 5.0
  resource:
    cpu_usage:
      warning: 70.0
      error: 85.0
      critical: 95.0
```

## 📡 ROS2接口

### 话题
- **/system/health** (libbot_msgs/msg/SystemHealth): 系统健康状态

### 服务
- **/system/get_health_report** (libbot_msgs/srv/GetHealthReport): 获取健康报告

## 🔧 开发指南

### 添加新的监控组件

1. 创建新的监控类，继承基础监控接口
2. 实现数据收集和健康度计算
3. 在主监控器中注册新组件
4. 配置相应的阈值参数

### 自定义告警规则

编辑 `config/monitoring_config.yaml` 文件，配置不同指标的告警阈值。

## 🧪 测试

```bash
# 运行单元测试
python3 -m pytest test_health_monitor.py -v

# 运行集成测试
ros2 launch libbot_monitoring health_monitor_test.launch.py
```

## 📈 性能目标

- **监控频率**: 10Hz
- **指标计算延迟**: <50ms
- **CPU占用**: <5%
- **内存占用**: <50MB
- **历史数据存储**: 1小时

## 🔍 故障排除

### 常见问题

1. **监控数据不更新**
   - 检查ROS2节点是否正常启动
   - 验证话题订阅是否正常

2. **告警频繁触发**
   - 调整阈值配置
   - 检查系统负载情况

3. **性能影响过大**
   - 降低监控频率
   - 减少监控组件数量

## 📚 相关文档

- [Story 3-1: 混合日志方案实现](../stories/3-1-hybrid-logging.md)
- [Story 3-3: UI日志面板实现](../stories/3-3-log-panel-ui.md)
- [项目详细设计](../../docs/design_brainstorm_detailed.md#D3章节)

## 🤝 贡献指南

1. Fork项目并创建功能分支
2. 遵循ROS2和Python编码规范
3. 添加相应的测试用例
4. 更新文档和配置示例
5. 提交Pull Request

---

**版本**: 1.0.0  
**最后更新**: 2026年4月14日  
**状态**: 开发完成，等待测试
