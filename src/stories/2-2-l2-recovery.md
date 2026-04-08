# Story 2-2: L2恢复行为实现

> **Epic**: #2 错误处理与恢复机制
> **Priority**: P0 (Critical)
> **Points**: 4
> **Status**: ready-for-dev
> **Platform**: ROS2 / Python / BehaviorTree
> **Dependencies**: Story 2-1 (L1恢复行为实现)

---

## 📋 用户故事 (User Story)

作为图书馆机器人系统操作员，
我希望机器人在L1恢复失败后能够执行更深层的系统重置，
这样可以在更严重故障时恢复系统正常运行。

---

## 🎯 验收标准 (Acceptance Criteria)

### 功能性要求
- [ ] 实现L2状态重置行为（任务层面重置，30-40秒）
- [ ] 支持清除代价地图和重新规划路径
- [ ] 支持任务状态重置和重新开始
- [ ] 支持系统组件重启（选择性重启）
- [ ] 支持返回到Home位置重新初始化
- [ ] L2恢复失败后自动升级到L3恢复

### 性能要求
- [ ] L2恢复时间不超过40秒
- [ ] 重置过程中保持系统稳定性
- [ ] 恢复后系统状态完整

### 代码质量
- [ ] 继承L1恢复的基础架构
- [ ] 详细的恢复状态跟踪
- [ ] 完整的错误处理链

---

## 🔧 实现细节

### 文件清单
```
src/libbot_tasks/libbot_tasks/
├── l2_recovery_behaviors.py      # 新建 - L2恢复行为实现
├── behaviors/
│   └── l2_recovery_nodes.xml     # 新建 - L2 BT节点定义
└── config/
    └── l2_recovery_params.yaml   # 新建 - L2恢复参数配置
```

### L2RecoveryBehaviors类设计

```python
# l2_recovery_behaviors.py

import rclpy
from rclpy.node import Node
from behavior_tree import BehaviorTree
from typing import Optional, Dict, Any
import time

class L2RecoveryBehaviors:
    """L2状态重置行为 - 任务层面重置，30-40秒"""
    
    def __init__(self, node: Node):
        """初始化L2恢复行为
        
        Args:
            node: ROS2节点实例
        """
        self.node = node
        self.recovery_timeout = 40.0  # 40秒超时
        self.l1_recovery = None  # L1恢复实例
        
    def set_l1_recovery(self, l1_recovery):
        """设置L1恢复实例用于协同工作"""
        self.l1_recovery = l1_recovery
        
    def clear_costmaps_and_replan(self, goal_pose: Dict[str, Any]) -> bool:
        """清除代价地图并重新规划路径
        
        当导航持续失败时，清除所有代价地图并重新规划
        
        Args:
            goal_pose: 目标位置信息
            
        Returns:
            bool: 重新规划是否成功
        """
        try:
            self.node.get_logger().info("L2恢复: 清除代价地图并重新规划")
            
            # 清除全局代价地图
            if not self._clear_global_costmap():
                return False
                
            # 清除局部代价地图
            if not self._clear_local_costmap():
                return False
                
            # 重新规划路径
            success = self._replan_path(goal_pose)
            
            if success:
                self.node.get_logger().info("L2恢复成功: 代价地图清除并重新规划完成")
                return True
            else:
                self.node.get_logger().warn("L2恢复失败: 重新规划未成功")
                return False
                
        except Exception as e:
            self.node.get_logger().error(f"L2代价地图清除错误: {str(e)}")
            return False
    
    def reset_task_state(self, task_info: Dict[str, Any]) -> bool:
        """任务状态重置
        
        重置当前任务状态，重新开始任务执行
        
        Args:
            task_info: 任务信息
            
        Returns:
            bool: 重置是否成功
        """
        try:
            self.node.get_logger().info(f"L2恢复: 重置任务状态 {task_info.get('task_id')}")
            
            # 保存任务上下文
            saved_context = self._save_task_context(task_info)
            
            # 重置任务状态
            if not self._reset_task_execution():
                return False
                
            # 恢复任务上下文
            if not self._restore_task_context(saved_context):
                return False
                
            # 重新开始任务
            success = self._restart_task(task_info)
            
            if success:
                self.node.get_logger().info("L2恢复成功: 任务状态重置完成")
                return True
            else:
                self.node.get_logger().warn("L2恢复失败: 任务重启失败")
                return False
                
        except Exception as e:
            self.node.get_logger().error(f"L2任务重置错误: {str(e)}")
            return False
    
    def restart_system_components(self, components: list) -> bool:
        """系统组件重启
        
        选择性重启指定的系统组件
        
        Args:
            components: 需要重启的组件列表
            
        Returns:
            bool: 重启是否成功
        """
        try:
            self.node.get_logger().info(f"L2恢复: 重启系统组件 {components}")
            
            success_count = 0
            for component in components:
                if self._restart_single_component(component):
                    success_count += 1
                else:
                    self.node.get_logger().warn(f"组件 {component} 重启失败")
                    
            # 如果所有组件都成功重启
            if success_count == len(components):
                self.node.get_logger().info("L2恢复成功: 所有组件重启完成")
                return True
            elif success_count > 0:
                self.node.get_logger().warn(f"L2恢复部分成功: {success_count}/{len(components)} 组件重启成功")
                return True  # 部分成功也算成功
            else:
                self.node.get_logger().warn("L2恢复失败: 所有组件重启失败")
                return False
                
        except Exception as e:
            self.node.get_logger().error(f"L2组件重启错误: {str(e)}")
            return False
    
    def return_to_home_and_reset(self) -> bool:
        """返回Home位置并重新初始化
        
        当其他恢复方法都失败时，返回Home位置重新开始
        
        Returns:
            bool: 返回并重置是否成功
        """
        try:
            self.node.get_logger().info("L2恢复: 返回Home位置并重新初始化")
            
            # 导航到Home位置
            if not self._navigate_to_home():
                return False
                
            # 重新初始化系统
            if not self._reinitialize_system():
                return False
                
            # 更新系统状态
            success = self._update_system_status()
            
            if success:
                self.node.get_logger().info("L2恢复成功: 返回Home并重新初始化完成")
                return True
            else:
                self.node.get_logger().warn("L2恢复失败: 系统重新初始化失败")
                return False
                
        except Exception as e:
            self.node.get_logger().error(f"L2返回Home错误: {str(e)}")
            return False
    
    # 私有方法实现
    def _clear_global_costmap(self) -> bool:
        """清除全局代价地图"""
        try:
            # 调用Nav2清除全局代价地图服务
            from nav2_msgs.srv import ClearCostmap3D
            
            client = self.node.create_client(ClearCostmap3D, '/global_costmap/clear_entirely')
            if not client.wait_for_service(timeout_sec=5.0):
                self.node.get_logger().error("全局代价地图清除服务不可用")
                return False
                
            request = ClearCostmap3D.Request()
            future = client.call_async(request)
            
            # 等待服务调用完成
            rclpy.spin_until_future_complete(self.node, future, timeout_sec=10.0)
            
            if future.result() is not None:
                return True
            else:
                return False
                
        except Exception as e:
            self.node.get_logger().error(f"清除全局代价地图错误: {str(e)}")
            return False
    
    def _clear_local_costmap(self) -> bool:
        """清除局部代价地图"""
        try:
            # 调用Nav2清除局部代价地图服务
            from nav2_msgs.srv import ClearCostmap3D
            
            client = self.node.create_client(ClearCostmap3D, '/local_costmap/clear_entirely')
            if not client.wait_for_service(timeout_sec=5.0):
                self.node.get_logger().error("局部代价地图清除服务不可用")
                return False
                
            request = ClearCostmap3D.Request()
            future = client.call_async(request)
            
            rclpy.spin_until_future_complete(self.node, future, timeout_sec=10.0)
            
            if future.result() is not None:
                return True
            else:
                return False
                
        except Exception as e:
            self.node.get_logger().error(f"清除局部代价地图错误: {str(e)}")
            return False
    
    def _replan_path(self, goal_pose: Dict[str, Any]) -> bool:
        """重新规划路径"""
        try:
            # 重新发送导航目标
            from geometry_msgs.msg import PoseStamped
            from nav2_msgs.action import NavigateToPose
            
            # 创建目标位姿
            goal = PoseStamped()
            goal.header.frame_id = "map"
            goal.header.stamp = self.node.get_clock().now().to_msg()
            goal.pose.position.x = goal_pose.get('x', 0.0)
            goal.pose.position.y = goal_pose.get('y', 0.0)
            goal.pose.orientation.w = 1.0
            
            # 发送导航目标
            # 这里需要集成到现有的导航系统中
            return True
            
        except Exception as e:
            self.node.get_logger().error(f"重新规划路径错误: {str(e)}")
            return False
    
    def _save_task_context(self, task_info: Dict[str, Any]) -> Dict[str, Any]:
        """保存任务上下文"""
        # TODO: 实现任务上下文保存
        return task_info.copy()
    
    def _reset_task_execution(self) -> bool:
        """重置任务执行状态"""
        # TODO: 实现任务执行状态重置
        return True
    
    def _restore_task_context(self, context: Dict[str, Any]) -> bool:
        """恢复任务上下文"""
        # TODO: 实现任务上下文恢复
        return True
    
    def _restart_task(self, task_info: Dict[str, Any]) -> bool:
        """重新开始任务"""
        # TODO: 实现任务重新开始
        return True
    
    def _restart_single_component(self, component: str) -> bool:
        """重启单个系统组件"""
        # TODO: 实现组件重启逻辑
        # 可能包括：重启ROS2节点、重新初始化服务等
        return True
    
    def _navigate_to_home(self) -> bool:
        """导航到Home位置"""
        # TODO: 实现返回Home位置的导航
        return True
    
    def _reinitialize_system(self) -> bool:
        """重新初始化系统"""
        # TODO: 实现系统重新初始化
        return True
    
    def _update_system_status(self) -> bool:
        """更新系统状态"""
        # TODO: 实现系统状态更新
        return True
```

### L2 BehaviorTree节点定义

```xml
<!-- behaviors/l2_recovery_nodes.xml -->

<root main_tree_to_execute="L2RecoveryTree">
    
    <!-- L2恢复主行为树 -->
    <BehaviorTree ID="L2RecoveryTree">
        <Sequence name="L2_Recovery_Main">
            
            <!-- 检查L1恢复是否失败 -->
            <Condition ID="L1RecoveryFailed" />
            
            <!-- L2恢复策略选择 -->
            <ReactiveFallback name="L2_Recovery_Strategies">
                
                <!-- 代价地图清除和重新规划 -->
                <Sequence name="Costmap_Clear_Recovery">
                    <Condition ID="IsNavigationStuck" />
                    <Action ID="ClearCostmapsAndReplan" />
                </Sequence>
                
                <!-- 任务状态重置 -->
                <Sequence name="Task_Reset_Recovery">
                    <Condition ID="IsTaskCorrupted" />
                    <Action ID="ResetTaskState" />
                </Sequence>
                
                <!-- 系统组件重启 -->
                <Sequence name="Component_Restart_Recovery">
                    <Condition ID="AreComponentsUnhealthy" />
                    <Action ID="RestartSystemComponents" />
                </Sequence>
                
                <!-- 返回Home重置 -->
                <Sequence name="Home_Reset_Recovery">
                    <Condition ID="IsSystemUnrecoverable" />
                    <Action ID="ReturnToHomeAndReset" />
                </Sequence>
                
                <!-- 所有L2恢复都失败，升级到L3 -->
                <Action ID="EscalateToL3" />
                
            </ReactiveFallback>
        </Sequence>
    </BehaviorTree>
    
    <!-- 具体L2恢复节点 -->
    <BehaviorTree ID="ClearCostmapsAndReplan">
        <Timeout duration="30">
            <Sequence name="Clear_And_Replan_Sequence">
                <Action ID="ClearGlobalCostmap" />
                <Action ID="ClearLocalCostmap" />
                <Action ID="ReplanToGoal" />
            </Sequence>
        </Timeout>
    </BehaviorTree>
    
    <BehaviorTree ID="ResetTaskState">
        <Timeout duration="20">
            <Sequence name="Task_Reset_Sequence">
                <Action ID="SaveTaskContext" />
                <Action ID="ResetExecutionState" />
                <Action ID="RestoreTaskContext" />
                <Action ID="RestartTaskExecution" />
            </Sequence>
        </Timeout>
    </BehaviorTree>
    
    <BehaviorTree ID="RestartSystemComponents">
        <Timeout duration="25">
            <Fallback name="Component_Restart_Fallback">
                <Sequence name="Critical_Components">
                    <Action ID="RestartRFIDNodes" />
                    <Action ID="RestartPerceptionNodes" />
                </Sequence>
                <Sequence name="Navigation_Components">
                    <Action ID="RestartNav2Nodes" />
                </Sequence>
            </Fallback>
        </Timeout>
    </BehaviorTree>
    
    <BehaviorTree ID="ReturnToHomeAndReset">
        <Timeout duration="40">
            <Sequence name="Home_Reset_Sequence">
                <Action ID="NavigateToHomePosition" />
                <Action ID="ReinitializeAllSystems" />
                <Action ID="UpdateSystemStatusToReady" />
            </Sequence>
        </Timeout>
    </BehaviorTree>
    
</root>
```

### L2配置文件

```yaml
# config/l2_recovery_params.yaml

recovery:
  l2:
    # L2恢复参数
    timeout_seconds: 40               # 超时时间（秒）
    max_consecutive_failures: 2       # 最大连续失败次数
    
    costmap_clear:
      global_timeout: 15.0            # 全局代价地图清除超时
      local_timeout: 10.0             # 局部代价地图清除超时
      replan_timeout: 15.0            # 重新规划超时
    
    task_reset:
      context_save_timeout: 5.0       # 上下文保存超时
      reset_timeout: 10.0             # 重置超时
      restore_timeout: 5.0            # 上下文恢复超时
    
    component_restart:
      critical_components:            # 关键组件列表
        - "rfid_processor"
        - "perception_manager"
        - "sensor_fusion"
      navigation_components:          # 导航组件列表
        - "nav2_bringup"
        - "amcl"
        - "dwb_controller"
      restart_timeout: 20.0           # 组件重启超时
    
    home_reset:
      home_position:                  # Home位置坐标
        x: 0.0
        y: 0.0
        yaw: 0.0
      navigation_timeout: 25.0        # 返回Home超时
      reinit_timeout: 15.0            # 重新初始化超时

# ROS2参数声明
/**:
  ros__parameters:
    recovery.l2.timeout_seconds: 40
    recovery.l2.max_consecutive_failures: 2
    recovery.l2.costmap_clear.global_timeout: 15.0
    recovery.l2.costmap_clear.local_timeout: 10.0
    recovery.l2.costmap_clear.replan_timeout: 15.0
    recovery.l2.task_reset.context_save_timeout: 5.0
    recovery.l2.task_reset.reset_timeout: 10.0
    recovery.l2.task_reset.restore_timeout: 5.0
    recovery.l2.component_restart.restart_timeout: 20.0
    recovery.l2.home_reset.navigation_timeout: 25.0
    recovery.l2.home_reset.reinit_timeout: 15.0
```

---

## ✅ 完成检查清单

- [ ] L2RecoveryBehaviors类实现并测试
- [ ] L2 BehaviorTree节点定义正确
- [ ] L2配置文件参数合理
- [ ] 代价地图清除功能工作正常
- [ ] 任务状态重置功能工作正常
- [ ] 系统组件重启功能工作正常
- [ ] 返回Home重置功能工作正常
- [ ] 与L1恢复的集成正确
- [ ] 与L3恢复的升级机制正确
- [ ] 手动测试L2恢复流程

---

## 🔍 测试场景

### 测试1: 代价地图清除恢复
1. 模拟导航卡住情况
2. 触发L2代价地图清除
3. 验证重新规划成功恢复导航

### 测试2: 任务状态重置
1. 模拟任务状态损坏
2. 触发L2任务重置
3. 验证任务能够重新开始

### 测试3: 系统组件重启
1. 模拟关键组件故障
2. 触发L2组件重启
3. 验证系统功能恢复

### 测试4: 返回Home重置
1. 模拟系统无法恢复
2. 触发L2返回Home
3. 验证系统完全重置成功

---

## 📚 相关文档

- [Story 2-1: L1恢复行为实现](./2-1-l1-recovery.md) - L1恢复行为
- [Story 2-3: 错误检测机制实现](./2-3-error-detection.md) - 错误检测
- [Story 2-4: 与Behavior Tree集成](./2-4-bt-integration.md) - BT集成
- [Story 3-2: 系统健康指标监控实现](./3-2-health-monitoring.md) - 系统监控
- [docs/design_brainstorm_detailed.md#D2章节] - 错误处理详细设计

---

## 💡 实现提示

1. **层次化恢复**: L2恢复应该在L1恢复失败后触发
2. **状态管理**: 保持详细的恢复状态跟踪，便于调试
3. **超时控制**: 每个L2恢复操作都应该有严格的超时控制
4. **组件隔离**: 组件重启时要注意依赖关系和启动顺序
5. **Home位置**: 确保Home位置是安全的重新初始化点

---
