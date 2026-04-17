# Groot可视化使用指南

## 📋 概述

本指南介绍如何使用Groot可视化工具监控和调试图书馆机器人系统的Behavior Tree执行过程。

## 🔧 环境准备

### 1. 安装Groot

```bash
# 安装Groot可视化工具
sudo apt update
sudo apt install groot

# 验证安装
groot --version
```

### 2. 确保ZeroMQ支持

```bash
# 安装Python ZeroMQ支持
pip3 install pyzmq

# 验证ZeroMQ可用
python3 -c "import zmq; print('ZeroMQ版本:', zmq.zmq_version())"
```

## 🚀 启动配置

### 1. 配置BT管理器

编辑配置文件以启用Groot支持：

```yaml
# ~/lib_bot_ws/src/libbot_tasks/libbot_tasks/config/bt_config.yaml
groot:
  enable: true                     # 启用Groot支持
  port: 1666                       # Groot通信端口
  update_frequency: 2.0            # 更新频率(Hz)
  publish_execution_flow: true     # 发布执行流程
  publish_tree_structure: true     # 发布树结构
  publish_node_states: true        # 发布节点状态
```

### 2. 启动BT管理器（启用Groot）

```bash
# 方法1：使用默认配置启动
ros2 run libbot_tasks bt_manager_node

# 方法2：指定配置文件
ros2 run libbot_tasks bt_manager_node --ros-args \
  --params-file ~/lib_bot_ws/src/libbot_tasks/libbot_tasks/config/bt_config.yaml

# 方法3：动态设置Groot参数
ros2 run libbot_tasks bt_manager_node --ros-args \
  -p groot.enable:=true \
  -p groot.port:=1666 \
  -p groot.update_frequency:=2.0
```

### 3. 验证Groot连接

```bash
# 查看BT管理器日志，确认Groot已启用
ros2 run libbot_tasks bt_manager_node --ros-args --log-level info

# 期望看到类似日志：
# [INFO] [bt_manager_node]: Groot可视化支持已启用，端口: 1666
# [INFO] [bt_manager_node]: Groot ZMQ发布器已启动，端口: 1666
```

## 🖥️ Groot使用步骤

### 步骤1：启动Groot

```bash
# 启动Groot可视化工具
groot
```

### 步骤2：配置Groot连接

1. **打开Groot后，点击 "Connect" 按钮**
2. **选择连接类型**: 选择 "ZMQ Subscriber"
3. **配置连接参数**:
   - Host: `localhost`
   - Port: `1666` (与BT管理器配置一致)
   - Protocol: `tcp`
4. **点击 "Connect"**

### 步骤3：加载行为树定义

1. **点击 "Load Tree" 按钮**
2. **选择行为树XML文件**:
   - `~/lib_bot_ws/src/libbot_tasks/libbot_tasks/behaviors/main_bt.xml`
   - `~/lib_bot_ws/src/libbot_tasks/libbot_tasks/behaviors/recovery_bt.xml`
   - `~/lib_bot_ws/src/libbot_tasks/libbot_tasks/behaviors/findbook_bt.xml`
3. **点击 "Load"**

### 步骤4：监控执行过程

1. **在Groot界面中，您将看到**:
   - 行为树结构图
   - 当前执行节点高亮显示
   - 节点状态（SUCCESS/FAILURE/RUNNING）
   - 执行流程动画

2. **实时监控功能**:
   - ✅ 节点执行状态变化
   - ✅ 执行路径可视化
   - ✅ 错误和恢复策略展示
   - ✅ 执行时间统计

## 📊 监控场景示例

### 场景1：图书查找任务监控

```bash
# 1. 启动BT管理器和Groot
ros2 run libbot_tasks bt_manager_node

# 2. 加载FindBook行为树
ros2 service call /bt/load_tree libbot_msgs/srv/LoadBehaviorTree "{
  tree_file: 'behaviors/findbook_bt.xml'
}"

# 3. 在Groot中观察:
#    - NavigateToBookshelf节点执行
#    - ScanForBook节点执行
#    - 错误处理流程（如果发生错误）
```

### 场景2：错误恢复监控

```bash
# 1. 启动BT管理器和Groot
ros2 run libbot_tasks bt_manager_node

# 2. 加载恢复行为树
ros2 service call /bt/load_tree libbot_msgs/srv/LoadBehaviorTree "{
  tree_file: 'behaviors/recovery_bt.xml'
}"

# 3. 在Groot中观察:
#    - 错误检测节点触发
#    - L1恢复策略执行
#    - L2恢复策略执行（如果L1失败）
#    - 恢复结果验证
```

### 场景3：系统健康监控

```bash
# 1. 启动BT管理器和Groot
ros2 run libbot_tasks bt_manager_node

# 2. 加载主行为树
ros2 service call /bt/load_tree libbot_msgs/srv/LoadBehaviorTree "{
  tree_file: 'behaviors/main_bt.xml'
}"

# 3. 在Groot中观察:
#    - 系统监控节点执行
#    - 并行健康检查
#    - 错误处理流程
```

## 🔍 调试技巧

### 1. 节点执行分析

- **绿色节点**: 执行成功
- **红色节点**: 执行失败
- **黄色节点**: 正在执行
- **灰色节点**: 未执行

### 2. 执行路径跟踪

```bash
# 在Groot中:
# 1. 启用 "Show Execution Flow"
# 2. 观察执行路径动画
# 3. 记录关键节点执行时间
# 4. 分析性能瓶颈
```

### 3. 错误诊断

```bash
# 当节点执行失败时:
# 1. 查看Groot中的错误高亮
# 2. 检查ROS2日志获取详细信息
# 3. 分析失败原因
# 4. 调整行为树逻辑
```

## ⚙️ 高级配置

### 1. 自定义端口

```bash
# 修改配置文件中的端口
ros2 run libbot_tasks bt_manager_node --ros-args \
  -p groot.port:=1777

# 在Groot中使用对应端口连接
```

### 2. 调整更新频率

```bash
# 提高更新频率以获得更流畅的动画
ros2 run libbot_tasks bt_manager_node --ros-args \
  -p groot.update_frequency:=5.0

# 降低更新频率以减少网络负载
ros2 run libbot_tasks bt_manager_node --ros-args \
  -p groot.update_frequency:=1.0
```

### 3. 选择性发布

```yaml
# 只发布关键信息以提高性能
groot:
  enable: true
  publish_execution_flow: true
  publish_tree_structure: false    # 禁用结构发布
  publish_node_states: true
```

## 🛠️ 故障排除

### 问题1：Groot无法连接

```bash
# 检查端口是否被占用
lsof -i :1666

# 检查防火墙设置
sudo ufw status

# 尝试使用不同端口
ros2 run libbot_tasks bt_manager_node --ros-args -p groot.port:=1777
```

### 问题2：无数据显示

```bash
# 检查BT管理器日志
ros2 run libbot_tasks bt_manager_node --ros-args --log-level debug

# 验证ZeroMQ连接
python3 -c "import zmq; print('ZeroMQ可用')"

# 重启Groot并重新连接
```

### 问题3：性能问题

```bash
# 降低更新频率
ros2 param set /bt_manager_node groot.update_frequency 1.0

# 禁用不必要的数据发布
ros2 param set /bt_manager_node groot.publish_tree_structure false
```

## 📈 性能优化建议

### 1. 网络优化

- 使用本地连接（localhost）
- 调整更新频率平衡实时性和性能
- 选择性发布数据

### 2. 可视化优化

- 只监控关键行为树
- 使用适当的缩放级别
- 禁用不必要的动画效果

### 3. 调试优化

- 使用日志级别过滤
- 设置断点进行逐步调试
- 记录执行历史用于分析

## 📚 参考资源

- [BehaviorTree.CPP官方文档](https://www.behaviortree.dev/)
- [Groot用户手册](https://github.com/BehaviorTree/Groot)
- [ZeroMQ指南](http://zguide.zeromq.org/)
- [ROS2与BT集成示例](https://github.com/BehaviorTree/BehaviorTree.ROS2)

---

**提示**: Groot是强大的调试工具，建议在实际开发和测试中充分利用其可视化能力来提高开发效率和系统可靠性。