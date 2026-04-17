# libbot_simulation - 图书馆机器人仿真包

基于Amazon RoboMaker书店世界和TurtleBot3 Waffle Pi的图书馆机器人仿真环境。

## 🏗️ 架构设计

- **基础场景**: Amazon RoboMaker书店世界 (aws-robomaker-bookstore-world)
- **机器人平台**: TurtleBot3 Waffle Pi
- **传感器**: LiDAR + 摄像头 + RFID (待实现)
- **仿真引擎**: Gazebo Classic 11

## 📁 文件结构

```
libbot_simulation/
├── launch/
│   ├── library_simulation.launch.py          # 基础图书馆场景
│   ├── library_with_turtlebot3.launch.py    # 完整仿真(含机器人)
│   └── library_headless.launch.py           # 无GUI模式(推荐)
├── config/
│   ├── turtlebot3_config.yaml               # TurtleBot3配置
│   └── gazebo_config.yaml                   # Gazebo参数
├── worlds/                                  # 符号链接到bookstore.world
└── models/                                  # 自定义模型目录
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
sudo apt install ros-humble-turtlebot3*
sudo apt install ros-humble-aws-robomaker-bookstore-world

# 设置TurtleBot3模型
export TURTLEBOT3_MODEL=waffle_pi
```

### 2. 编译包

```bash
cd ~/lib_bot_ws
colcon build --packages-select libbot_simulation
turtlebot3_gazebo turtlebot3_description
source install/setup.bash
```

### 3. 启动仿真

**选项1: 无GUI模式 (推荐)**
```bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch libbot_simulation library_headless.launch.py
```

**选项2: 完整仿真 (含GUI)**
```bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch libbot_simulation library_with_turtlebot3.launch.py
```

**选项3: 仅图书馆环境**
```bash
ros2 launch libbot_simulation library_simulation.launch.py
```

**选项4: 自定义机器人位置**
```bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch libbot_simulation library_with_turtlebot3.launch.py x_pose:=2.0 y_pose:=1.0
```

## 🎮 控制机器人

### 键盘控制
```bash
# 新终端中运行
ros2 run turtlebot3_teleop teleop_keyboard
```

### 查看传感器数据
```bash
# LiDAR数据
ros2 topic echo /scan

# 摄像头数据
ros2 topic echo /camera/image

# 机器人状态
ros2 topic echo /odom

# TF变换
ros2 run tf2_tools view_frames
```

## 🔧 常用调试命令

```bash
# 查看所有话题
ros2 topic list

# 查看所有节点
ros2 node list

# 查看话题频率
ros2 topic hz /scan

# 查看话题信息
ros2 topic info /odom
```

## 📊 验证功能

### 1. Gazebo仿真
- ✅ 书店场景正常加载
- ✅ TurtleBot3 Waffle Pi机器人出现
- ✅ 机器人传感器正常工作

### 2. ROS2话题
- ✅ `/scan` (LiDAR数据)
- ✅ `/odom` (里程计数据)
- ✅ `/camera/image` (摄像头数据)
- ✅ `/tf` (坐标变换)
- ✅ `/cmd_vel` (速度控制)

### 3. RViz可视化
```bash
ros2 run rviz2 rviz2
```
- 添加LaserScan显示/scan话题
- 添加RobotModel显示机器人
- 添加Image显示/camera/image话题

## 🐛 故障排除

### 问题1: TurtleBot3模型未找到
```bash
# 检查环境变量
echo $TURTLEBOT3_MODEL

# 重新设置
export TURTLEBOT3_MODEL=waffle_pi
```

### 问题2: 依赖包缺失
```bash
# 检查TurtleBot3包
dpkg -l | grep turtlebot3

# 重新安装
sudo apt install ros-humble-turtlebot3-gazebo ros-humble-turtlebot3-description
```

### 问题3: Gazebo启动慢或崩溃
```bash
# 使用无GUI模式
ros2 launch libbot_simulation library_headless.launch.py

# 检查系统资源
free -h
top
```

### 问题4: 机器人不出现
```bash
# 检查Gazebo是否正常运行
ros2 topic echo /clock

# 检查机器人生成状态
ros2 node list | grep spawn

# 检查URDF文件
ls $(ros2 pkg prefix turtlebot3_description)/share/turtlebot3_description/urdf/
```

## 📈 性能优化建议

1. **使用无GUI模式**: 提高仿真性能
2. **降低物理更新率**: 在配置中调整`real_time_update_rate`
3. **简化传感器噪声**: 调试时可暂时禁用噪声模型
4. **使用ROS2 DDS优化**: 配置合适的DDS实现

## 🔄 与BMAD开发计划集成

本仿真环境支持BMAD项目的以下功能开发:

- **Story 6-1**: RFID噪声模型实现
- **Story 6-2**: 动态障碍物模拟
- **Story 6-3**: Gazebo Actor配置
- **导航系统开发**: 基于TurtleBot3的SLAM和路径规划
- **传感器融合**: LiDAR + RFID + 视觉

## 📚 相关文档

- [BMAD开发计划](../../../CORE_DEVELOPMENT_PLAN.md)
- [RFID噪声模型](../../stories/6-1-rfid-noise-model.md)
- [TurtleBot3文档](https://emanual.robotis.com/docs/en/platform/turtlebot3/)
- [Amazon RoboMaker书店世界](../../aws-robomaker-bookstore-world/README.md)

## 🎯 下一步开发计划

1. **RFID传感器插件**: 实现Story 6-1的噪声模型
2. **动态障碍物**: 添加移动的人和物体
3. **导航集成**: 集成SLAM和Navigation2
4. **任务执行**: 实现图书查找任务

---

**注意**: 本包专注于图书馆机器人仿真，基于成熟的TurtleBot3平台和Amazon书店世界，确保仿真的真实性和可靠性。