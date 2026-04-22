# 图书馆机器人仿真系统启动指南

本文档说明如何启动完整的图书馆机器人仿真系统，包括Gazebo仿真、MoveIt运动规划和Nav2导航功能。

## 系统组件

完整的仿真系统包含以下三个核心组件：

1. **Gazebo仿真环境** - 提供物理仿真和传感器模拟
2. **MoveIt运动规划** - 机械臂运动规划和控制
3. **Nav2导航系统** - 机器人自主导航和路径规划

## 启动文件说明

### 1. MoveIt 运动规划启动文件
**路径**: `/home/lhl/lib_bot_ws/src/turtlebot3_manipulation/turtlebot3_manipulation_moveit_config/launch/move_group.launch.py`

**功能**:
- 启动MoveIt运动规划器
- 配置机械臂运动学求解器
- 设置碰撞检测和避障
- 提供运动规划服务接口

**启动命令**:
```bash
ros2 launch turtlebot3_manipulation_moveit_config move_group.launch.py
```

### 2. Gazebo仿真启动文件
**路径**: `/home/lhl/lib_bot_ws/src/libbot_simulation/launch/library_gazebo_rfid.launch.py`

**功能**:
- 启动Gazebo仿真环境
- 加载图书馆世界模型（带RFID标签）
- 生成机器人URDF模型
- 启动机器人状态发布器
- 配置控制器管理器
- 启动RViz可视化（可选）

**启动命令**:
```bash
ros2 launch libbot_simulation library_gazebo_rfid.launch.py
```

**参数说明**:
- `start_rviz`: 是否启动RViz（默认false）
- `prefix`: 关节和链接名称前缀
- `use_sim`: 是否使用仿真模式（默认true）
- `world`: Gazebo世界文件路径
- `x_pose`, `y_pose`, `z_pose`: 机器人初始位置
- `roll`, `pitch`, `yaw`: 机器人初始姿态

### 3. Nav2导航启动文件
**路径**: `/home/lhl/lib_bot_ws/src/libbot_simulation/launch/library_nav2_use_sim_time.launch.py`

**功能**:
- 启动Nav2导航堆栈
- 配置路径规划和避障
- 设置代价地图和全局规划器
- 启用仿真时间同步

**启动命令**:
```bash
ros2 launch libbot_simulation library_nav2_use_sim_time.launch.py
```

## 启动顺序

建议按以下顺序启动系统组件：

1. **首先启动Gazebo仿真**
   ```bash
   ros2 launch libbot_simulation library_gazebo_rfid.launch.py
   ```

2. **然后启动MoveIt运动规划**
   ```bash
   ros2 launch turtlebot3_manipulation_moveit_config move_group.launch.py
   ```

3. **最后启动Nav2导航系统**
   ```bash
   ros2 launch libbot_simulation library_nav2_use_sim_time.launch.py
   ```

## 验证系统状态

启动完成后，可以使用以下命令验证各组件是否正常运行：

```bash
# 查看活动节点
ros2 node list

# 查看话题列表
ros2 topic list

# 查看服务列表
ros2 service list

# 检查机器人状态
ros2 topic echo /robot_description
```

## 常见问题

### 1. xacro参数解析错误
如果在启动Gazebo时遇到xacro参数解析错误，请检查`library_manipulation_base.launch.py`文件中的参数分隔符是否正确。

### 2. 控制器启动失败
如果控制器启动失败，请确保已正确安装所有依赖包，并检查控制器配置文件路径。

### 3. 仿真时间同步问题
如果遇到时间同步问题，请确保所有节点都使用`use_sim_time`参数，并正确设置为true。

## 依赖包要求

- `turtlebot3_manipulation_gazebo`
- `turtlebot3_manipulation_moveit_config`
- `libbot_simulation`
- `aws_robomaker_bookstore_world`
- `gazebo_ros`
- `navigation2`
- `nav2_bringup`

确保所有依赖包已正确安装并在ROS 2工作空间中构建完成。
