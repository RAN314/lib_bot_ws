# 🎯 图书馆机器人ROS2项目 - 功能清单总结

> **项目阶段**: 头脑风暴与设计完成
> **适用范围**: Phase 1 MVP（4周）
> **最后更新**: 2026-4-7
> **状态**: 准备开始编码

---

## 📋 功能总览（8大核心功能）

| # | 功能名称 | 优先级 | 状态 | 文档位置 |
|---|---------|--------|------|---------|
| 1 | 人机交互细节 | P0 | ✅ 完成 | design_brainstorm_detailed.md / D1 |
| 2 | 错误处理与恢复机制 | P0 | ✅ 完成 | design_brainstorm_detailed.md / D2 |
| 3 | 日志与监控系统 | P0 | ✅ 完成 | design_brainstorm_detailed.md / D3 |
| 4 | 配置管理系统 | P0 | ✅ 完成 | design_brainstorm_detailed.md / D4 |
| 5 | API设计细节 | P0 | ✅ 完成 | design_brainstorm_detailed.md / D5 |
| 6 | 仿真真实性增强 | P0 | ✅ 完成 | design_brainstorm_detailed.md / D6 |
| 7 | 数据同步机制 | P0 | ✅ 完成 | design_brainstorm_detailed.md / D7 |
| 8 | 安全机制 | P0 | ✅ 完成 | design_brainstorm_detailed.md / D8 |

---

## 📖 文档清单

### 设计文档
| 文档名称 | 状态 | 用途 |
|---------|------|------|
| design_brainstorm_highlevel.md | ✅ 完成 | 高层架构、技术决策、演进路线 |
| **design_brainstorm_detailed.md** | ✅ 完成 | 8大功能详细设计（核心文档） |
| **design_ui.md** | ✅ 完成 | UI界面规范、交互细节、快捷键 |
| **test_cases.md** | ✅ 完成 | 测试用例清单（5 E2E + 10集成 + 30单元） |
| phase1_implementation_plan.md | ✅ 完成 | 4周实施计划、任务分解 |
| **features_summary.md** | ✅ **本文档** | 功能索引、快速查找 |

**加粗文档**为日常开发高频使用文档

---

## 🛠️ Phase 1 实施准备清单

### 代码准备
```bash
[ ] 创建工作空间目录结构
[ ] 初始化Git仓库
[ ] 创建8个ROS2包（libbot_description, libbot_simulation, libbot_navigation, libbot_perception, libbot_database, libbot_msgs, libbot_tasks, libbot_ui）
[ ] 配置.package.xml和setup.py
[ ] 创建launch目录结构
```

### 配置准备
```bash
[ ] 创建library_config/目录
[ ] 复制配置文件（config_dev.yaml, config_test.yaml, config_demo.yaml）
[ ] 生成50本测试图书数据（books.csv + library.db）
[ ] 创建bookshelf_templates.yaml
[ ] 验证配置文件路径和权限
```

### 依赖安装
```bash
[ ] 安装ROS2 Humble完整版
[ ] 安装TurtleBot3包
[ ] 安装Nav2包
[ ] 安装Gazebo Classic 11
[ ] 安装Python依赖（pyqt5, sqlite3）
[ ] 验证安装：ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

### 测试准备
```bash
[ ] 准备测试脚本目录
[ ] 编写单元测试框架（pytest）
[ ] 配置CI/CD（可选）
[ ] 准备性能监控工具（rqt, ros2 topic hz）
```

---

## 📚 详细功能索引

### 功能1: 人机交互细节
**文档**: design_brainstorm_detailed.md / D1章节
**核心内容**:
- UI响应时间要求（≤50ms按钮反馈）
- 线程模型（主线程 + ROS2线程 + 回调线程）
- Ros2Manager类设计（Signal/Slot机制）
- 四级错误显示策略（Modal对话框 → 日志）
- UI状态机（IDLE → QUERYING_DB → NAVIGATING → SCANNING → COMPLETED）
- UI可测试性设计（objectName、测试模式、状态快照）

**涉及的文件**:
- `src/libbot_ui/libbot_ui/ros2_manager.py`（需创建）
- `src/libbot_ui/libbot_ui/main_window.py`（需创建）
- `src/libbot_ui/config/qt_stylesheet.yaml`（可选）

**关键决策**:
- Qt5框架，独立窗口应用
- 10Hz刷新频率
- 100条日志缓冲区
- 三级确认机制（普通→重要→危险）

---

### 功能2: 错误处理与恢复机制
**文档**: design_brainstorm_detailed.md / D2章节
**核心内容**:
- 错误分类体系（感知/导航/系统三层）
- 严重程度分级（Fatal → Critical → Error → Warning）
- 三层恢复机制（L1快速恢复→L2状态重置→L3系统重置）
- 具体恢复行为（重新扫描、重新定位、目标重定义、返回Home）
- 错误检测机制（定位误差、规划失败、机器人卡住）
- 与Behavior Tree集成（RecoveryNode模式）

**涉及的文件**:
- `src/libbot_tasks/libbot_tasks/recovery_behaviors.py`（需创建）
- `src/libbot_tasks/behaviors/recovery_node.xml`（需创建）
- `src/libbot_tasks/config/recovery_params.yaml`（需创建）

**关键决策**:
- L1恢复: 5-10秒，任务内部处理
- L2恢复: 30-40秒，任务层面重置
- L3恢复: 60-120秒，系统层面重置
- 漏检率15%，触发重新扫描

---

### 功能3: 日志与监控系统
**文档**: design_brainstorm_detailed.md / D3章节
**核心内容**:
- 混合日志方案（ROS2日志 + SQLite业务日志）
- 日志分类（系统日志vs业务日志）
- 运行监控指标（导航健康度、感知健康度、系统资源）
- UI日志面板设计（100条缓冲区，颜色编码）
- 日志存储与轮转（ROS2日志7天，业务日志30天）

**涉及的文件**:
- `src/libbot_database/libbot_database/log_manager.py`（需创建）
- `src/libbot_perception/libbot_perception/metrics_publisher.py`（可选）
- `library_config/logging.yaml`（需创建）

**关键决策**:
- Topic: /system/health（1Hz发布）
- 日志级别: INFO/WARN/ERROR三级
- 性能监控: 嵌入式检查（Phase 1不实现独立监控节点）

---

### 功能4: 配置管理系统
**文档**: design_brainstorm_detailed.md / D4章节
**核心内容**:
- 配置策略（YAML文件 + ROS2参数混合）
- library_config.yaml结构（7大模块）
- 三环境配置（dev/test/demo）
- 动态参数更新流程（UI调用→ros2 param set→验证→确认）
- 参数验证机制（范围、类型、枚举值）

**涉及的文件**:
- `library_config/library_config.yaml`（需创建主配置）
- `library_config/config_dev.yaml`（需创建）
- `library_config/config_test.yaml`（需创建）
- `library_config/config_demo.yaml`（需创建）
- `src/libbot_tasks/libbot_tasks/param_validator.py`（需创建）

**关键决策**:
- 动态参数8个（速度、阈值、超时等）
- 静态参数集中管理（library_config.yaml）
- 启动时验证，失败则中止
- Git版本控制配置文件

---

### 功能5: API设计细节
**文档**: design_brainstorm_detailed.md / D5章节
**核心内容**:
- API设计四原则（命名、错误码、超时、兼容性）
- Topic接口（/rfid/scan/{front,back,left,right}, /books/locations, /system/health）
- Service接口（/get_book_info, /update_book_location, /check_robot_status）
- Action接口（/find_book, /perform_inventory）
- 接口版本管理（v1.0.0，libbot_msgs包）

**涉及的文件**:
- `src/libbot_msgs/action/FindBook.action`（需创建）
- `src/libbot_msgs/msg/RFIDScan.msg`（需创建）
- `src/libbot_msgs/msg/SystemHealth.msg`（需创建）
- `src/libbot_msgs/srv/GetBookInfo.srv`（需创建）
- `src/libbot_database/libbot_metrics/api_monitor.py`（可选）

**关键决策**:
- Topic QoS: RELIABLE + VOLATILE
- Service超时: 5秒
- Action超时: 5分钟（可配置）
- 错误码: 0=成功，1+=具体错误类型

---

### 功能6: 仿真真实性增强
**文档**: design_brainstorm_detailed.md / D6章节
**核心内容**:
- RFID噪声模型（距离-概率曲线 + 漏检率15%）
- 检测概率函数（calculate_detection_probability）
- 四向扫描实现（4个独立RFID读取器）
- 动态障碍物（1名移动阅读者 + 1名静止读者 + 2个移动椅子）
- Gazebo Actor配置（waypoints, avoid_robot, idle_time）
- 错架/缺失模拟（5-10%错架率，2-3%缺失率）
- 代价地图社交层（阅读区增加代价）

**涉及的文件**:
- `src/libbot_perception/libbot_perception/rfid_simulator.py`（需创建）
- `src/libbot_simulation/worlds/library_basic.sdf`（需创建）
- `src/libbot_simulation/models/bookshelf/model.sdf`（需创建）
- `src/libbot_navigation/config/social_layer.yaml`（需创建）
- `library_config/rfid_noise_params.yaml`（需创建）

**关键决策**:
- 检测范围: 0.5米
- 漏检率: 15%可调
- 障碍物上限: 4个（性能考虑）
- 阅读者周期: 90-180秒
- 椅子移动: 每10秒30%概率

---

### 功能7: 数据同步机制（高层）
**文档**: design_brainstorm_detailed.md / D7章节
**核心内容**:
- 同步场景（Gazebo↔SQLite双向、SQLite→节点通知）
- 同步策略对比（定时轮询 vs 事件驱动 vs 混合）
- 架构设计（同步协调器 + 数据库监控 + Gazebo监控）
- 数据库变更通知（/books/changed Topic）
- 批量写入队列（避免锁竞争）
- 冲突处理（数据库优先）

**涉及的文件**:
- `src/libbot_database/libbot_database/sync_coordinator.py`（需创建）
- `src/libbot_database/libbot_database/db_change_publisher.py`（需创建）
- `scripts/sync_gazebo_to_db.py`（需创建）
- `scripts/sync_db_to_gazebo.py`（需创建）

**关键决策**:
- 权威数据源: SQLite数据库
- 冲突解决: 数据库为准（Gazebo数据可能临时变更）
- Phase 1简化: 启动时同步 + 手动触发脚本
- 并发写入: 连接池 + 批量队列

---

### 功能8: 安全机制（高层）
**文档**: design_brainstorm_detailed.md / D8章节
**核心内容**:
- 运动安全（三层速度限制、边界限制、异常行为检测）
- 数据完整性（数据库备份、配置文件保护、日志轮转）
- 系统健康监控（节点状态、资源使用、心跳检测）
- 操作安全（三级确认机制、审计日志、安全事件日志）
- 事后分析（安全事件分类、诊断工具）

**涉及的文件**:
- `src/libbot_navigation/libbot_navigation/safety_monitor.py`（需创建）
- `src/libbot_tasks/libbot_tasks/operation_auditor.py`（需创建）
- `config/safety_limits.yaml`（需创建）
- `logs/security_events.log`（自动生成）
- `logs/audit.log`（自动生成）

**关键决策**:
- 最大速度: 0.3 m/s（配置上限）
- 边界预警: 0.5米软边界
- 自动恢复: L1/L2/L3三级安全恢复
- 确认对话框: Level 2单次确认，Level 3二次确认
- 审计日志: 记录所有关键操作（who/when/what）

---

## 🎬 Phase 1 实施顺序建议

### 第1周优先级（搭建基础）
```
Day 1-2（高优先级）:
  [ ] 创建工作空间和所有ROS2包结构
  [ ] 配置package.xml和setup.py
  [ ] 安装依赖并验证
  [ ] 编译空工作空间（colcon build）

Day 3-4（高优先级）:
  [ ] 搭建基础Gazebo环境（空房间 + TurtleBot3）
  [ ] 配置基础Nav2（机器人可导航到目标点）
  [ ] 创建并测试基础启动文件

Day 5（中优先级）:
  [ ] 生成50本测试图书数据
  [ ] 创建SQLite数据库
  [ ] 测试数据库查询和更新
```

### 第2周优先级（核心功能）
```
Day 6-7（高优先级）:
  [ ] 实现四向RFID扫描器（4个Topic发布）
  [ ] 图书馆环境建模（24个书架）
  [ ] 测试RFID检测范围和概率

Day 8-9（高优先级）:
  [ ] 定义自定义消息（RFIDScan, FindBook Action）
  [ ] 实现FindBook Action服务器
  [ ] 集成导航 + RFID扫描

Day 10（中优先级）:
  [ ] FindBook端到端测试（5次测试）
  [ ] 调试导航参数
  [ ] 记录测试结果
```

### 第3周优先级（完善功能）
```
Day 11-12（高优先级）:
  [ ] UI主窗口实现（左右面板布局）
  [ ] Ros2Manager封装（与ROS2通信）
  [ ] 实现找书按钮和对话框

Day 13-14（高优先级）:
  [ ] UI状态显示（当前任务、进度、图书信息）
  [ ] 日志面板实现（实时显示）
  [ ] 集成测试（UI → ROS2 → Robot）

Day 15（中优先级）:
  [ ] 实现任务取消功能
  [ ] 实现暂停/继续功能
  [ ] E2E测试（完整找书流程）
```

### 第4周优先级（优化和验收）
```
Day 16-17（高优先级）:
  [ ] 启动时间优化（<15秒）
  [ ] 导航参数调优（成功率>95%）
  [ ] 性能测试（帧率>30 FPS）

Day 18-19（中优先级）:
  [ ] 完善文档（API文档、调优指南）
  [ ] 生成完整测试数据集（books_50.csv）
  [ ] 编写快速开始指南（README.md）

Day 20（高优先级）:
  [ ] Phase 1验收测试（TC_E2E_01到TC_E2E_05）
  [ ] 修复发现的bug
  [ ] 生成验收报告
```

---

## 📊 工作量估算

### 代码文件统计（预计）
```
ROS2包:          8个
Python文件:      ~40-50个
Launch文件:      ~10个
配置文件:        ~15个
消息定义:        ~8个
测试文件:        ~20个

总计:            ~100个文件
```

### 代码行数估算
```
核心逻辑:        ~3000行
消息定义:        ~500行
配置文件:        ~1000行
测试代码:        ~1500行
文档/注释:       ~2000行

总计:            ~8000行
```

### 开发时间估算
```
设计阶段（已完成）:     40小时
实现阶段（预计）:       80小时
测试阶段（预计）:       40小时
文档完善（预计）:       20小时

总计:                  180小时（4周）
```

---

## 🎯 关键里程碑

| 里程碑 | 交付物 | 验收标准 |
|-------|--------|---------|
| **M1: 基础环境搭建**（第1周结束） | Gazebo环境 + Nav2导航 + 50本测试数据 | 机器人可导航到任意位置，无碰撞 |
| **M2: RFID感知系统**（第2周结束） | 四向RFID扫描 + SQLite集成 + FindBook Action | FindBook端到端成功率>80% |
| **M3: UI集成完成**（第3周结束） | UI主窗口 + 完整找书流程 | UI可通过按钮触发完整找书流程 |
| **M4: Phase 1验收**（第4周结束） | 所有文档 + 测试报告 + 优化参数 | 5个E2E测试全部通过 |

---

## 🚨 风险与缓解措施

| 风险 | 概率 | 影响 | 缓解措施 |
|-----|------|------|---------|
| **Nav2在重复环境中定位失败** | 中 | 高 | 增加AMCL粒子数（3k→8k），备用恢复行为 |
| **Gazebo性能不达标（<30 FPS）** | 低 | 高 | 减少模型复杂度，禁用图书碰撞 |
| **Task调度逻辑复杂度过高** | 中 | 中 | 简化Phase 1，仅支持FIFO队列 |
| **RFID仿真精度不足** | 中 | 中 | 预留2天调参时间，增加测试覆盖 |
| **UI与ROS2通信延迟高** | 低 | 中 | 使用10Hz刷新 + Signal/Slot机制 |

---

## ✅ 开始编码前检查清单

### 环境准备
```bash
[ ] Ubuntu 22.04 LTS 已安装
[ ] ROS2 Humble Hawksbill 已安装
[ ] Gazebo Classic 11 已安装
[ ] Git 已配置
[ ] Python 3.8+ 已安装
[ ] VS Code / IDE 已配置ROS2插件
```

### 知识准备
```bash
[ ] 熟悉ROS2基础（节点、话题、服务、动作）
[ ] 熟悉Nav2基本操作
[ ] 熟悉Gazebo仿真
[ ] 熟悉Python编程
[ ] 熟悉SQLite数据库
[ ] 阅读完所有设计文档
```

### 工具准备
```bash
[ ] 准备好rqt、rviz2等调试工具
[ ] 配置好ros2 topic echo/ros2 service call
[ ] 安装htop/top用于性能监控
[ ] 准备ros2 bag用于记录（可选）
```

### 项目准备
```bash
[ ] Fork/Clone项目到本地
[ ] 创建功能分支（feature/xxx）
[ ] 配置好.gitignore（build/, install/, log/, *.db）
[ ] 准备好提交规范（Conventional Commits）
```

---

## 📝 下一阶段工作建议

### 立即开始（第1天）
1. **搭建基础环境**
   ```bash
   mkdir -p ~/lib_bot_ws/src
   cd ~/lib_bot_ws
   git init
   ros2 pkg create libbot_description --build-type ament_python
   # 创建其他7个包...
   ```

2. **配置开发环境**
   ```bash
   # 在VS Code中配置ROS2工作空间
   # 安装必要的VS Code插件
   # 配置launch.json用于调试
   ```

3. **创建基础Gazebo环境**
   ```bash
   # 启动空Gazebo
   ros2 launch gazebo_ros gazebo.launch.py
   # 加载TurtleBot3
   ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
   ```

### 本周目标（第1周）
- ✅ 工作空间可编译
- ✅ 机器人可在空环境中导航
- ✅ 50本测试数据生成完成
- ✅ SQLite数据库可查询

---

## 🎯 提示与建议

### 开发建议
```yaml
1. 从小步开始:
   - 先实现最基础的功能（机器人能走）
   - 再添加功能（RFID扫描）
   - 最后集成（完整流程）

2. 频繁测试:
   - 每完成一个子功能就测试
   - 不要等到最后再测试
   - 使用测试用例指导开发

3. 文档同步:
   - 代码和文档同步更新
   - 发现设计问题时及时更新文档
   - 每周总结进展，更新计划

4. 性能优先:
   - 每阶段关注性能指标
   - 启动时间 < 15秒
   - 运行帧率 > 30 FPS
   - 内存占用 < 2GB

5. 版本控制:
   - 频繁提交（每完成一个小功能）
   - 清晰的commit message
   - 使用分支开发，PR合并
```

### 常见问题解决
```yaml
问题: Gazebo启动失败
解决:
  - 检查显卡驱动（glxinfo）
  - 杀死僵尸gazebo进程
  - 删除~/.gazebo/pid文件

问题: Nav2规划失败
解决:
  - 检查地图是否正确加载
  - 检查初始位置是否设置
  - 调整inflation_radius参数

问题: RFID检测不到
解决:
  - 检查Topic是否发布
  - 检查检测范围参数
  - 调整false_negative_rate

问题: UI连接不上
解决:
  - 检查Ros2Manager初始化
  - 检查节点名称是否正确
  - 检查QoS配置
```

---

## 🎉 设计阶段完成

**恭喜！设计阶段已全部完成。**

我们已经完成了:
- ✅ 8大核心功能的详细设计
- ✅ UI界面规范
- ✅ 测试用例清单（45个测试）
- ✅ Phase 1实施计划（4周）
- ✅ 代码结构规划（100个文件预估）
- ✅ 风险评估与缓解
- ✅ 开发环境准备清单

**下一步: 开始编码实现！**

---

## 📞 支持与反馈

### 开发过程中遇到问题时:
1. 查阅相关功能文档（design_brainstorm_detailed.md）
2. 查看测试用例（test_cases.md）
3. 运行诊断工具（diagnose.sh）
4. 检查日志文件（logs/）

### 需要调整设计时:
1. 更新相关文档
2. 记录变更原因
3. 同步更新所有相关部分
4. 更新features_summary.md

### 准备提交代码时:
1. 确保测试通过（单元测试 + 集成测试）
2. 更新文档（如果接口变更）
3. 运行性能测试（启动时间、帧率）
4. 提交PR并关联相关Issue

---

**准备开始编码！按照Phase 1实施计划，从第1周开始逐步推进。**

**祝开发顺利！** 🚀
