# Story 2-4: 与Behavior Tree集成

> **Epic**: #2 错误处理与恢复机制
> **Priority**: P0 (Critical)
> **Points**: 4
> **Status**: review
> **Platform**: ROS2 / Python / py_trees
> **Dependencies**: Story 2-1 (L1恢复行为实现), Story 2-2 (L2恢复行为实现), Story 2-3 (错误检测机制实现)

---

## 📋 用户故事 (User Story)

作为图书馆机器人系统开发者，
我希望错误恢复机制能够与Behavior Tree框架无缝集成，
这样可以实现统一的决策控制和可视化管理。

---

## 🎯 验收标准 (Acceptance Criteria)

### 功能性要求
- [ ] 实现BT Manager节点管理所有行为树
- [ ] 集成L1/L2恢复节点到行为树中
- [ ] 支持BT节点与错误检测器的通信
- [ ] 实现BT执行状态监控和反馈
- [ ] 支持BT热重载（不重启节点更新树）
- [ ] 实现BT可视化调试支持

### 性能要求
- [ ] BT执行频率10Hz
- [ ] 节点间通信延迟<50ms
- [ ] BT决策时间<100ms

### 代码质量
- [ ] 使用py_trees最佳实践
- [ ] 完整的BT节点文档
- [ ] 支持Groot可视化工具

---

## 🔧 实现细节

### 文件清单
```
src/libbot_tasks/libbot_tasks/
├── bt_manager_node.py           # 新建 - BT管理器节点
├── bt_nodes/
│   ├── recovery_nodes.py        # 新建 - 恢复相关BT节点
│   ├── condition_nodes.py       # 新建 - 条件判断节点
│   └── action_nodes.py          # 新建 - 动作执行节点
├── behaviors/
│   ├── main_bt.xml             # 新建 - 主行为树
│   ├── recovery_bt.xml         # 新建 - 恢复行为树
│   └── findbook_bt.xml         # 新建 - FindBook行为树
└── config/
    └── bt_config.yaml          # 新建 - BT配置
```

### BT Manager节点

```python
# bt_manager_node.py

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

import threading
import time
import os

import py_trees
from py_trees.common import Status as NodeStatus

from libbot_msgs.msg import BTExecutionStatus, BTNodeStatus
from libbot_msgs.srv import LoadBehaviorTree, ReloadBehaviorTree

class BTManagerNode(Node):
    """Behavior Tree管理器节点 - 统一管理所有行为树执行"""
    
    def __init__(self):
        super().__init__('bt_manager_node')
        
        # BT管理器
        self.bt_manager = BehaviorTreeManager()
        self.active_trees = {}  # 活跃的行为树
        self.tree_configs = {}  # 树配置信息
        
        # 线程安全
        self.callback_group = ReentrantCallbackGroup()
        self.tree_lock = threading.RLock()
        
        # 执行参数
        self.tick_rate = 10.0  # 10Hz执行频率
        self.execution_thread = None
        self.is_running = False
        
        # 初始化BT系统
        self._init_bt_system()
        
        # 创建ROS2接口
        self._create_ros_interfaces()
        
        # 启动执行线程
        self._start_execution()
        
        self.get_logger().info("BT Manager节点初始化完成")
        
    def _init_bt_system(self):
        """初始化Behavior Tree系统"""
        try:
            # 注册自定义节点类型
            self._register_custom_nodes()
            
            # 加载行为树配置
            self._load_tree_configs()
            
            # 加载默认行为树
            self._load_default_trees()
            
        except Exception as e:
            self.get_logger().error(f"BT系统初始化失败: {str(e)}")
            raise
            
    def _register_custom_nodes(self):
        """注册自定义BT节点类型"""
        from .bt_nodes.recovery_nodes import (
            L1RecoveryNode, L2RecoveryNode, ErrorDetectionNode
        )
        from .bt_nodes.condition_nodes import (
            IsBookAvailable, IsNavigationStuck, IsLocalizationLost
        )
        from .bt_nodes.action_nodes import (
            NavigateToBookshelf, ScanForBook, UpdateDatabase
        )
        
        # 注册恢复节点
        self.bt_manager.register_node("L1Recovery", L1RecoveryNode)
        self.bt_manager.register_node("L2Recovery", L2RecoveryNode)
        self.bt_manager.register_node("ErrorDetection", ErrorDetectionNode)
        
        # 注册条件节点
        self.bt_manager.register_node("IsBookAvailable", IsBookAvailable)
        self.bt_manager.register_node("IsNavigationStuck", IsNavigationStuck)
        self.bt_manager.register_node("IsLocalizationLost", IsLocalizationLost)
        
        # 注册动作节点
        self.bt_manager.register_node("NavigateToBookshelf", NavigateToBookshelf)
        self.bt_manager.register_node("ScanForBook", ScanForBook)
        self.bt_manager.register_node("UpdateDatabase", UpdateDatabase)
        
    def _load_tree_configs(self):
        """加载行为树配置文件"""
        config_path = os.path.join(
            os.path.dirname(__file__), 
            'config/bt_config.yaml'
        )
        
        try:
            import yaml
            with open(config_path, 'r') as f:
                configs = yaml.safe_load(f)
                
            self.tree_configs = configs.get('behavior_trees', {})
            self.get_logger().info(f"加载了 {len(self.tree_configs)} 个行为树配置")
            
        except Exception as e:
            self.get_logger().error(f"加载BT配置文件失败: {str(e)}")
            # 使用默认配置
            self._set_default_configs()
            
    def _load_default_trees(self):
        """加载默认行为树"""
        default_trees = [
            'behaviors/main_bt.xml',
            'behaviors/recovery_bt.xml', 
            'behaviors/findbook_bt.xml'
        ]
        
        for tree_file in default_trees:
            try:
                self._load_tree_from_file(tree_file)
            except Exception as e:
                self.get_logger().warn(f"加载行为树 {tree_file} 失败: {str(e)}")
                
    def _load_tree_from_file(self, tree_file: str) -> bool:
        """从文件加载单个行为树"""
        try:
            # 构建完整路径
            full_path = os.path.join(os.path.dirname(__file__), tree_file)
            
            if not os.path.exists(full_path):
                self.get_logger().error(f"行为树文件不存在: {full_path}")
                return False
                
            # 解析XML文件
            parser = XmlTreeParser()
            tree_xml = parser.load_from_file(full_path)
            
            # 提取树名称
            tree_name = os.path.splitext(os.path.basename(tree_file))[0]
            
            # 加载到BT管理器
            tree_id = self.bt_manager.load_tree(tree_xml, tree_name)
            
            if tree_id:
                self.get_logger().info(f"成功加载行为树: {tree_name} (ID: {tree_id})")
                return True
            else:
                self.get_logger().error(f"加载行为树失败: {tree_name}")
                return False
                
        except Exception as e:
            self.get_logger().error(f"加载行为树 {tree_file} 错误: {str(e)}")
            return False
            
    def _create_ros_interfaces(self):
        """创建ROS2接口"""
        
        # 发布BT执行状态
        self.bt_status_publisher = self.create_publisher(
            BTExecutionStatus,
            '/bt/execution_status',
            10
        )
        
        # 发布节点状态
        self.node_status_publisher = self.create_publisher(
            BTNodeStatus,
            '/bt/node_status',
            10
        )
        
        # 加载行为树服务
        self.load_tree_service = self.create_service(
            LoadBehaviorTree,
            '/bt/load_tree',
            self._load_tree_callback,
            callback_group=self.callback_group
        )
        
        # 重载行为树服务
        self.reload_tree_service = self.create_service(
            ReloadBehaviorTree,
            '/bt/reload_tree',
            self._reload_tree_callback,
            callback_group=self.callback_group
        )
        
        # 执行状态定时发布
        self.status_timer = self.create_timer(
            1.0,  # 1秒发布一次状态
            self._publish_status_callback,
            callback_group=self.callback_group
        )
        
    def _start_execution(self):
        """启动BT执行线程"""
        if self.is_running:
            return
            
        self.is_running = True
        self.execution_thread = threading.Thread(
            target=self._execution_loop,
            daemon=True
        )
        self.execution_thread.start()
        
        self.get_logger().info("BT执行线程启动")
        
    def _execution_loop(self):
        """BT执行主循环"""
        tick_interval = 1.0 / self.tick_rate
        
        while self.is_running and rclpy.ok():
            try:
                start_time = time.time()
                
                # 执行所有活跃的行为树
                self._tick_active_trees()
                
                # 计算执行时间
                execution_time = time.time() - start_time
                sleep_time = tick_interval - execution_time
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    self.get_logger().warn(
                        f"BT执行超时: {execution_time:.3f}s > {tick_interval:.3f}s"
                    )
                    
            except Exception as e:
                self.get_logger().error(f"BT执行循环错误: {str(e)}")
                time.sleep(0.1)  # 错误时短暂休眠
                
    def _tick_active_trees(self):
        """执行所有活跃行为树的tick"""
        with self.tree_lock:
            for tree_id, tree_info in self.active_trees.items():
                try:
                    # 执行tick
                    status = self.bt_manager.tick_tree(tree_id)
                    
                    # 更新状态信息
                    tree_info['last_status'] = status
                    tree_info['last_tick_time'] = time.time()
                    
                    # 如果树执行完成，处理结果
                    if status in [NodeStatus.SUCCESS, NodeStatus.FAILURE]:
                        self._handle_tree_completion(tree_id, status)
                        
                except Exception as e:
                    self.get_logger().error(
                        f"执行行为树 {tree_id} tick错误: {str(e)}"
                    )
                    
    def _handle_tree_completion(self, tree_id: str, status: NodeStatus):
        """处理行为树完成事件"""
        tree_info = self.active_trees.get(tree_id)
        if not tree_info:
            return
            
        tree_name = tree_info.get('name', 'unknown')
        
        if status == NodeStatus.SUCCESS:
            self.get_logger().info(f"行为树 {tree_name} 执行成功")
        else:
            self.get_logger().warn(f"行为树 {tree_name} 执行失败")
            
        # 根据配置决定是否重新执行或停止
        if tree_info.get('auto_restart', False):
            self.get_logger().info(f"自动重启行为树 {tree_name}")
            self.bt_manager.reset_tree(tree_id)
        else:
            # 停止执行
            self.stop_tree(tree_id)
            
    def start_tree(self, tree_name: str, auto_restart: bool = False) -> bool:
        """启动指定行为树
        
        Args:
            tree_name: 行为树名称
            auto_restart: 是否自动重启
            
        Returns:
            bool: 启动是否成功
        """
        try:
            # 查找树ID
            tree_id = self.bt_manager.get_tree_id(tree_name)
            if not tree_id:
                self.get_logger().error(f"找不到行为树: {tree_name}")
                return False
                
            with self.tree_lock:
                # 添加到活跃树列表
                self.active_trees[tree_id] = {
                    'name': tree_name,
                    'auto_restart': auto_restart,
                    'start_time': time.time(),
                    'last_status': NodeStatus.IDLE,
                    'last_tick_time': None
                }
                
            self.get_logger().info(
                f"启动行为树: {tree_name} (自动重启: {auto_restart})"
            )
            return True
            
        except Exception as e:
            self.get_logger().error(f"启动行为树 {tree_name} 失败: {str(e)}")
            return False
            
    def stop_tree(self, tree_id: str) -> bool:
        """停止指定行为树"""
        try:
            with self.tree_lock:
                if tree_id in self.active_trees:
                    tree_name = self.active_trees[tree_id]['name']
                    del self.active_trees[tree_id]
                    
                    self.get_logger().info(f"停止行为树: {tree_name}")
                    return True
                    
            return False
            
        except Exception as e:
            self.get_logger().error(f"停止行为树失败: {str(e)}")
            return False
            
    def _load_tree_callback(self, request, response):
        """加载行为树服务回调"""
        try:
            # 加载树文件
            success = self._load_tree_from_file(request.tree_file)
            
            response.success = success
            if success:
                response.message = f"成功加载行为树: {request.tree_file}"
            else:
                response.message = f"加载行为树失败: {request.tree_file}"
                
        except Exception as e:
            response.success = False
            response.message = f"加载行为树错误: {str(e)}"
            
        return response
        
    def _reload_tree_callback(self, request, response):
        """重载行为树服务回调"""
        try:
            tree_name = request.tree_name
            
            # 先卸载现有树
            if tree_name in self.bt_manager.get_loaded_trees():
                self.bt_manager.unload_tree(tree_name)
                
            # 重新加载
            tree_file = f"behaviors/{tree_name}.xml"
            success = self._load_tree_from_file(tree_file)
            
            response.success = success
            if success:
                response.message = f"成功重载行为树: {tree_name}"
            else:
                response.message = f"重载行为树失败: {tree_name}"
                
        except Exception as e:
            response.success = False
            response.message = f"重载行为树错误: {str(e)}"
            
        return response
        
    def _publish_status_callback(self):
        """发布BT状态回调"""
        try:
            # 发布执行状态
            status_msg = BTExecutionStatus()
            status_msg.header.stamp = self.get_clock().now().to_msg()
            
            with self.tree_lock:
                status_msg.active_trees = len(self.active_trees)
                status_msg.total_trees = len(self.bt_manager.get_loaded_trees())
                
                # 活跃树名称列表
                for tree_info in self.active_trees.values():
                    status_msg.running_tree_names.append(tree_info['name'])
                    
            self.bt_status_publisher.publish(status_msg)
            
            # 发布节点状态（简化版本）
            node_msg = BTNodeStatus()
            node_msg.header.stamp = self.get_clock().now().to_msg()
            node_msg.node_name = "bt_manager"
            node_msg.status = "running"
            
            self.node_status_publisher.publish(node_msg)
            
        except Exception as e:
            self.get_logger().error(f"发布BT状态错误: {str(e)}")
            
    def _set_default_configs(self):
        """设置默认配置"""
        self.tree_configs = {
            'main_bt': {
                'file': 'behaviors/main_bt.xml',
                'auto_start': True,
                'auto_restart': False
            },
            'recovery_bt': {
                'file': 'behaviors/recovery_bt.xml', 
                'auto_start': False,
                'auto_restart': False
            },
            'findbook_bt': {
                'file': 'behaviors/findbook_bt.xml',
                'auto_start': False,
                'auto_restart': True
            }
        }
        
    def get_tree_status(self, tree_name: str) -> dict:
        """获取指定行为树状态"""
        tree_id = self.bt_manager.get_tree_id(tree_name)
        if not tree_id:
            return {}
            
        with self.tree_lock:
            if tree_id in self.active_trees:
                return self.active_trees[tree_id].copy()
            else:
                return {'name': tree_name, 'status': 'not_running'}
                
    def shutdown(self):
        """关闭BT管理器"""
        self.get_logger().info("关闭BT管理器...")
        
        # 停止执行
        self.is_running = False
        
        # 停止所有活跃树
        with self.tree_lock:
            for tree_id in list(self.active_trees.keys()):
                self.stop_tree(tree_id)
                
        # 等待执行线程结束
        if self.execution_thread:
            self.execution_thread.join(timeout=2.0)
            
        self.get_logger().info("BT管理器已关闭")


def main(args=None):
    """主函数"""
    rclpy.init(args=args)
    
    try:
        # 创建BT管理器节点
        bt_manager = BTManagerNode()
        
        # 启动ROS2 spinning
        executor = MultiThreadedExecutor()
        executor.add_node(bt_manager)
        
        try:
            executor.spin()
        except KeyboardInterrupt:
            bt_manager.get_logger().info("收到Ctrl+C，关闭...")
        finally:
            executor.shutdown()
            
    except Exception as e:
        print(f"BT管理器启动失败: {str(e)}")
    finally:
        if 'bt_manager' in locals():
            bt_manager.shutdown()
            bt_manager.destroy_node()
        
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### 主行为树XML定义

```xml
<!-- behaviors/main_bt.xml -->

<root main_tree_to_execute="MainBehaviorTree">
    
    <!-- 主行为树 - 协调整个机器人行为 -->
    <BehaviorTree ID="MainBehaviorTree">
        <ReactiveFallback name="Main_Control_Flow">
            
            <!-- 1. 错误处理和恢复 -->
            <Sequence name="Error_Handling">
                <Condition ID="HasActiveErrors" />
                <Action ID="HandleErrors" />
            </Sequence>
            
            <!-- 2. 任务执行 -->
            <Sequence name="Task_Execution">
                <Condition ID="HasPendingTasks" />
                <Action ID="ExecuteNextTask" />
            </Sequence>
            
            <!-- 3. 系统监控 -->
            <Sequence name="System_Monitoring">
                <Condition ID="ShouldMonitorSystem" />
                <Action ID="PerformSystemCheck" />
            </Sequence>
            
            <!-- 4. 待机状态 -->
            <Action ID="EnterIdleState" />
            
        </ReactiveFallback>
    </BehaviorTree>
    
    <!-- 错误处理子树 -->
    <BehaviorTree ID="HandleErrors">
        <Fallback name="Error_Recovery_Strategy">
            
            <!-- L1快速恢复 -->
            <Sequence name="L1_Recovery_Attempt">
                <Condition ID="CanUseL1Recovery" />
                <Action ID="L1Recovery" />
            </Sequence>
            
            <!-- L2状态重置 -->
            <Sequence name="L2_Recovery_Attempt">
                <Condition ID="CanUseL2Recovery" />
                <Action ID="L2Recovery" />
            </Sequence>
            
            <!-- L3系统重置 -->
            <Sequence name="L3_Recovery_Attempt">
                <Condition ID="CanUseL3Recovery" />
                <Action ID="L3Recovery" />
            </Sequence>
            
            <!-- 无法恢复，需要人工干预 -->
            <Action ID="RequestHumanIntervention" />
            
        </Fallback>
    </BehaviorTree>
    
    <!-- 任务执行子树 -->
    <BehaviorTree ID="ExecuteNextTask">
        <Sequence name="Task_Execution_Flow">
            
            <!-- 获取下一个任务 -->
            <Action ID="GetNextTaskFromQueue" />
            
            <!-- 根据任务类型选择执行策略 -->
            <ReactiveFallback name="Task_Type_Selector">
                
                <!-- FindBook任务 -->
                <Sequence name="FindBook_Task">
                    <Condition ID="IsFindBookTask" />
                    <SubTree ID="FindBookBehaviorTree" />
                </Sequence>
                
                <!-- Inventory任务 -->
                <Sequence name="Inventory_Task">
                    <Condition ID="IsInventoryTask" />
                    <SubTree ID="InventoryBehaviorTree" />
                </Sequence>
                
                <!-- Navigation任务 -->
                <Sequence name="Navigation_Task">
                    <Condition ID="IsNavigationTask" />
                    <Action ID="NavigateToPose" />
                </Sequence>
                
            </ReactiveFallback>
            
        </Sequence>
    </BehaviorTree>
    
    <!-- 系统监控子树 -->
    <BehaviorTree ID="PerformSystemCheck">
        <Parallel name="System_Health_Checks">
            <Action ID="CheckLocalizationHealth" />
            <Action ID="CheckNavigationHealth" />
            <Action ID="CheckPerceptionHealth" />
            <Action ID="CheckSystemResources" />
        </Parallel>
    </BehaviorTree>
    
</root>
```

### BT配置文件

```yaml
# config/bt_config.yaml

behavior_trees:
  # 主行为树配置
  main_bt:
    file: "behaviors/main_bt.xml"
    auto_start: true
    auto_restart: false
    tick_rate: 10.0
    
  # 恢复行为树配置
  recovery_bt:
    file: "behaviors/recovery_bt.xml"
    auto_start: false
    auto_restart: false
    tick_rate: 10.0
    
  # FindBook行为树配置
  findbook_bt:
    file: "behaviors/findbook_bt.xml"
    auto_start: false
    auto_restart: true
    tick_rate: 10.0

# BT执行参数
execution:
  default_tick_rate: 10.0          # 默认执行频率(Hz)
  max_execution_time: 0.1          # 最大执行时间(s)
  error_retry_count: 3             # 错误重试次数
  
# 节点超时配置
node_timeouts:
  navigation_nodes: 30.0           # 导航节点超时(s)
  perception_nodes: 10.0           # 感知节点超时(s)
  recovery_nodes: 60.0             # 恢复节点超时(s)
  database_nodes: 5.0              # 数据库节点超时(s)

# 调试配置
debug:
  enable_visualization: true       # 启用可视化
  publish_tree_status: true        # 发布树状态
  log_node_execution: true         # 记录节点执行
  
# Groot集成配置
groot:
  enable: true                     # 启用Groot支持
  update_frequency: 2.0            # 更新频率(Hz)
  publish_execution_flow: true