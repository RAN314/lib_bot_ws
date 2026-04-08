# Project Context - 图书馆机器人ROS2项目

## 项目概述
- **项目名称**: 图书馆机器人ROS2仿真系统
- **目标**: 构建一个图书馆机器人的ROS2仿真工作空间，实现自主导航、图书检索和库存管理
- **阶段**: Phase 1 MVP (4周)
- **团队**: 1名开发者

## 技术栈
- **操作系统**: Ubuntu 22.04 LTS
- **ROS版本**: ROS2 Humble Hawksbill
- **仿真平台**: Gazebo Classic 11
- **机器人平台**: TurtleBot3 Waffle Pi
- **编程语言**: Python 3.8+
- **UI框架**: Qt5
- **数据库**: SQLite

## 核心功能 (Epics)
1. 人机交互细节 - Qt5 UI界面设计与实现
2. 错误处理与恢复机制 - 三层恢复机制（L1/L2/L3）
3. 日志与监控系统 - 混合日志方案
4. 配置管理系统 - YAML + ROS2参数混合
5. API设计细节 - Topic/Service/Action接口
6. 仿真真实性增强 - RFID噪声模型 + 动态障碍物
7. 数据同步机制 - Gazebo↔SQLite双向同步
8. 安全机制 - 运动安全、数据保护、操作安全

## 项目约束
- 单机器人场景（不考虑多机器人协作）
- 单层图书馆（不考虑多楼层）
- 服务型机器人（仅导航和指示，不执行图书抓取）
- 仿真环境验证（不考虑Sim2Real迁移）

## 产出物
- 8个ROS2功能包
- 完整的仿真环境（Gazebo）
- Qt5控制面板UI
- 50本测试图书数据集
- SQLite数据库
- 45个测试用例（5 E2E + 10集成 + 30单元）
- 设计文档和实施计划

## 性能目标
- 启动时间: < 15秒
- 运行帧率: > 30 FPS
- 内存占用: < 2GB
- 导航响应: < 2秒
- 找书成功率: > 85%
- 代码覆盖率: > 85%

## 敏捷开发方法
- 框架: Scrum
- Sprint: Phase 1 (4周)
- 冲刺周期: 每周一个小目标
- 故事点: 斐波那契数列（1, 2, 3, 5, 8, 13）
- 每日站会: 15分钟（开发者自我同步）
- 周评审: 每周五下午

## 文档约定
- 设计文档位置: `~/lib_bot_ws/docs/`
- Story文档位置: `~/lib_bot_ws/src/stories/`
- 代码位置: `~/lib_bot_ws/src/`
- 配置文件: `~/lib_bot_ws/library_config/`
- 日志文件: `~/lib_bot_ws/logs/`
- 备份文件: `~/lib_bot_ws/backups/`

## 设计阶段产出
- design_brainstorm_highlevel.md (高层架构)
- design_brainstorm_detailed.md (详细设计，D1-D8章节)
- design_ui.md (UI设计)
- test_cases.md (45个测试用例)
- phase1_implementation_plan.md (4周实施计划)
- features_summary.md (功能索引)

## 关键里程碑
- M1: 基础环境搭建完成（第1周）
- M2: RFID感知系统完成（第2周）
- M3: UI集成完成（第3周）
- M4: Phase 1验收（第4周）
