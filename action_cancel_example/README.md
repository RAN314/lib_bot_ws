# Test Action Cancel - ROS2 Action Cancel功能演示

## 概述

这是一个ROS2功能包，用于演示Action的cancel功能和基于topic控制的连续goal执行。主要包含一个action server和一个action client，通过`/cancel_control` topic实现实时控制。

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Control       │    │   Client        │    │   Server        │
│   Publisher     │───▶│                 │◀──▶│                 │
│                 │    │ - 订阅控制信号   │    │ - 执行20步任务   │
│   (可选)        │    │ - 发送/取消goal  │    │ - 实时cancel    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ /cancel_control │
                       │    (Bool)       │
                       └─────────────────┘
```

## Action接口定义

### TestCancel.action
```action
int32 duration  # 目标执行时长（实际固定为20步）
---
string message  # 结果消息
---
string progress # 执行进度
```

## Server设计

### 核心功能
- **固定执行周期**：忽略client发送的duration参数，固定执行20步
- **实时反馈**：每步执行后发布feedback，显示当前进度
- **Cancel响应**：在执行过程中检查cancel请求，立即停止并返回结果
- **异步执行**：使用MultiThreadedExecutor支持并发

### 关键代码逻辑

```python
async def execute_callback(self, goal_handle):
    for i in range(20):  # 固定20步
        if goal_handle.is_cancel_requested:
            goal_handle.canceled()
            return TestCancel.Result(message="Goal was canceled")

        # 发布进度反馈
        feedback_msg.progress = f"Step {i + 1}/20"
        goal_handle.publish_feedback(feedback_msg)

        # 等待1秒（模拟工作）
        rclpy.spin_once(self, timeout_sec=1.0)

    goal_handle.succeed()
    return TestCancel.Result(message="Goal succeeded")
```

## Client设计

### 核心功能
- **Topic控制**：订阅`/cancel_control` Bool topic实现外部控制
- **状态管理**：维护运行状态，防止重复发送goal
- **自动连续执行**：goal成功后根据控制状态自动发送下一个goal
- **即时Cancel**：收到停止信号时立即cancel当前goal

### 控制逻辑

| 控制信号 | 含义 | Client行为 |
|---------|------|-----------|
| `False` | 开始/继续运行 | 发送goal，成功后自动继续 |
| `True` | 停止运行 | Cancel当前goal，停止发送新goal |

### 状态变量
- `_should_continue`: 当前是否应该停止运行 (True=停止, False=继续)
- `_goal_handle`: 当前活跃goal的句柄
- `_sending_goal`: 防止重复发送goal的标志

### 关键代码逻辑

```python
def control_callback(self, msg):
    control_run = not msg.data  # False=运行, True=取消
    self._should_continue = not control_run

    if control_run and not self._goal_handle and not self._sending_goal:
        self.send_goal()  # 开始新goal
    elif not control_run and self._goal_handle:
        self.cancel_goal()  # 取消当前goal

def get_result_callback(self, future):
    result = future.result().result
    self._goal_handle = None
    self._sending_goal = False

    # 根据控制状态决定是否继续
    if not self._should_continue:
        self.send_goal()  # 自动发送下一个goal
```

## 工作流程

### 启动流程
1. Server启动，注册action server `/test_cancel`
2. Client启动，订阅 `/cancel_control` topic
3. 等待控制信号

### 运行流程
```
收到 False → 发送Goal → Server执行20步 → 返回成功 → 自动发送下一个Goal
     ↓
收到 True  → Cancel当前Goal → 停止发送新Goal
```

### 详细时序
1. **初始状态**：Client等待控制信号
2. **收到`False`**：Client发送goal，Server开始执行
3. **执行过程**：
   - Server每秒发布一次feedback
   - Client可以随时发送`True`进行cancel
4. **执行完成**：
   - Server返回成功结果
   - Client检查控制状态
   - 如果仍为`False`，自动发送下一个goal
5. **收到`True`**：
   - 如果有活跃goal，立即cancel
   - 停止自动发送新goal

## 关键特性

### 1. 实时Cancel
- Server在每次循环开始时检查`goal_handle.is_cancel_requested`
- Client调用`goal_handle.cancel_goal_async()`发送cancel请求
- 支持异步cancel，立即响应

### 2. 连续执行
- Goal完成后不退出，而是根据控制状态决定是否继续
- 实现了"循环执行"模式，无需外部干预

### 3. 外部控制
- 通过ROS topic实现解耦控制
- 可以被其他节点或脚本控制
- 支持动态调整执行策略

### 4. 状态保护
- `_sending_goal`标志防止重复发送goal
- 状态检查确保操作的原子性
- 异常情况下的状态重置

## 测试方法

### 基本测试
```bash
# 终端1：启动server
ros2 run test_action_cancel test_cancel_server

# 终端2：启动client
ros2 run test_action_cancel test_cancel_client

# 终端3：发送控制信号
ros2 topic pub /cancel_control std_msgs/Bool "data: false"  # 开始运行
ros2 topic pub /cancel_control std_msgs/Bool "data: true"   # 停止运行
```

### 自动测试
```bash
# 使用control_publisher自动切换
ros2 run test_action_cancel control_publisher
```

### 验证Cancel
1. 发送`false`开始执行
2. 等待几秒，看到feedback
3. 发送`true`进行cancel
4. 观察server和client的日志

## 日志分析

### Server日志
```
[INFO] Received goal request with duration: 20
[INFO] Starting goal execution
[INFO] Publishing feedback: Step 1/20
...
[INFO] Goal execution completed successfully
[INFO] Returning success result to client
```

### Client日志
```
[INFO] Control message received: False (run_goals=True)
[INFO] Goal accepted
[INFO] Received feedback: Step 1/20
...
[INFO] Result: Goal succeeded
[INFO] Goal completed, sending next goal...
```

## 设计优势

1. **模块化**：Server和Client独立，可以单独测试
2. **可扩展**：Topic控制机制易于扩展更多控制逻辑
3. **实时性**：Cancel响应及时，支持中断执行
4. **鲁棒性**：状态检查和标志防止竞态条件
5. **可观察**：详细日志便于调试和监控

## 潜在改进

1. **参数化**：将固定20步改为可配置参数
2. **多Client**：支持多个client同时控制
3. **优先级**：Cancel请求的优先级处理
4. **超时控制**：Goal执行的超时机制
5. **结果反馈**：更详细的执行结果统计

## 总结

这个实现展示了ROS2 Action的强大功能：
- 通过cancel机制实现实时中断
- 通过topic实现外部控制
- 通过状态机实现连续执行
- 通过异步编程实现并发处理

是学习ROS2 Action高级特性的优秀示例。