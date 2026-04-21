# RFID 找书功能快速测试指南

## 🎯 目标
测试原点书籍 (ORIGIN_BOOK_001) 的完整找书流程

## 📋 准备工作

### 已完成的配置
- ✅ 书籍数据库：添加了 "图书馆指南" (ORIGIN_BOOK_001)
- ✅ RFID配置：test_tag_origin → ORIGIN_BOOK_001
- ✅ 位置一致：书籍和RFID标签都在 (0.0, 0.0)
- ✅ 世界模型：存在 rfid_tag_origin 标签

## 🚀 测试步骤

### 步骤 1：启动仿真环境
```bash
# 终端1：启动带RFID的Gazebo仿真
ros2 launch libbot_simulation library_gazebo_rfid.launch.py
```

### 步骤 2：启动RFID传感器
```bash
# 终端2：启动RFID传感器节点
ros2 run libbot_simulation rfid_sensor_node
```

### 步骤 3：启动UI控制面板
```bash
# 终端3：启动UI找书界面
ros2 launch libbot_ui ui_findbook_demo.launch.py
```

### 步骤 4：测试找书功能
1. 在UI界面中，点击 "查找图书" 按钮
2. 在搜索框中输入 "ORIGIN_BOOK_001" 或 "图书馆指南"
3. 选择找到的书籍
4. 点击 "开始找书" 按钮
5. 观察机器人导航到原点 (0.0, 0.0)
6. 查看RFID检测反馈

## 📊 预期结果

### 导航过程
- ✅ 机器人从初始位置移动到原点 (0.0, 0.0)
- ✅ UI显示导航进度和状态
- ✅ 状态栏显示 "导航: navigating" → "导航: scanning" → "导航: completed"

### RFID检测
- ✅ RFID传感器检测到 ORIGIN_BOOK_001 标签
- ✅ 信号强度显示在合理范围内 (0.6-1.0)
- ✅ 检测结果通过ROS2话题发布

### 任务完成
- ✅ UI显示 "✅ 找书任务已完成"
- ✅ 日志面板显示完整的找书过程
- ✅ 机器人停留在目标位置

## 🔍 故障排查

### 问题1：UI中找不到书籍
- 检查书籍数据库路径是否正确
- 确认 `ORIGIN_BOOK_001` 在数据库中存在
- 重启UI应用

### 问题2：机器人不移动
- 检查Nav2导航是否正常运行
- 确认仿真时间设置正确
- 检查是否有导航错误消息

### 问题3：RFID检测不到标签
- 检查RFID传感器节点是否启动
- 确认机器人位置接近 (0.0, 0.0)
- 查看RFID话题是否有数据发布：`ros2 topic echo /rfid/scan/front`

### 问题4：位置不准确
- 检查书籍和RFID标签的位置配置是否一致
- 确认世界模型中标签位置正确
- 调整导航参数（如果需要）

## 📡 ROS2 话题监控

```bash
# 监控RFID检测话题
ros2 topic echo /rfid/scan/front

# 查看机器人位姿
ros2 topic echo /robot_pose

# 查看导航状态
ros2 topic echo /navigate_to_pose/_action/status

# 查看所有RFID相关话题
ros2 topic list | grep rfid
```

## 🎮 高级测试

### 测试不同距离的RFID检测
1. 修改机器人目标位置到 (0.1, 0.1)、(0.2, 0.2) 等
2. 观察RFID信号强度变化
3. 验证距离衰减模型

### 测试多书籍场景
1. 在UI中选择其他书籍 (BK001, BK002等)
2. 验证导航到不同位置
3. 测试书籍切换和连续找书

## 📈 性能验证

### 检测延迟
- RFID检测延迟应 < 100ms
- 导航响应时间应 < 1s

### 定位精度
- 导航到原点的误差应 < 0.1m
- RFID检测距离应 ≤ 0.5m

### 系统稳定性
- 连续多次找书测试应稳定运行
- 无内存泄漏或性能下降

## 🎉 成功标志

当完成以下所有项目时，表示RFID找书功能测试成功：

- ✅ 机器人能准确导航到原点位置
- ✅ RFID传感器能检测到ORIGIN_BOOK_001标签
- ✅ UI显示完整的找书流程和结果
- ✅ 系统稳定运行，无错误消息
- ✅ 用户能通过UI完成完整的找书操作

---

**测试环境**: lib_bot_ws ROS2 Humble
**最后更新**: 2026年4月21日
**状态**: ✅ 配置完成，准备测试
