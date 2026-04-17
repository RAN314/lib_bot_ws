# RFID传感器仿真快速参考 🎯

## 🚀 一键启动命令

### 简单RFID仿真演示（推荐）
```bash
# 启动简单RFID仿真环境（推荐）
ros2 launch libbot_simulation simple_rfid_demo.launch.py
```

### 完整RFID仿真演示
```bash
# 启动完整RFID仿真环境
ros2 launch libbot_simulation library_rfid_demo.launch.py
```

### 仅启动RFID传感器
```bash
# 启动RFID传感器节点
ros2 run libbot_simulation rfid_sensor_node

# 启动机器人位姿发布器
ros2 run libbot_simulation robot_pose_publisher

# 启动RFID可视化
ros2 run libbot_simulation rfid_visualizer
```

## 📡 监控命令

### 查看RFID检测数据
```bash
# 查看前方RFID检测
ros2 topic echo /rfid/scan/front

# 查看所有RFID话题
ros2 topic list | grep rfid

# 查看检测统计
ros2 topic echo /rfid_visualization
```

### 机器人控制
```bash
# 键盘控制
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# 查看机器人位姿
ros2 topic echo /robot_pose

# 查看激光雷达
ros2 topic echo /scan
```

## 🔧 配置文件位置

| 文件 | 路径 | 说明 |
|------|------|------|
| RFID配置 | `src/libbot_simulation/config/rfid_config.yaml` | 传感器参数和标签数据库 |
| 机器人配置 | `src/libbot_simulation/config/turtlebot3_config.yaml` | Waffle机器人设置 |
| RVIZ配置 | `src/libbot_simulation/rviz/rfid_demo.rviz` | 可视化界面配置 |

## 📊 关键参数

### RFID传感器参数
- **检测范围**: 0.5米
- **扫描频率**: 10Hz
- **漏检率**: 15%
- **误检率**: 5%
- **检测方向**: 前、后、左、右

### 标签信息
- **世界标签**: 43个（书架标签）
- **图书标签**: 8个（可移动图书）
- **检测高度**: 0.2-0.8米

## 🎯 测试位置

| 位置 | 坐标 | 预期检测 |
|------|------|----------|
| 原点 | (0, 0) | test_tag_origin |
| 靠近book_001 | (2.0, 1.5) | book_001 |
| 靠近book_006 | (1.5, -2.0) | book_006 |
| 靠近world_tag_001 | (1.3, -1.6) | world_tag_001 |

## 🔍 调试命令

### 检查节点状态
```bash
# 查看所有节点
ros2 node list

# 查看节点信息
ros2 node info /rfid_sensor_node

# 查看话题信息
ros2 topic info /rfid/scan/front
```

### 检查服务
```bash
# 查看可用服务
ros2 service list | grep gazebo

# 测试Gazebo服务
ros2 service call /gazebo/get_entity_state gazebo_msgs/srv/GetEntityState "name: 'turtlebot3_waffle_pi'"
```

## 🎨 RVIZ显示说明

| 显示元素 | 颜色 | 说明 |
|----------|------|------|
| 机器人模型 | 蓝色 | Waffle Pi机器人 |
| RFID检测范围 | 浅蓝透明 | 0.5米检测区域 |
| 检测到的标签 | 绿-红渐变 | 信号强度指示 |
| 标签文本 | 白色 | 标签ID和强度 |

## 🚨 故障排除

### 问题：无RFID检测输出
**解决方案**：
1. 检查RFID传感器节点是否运行：`ros2 node list | grep rfid`
2. 检查机器人位姿发布：`ros2 topic echo /robot_pose`
3. 验证Gazebo服务：`ros2 service list | grep gazebo`

### 问题：检测率低
**解决方案**：
1. 移动到标签附近（<0.5米）
2. 检查标签高度（0.2-0.8米）
3. 调整配置文件中的检测参数

### 问题：RVIZ无RFID可视化
**解决方案**：
1. 确认rfid_visualizer节点运行
2. 检查MarkerArray话题：`ros2 topic echo /rfid_visualization`
3. 重新加载RVIZ配置

## 📈 性能指标

- **最新检测率**: 15.6%
- **成功检测标签**: 3个
- **误检数量**: 符合5%设计目标
- **系统响应时间**: <100ms

## 🎓 使用场景

1. **定点检测**：机器人停在标签附近进行RFID扫描
2. **移动检测**：机器人移动过程中持续RFID检测
3. **路径规划**：基于RFID检测结果的导航决策
4. **错误恢复**：利用RFID标签进行位置校正

---

**提示**：RFID传感器已成功集成，可以在完整的Gazebo仿真环境中进行各种RFID检测实验！