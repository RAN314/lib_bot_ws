# Story 5-1: Topic接口实现

> **Epic**: #5 API设计细节
> **Priority**: P0 (Critical)
> **Points**: 4
> **Status**: ready-for-dev
> **Platform**: ROS2 / Python
> **Dependencies**: Story 5-4 (libbot_msgs消息包实现)

---

## 📋 用户故事 (User Story)

作为ROS2开发者，
我希望系统提供标准化的Topic接口，
这样可以方便地实现各模块间的数据通信。

---

## 🎯 验收标准 (Acceptance Criteria)

### 功能性要求
- [ ] 实现RFID扫描Topic接口（4个方向）
- [ ] 实现系统健康状态Topic
- [ ] 实现图书位置更新Topic
- [ ] 实现导航反馈Topic
- [ ] 配置QoS策略
- [ ] 实现Topic数据验证

### 性能要求
- [ ] Topic发布频率稳定
- [ ] 数据传输延迟<50ms
- [ ] 支持多订阅者

### 代码质量
- [ ] 统一的Topic接口设计
- [ ] 完整的接口文档
- [ ] 错误处理和超时机制

---

## 🔧 实现细节

### 文件清单
```
src/libbot_perception/libbot_perception/
├── topic_publishers.py          # 新建 - Topic发布器
├── topic_subscribers.py         # 新建 - Topic订阅器
└── config/
    └── topic_config.yaml        # 新建 - Topic配置

src/libbot_msgs/msg/
├── RFIDScan.msg                # 已存在 - RFID扫描消息
├── SystemHealth.msg            # 已存在 - 系统健康消息
├── BookLocation.msg            # 已存在 - 图书位置消息
└── NavigationFeedback.msg      # 已存在 - 导航反馈消息
```

### Topic发布器实现

```python
# topic_publishers.py

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy
from typing import Dict, Any, Optional
import threading
import time

from libbot_msgs.msg import (
    RFIDScan, SystemHealth, BookLocation, NavigationFeedback
)
from std_msgs.msg import Header

class TopicPublisherManager:
    """Topic发布管理器 - 统一管理所有Topic发布"""
    
    def __init__(self, node: Node):
        """初始化Topic发布管理器
        
        Args:
            node: ROS2节点实例
        """
        self.node = node
        self.publishers = {}
        self.publishing_threads = {}
        self.is_running = False
        
        # 默认QoS配置
        self.default_qos = QoSProfile(
            reliability=QoSReliabilityPolicy.RELIABLE,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        # 高频率数据QoS（RFID扫描）
        self.high_freq_qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=5
        )
        
    def initialize_publishers(self):
        """初始化所有Topic发布器"""
        try:
            # 1. RFID扫描Topic（4个方向）
            self._create_rfid_publishers()
            
            # 2. 系统健康Topic
            self._create_system_health_publisher()
            
            # 3. 图书位置Topic
            self._create_book_location_publisher()
            
            # 4. 导航反馈Topic
            self._create_navigation_feedback_publisher()
            
            self.node.get_logger().info(
                f"初始化了 {len(self.publishers)} 个Topic发布器"
            )
            
        except Exception as e:
            self.node.get_logger().error(f"初始化发布器错误: {str(e)}")
            raise
            
    def _create_rfid_publishers(self):
        """创建RFID扫描Topic发布器"""
        directions = ['front', 'back', 'left', 'right']
        
        for direction in directions:
            topic_name = f'/rfid/scan/{direction}'
            
            publisher = self.node.create_publisher(
                RFIDScan,
                topic_name,
                self.high_freq_qos
            )
            
            self.publishers[topic_name] = {
                'publisher': publisher,
                'message_type': RFIDScan,
                'direction': direction,
                'rate': 10.0  # 10Hz
            }
            
    def _create_system_health_publisher(self):
        """创建系统健康Topic发布器"""
        topic_name = '/system/health'
        
        publisher = self.node.create_publisher(
            SystemHealth,
            topic_name,
            self.default_qos
        )
        
        self.publishers[topic_name] = {
            'publisher': publisher,
            'message_type': SystemHealth,
            'rate': 1.0  # 1Hz
        }
        
    def _create_book_location_publisher(self):
        """创建图书位置Topic发布器"""
        topic_name = '/books/locations'
        
        publisher = self.node.create_publisher(
            BookLocation,
            topic_name,
            self.default_qos
        )
        
        self.publishers[topic_name] = {
            'publisher': publisher,
            'message_type': BookLocation,
            'rate': 0.5  # 0.5Hz
        }
        
    def _create_navigation_feedback_publisher(self):
        """创建导航反馈Topic发布器"""
        topic_name = '/nav2/feedback'
        
        publisher = self.node.create_publisher(
            NavigationFeedback,
            topic_name,
            self.default_qos
        )
        
        self.publishers[topic_name] = {
            'publisher': publisher,
            'message_type': NavigationFeedback,
            'rate': 10.0  # 10Hz
        }
        
    def publish_rfid_scan(self, direction: str, tags: list, 
                         signal_strengths: list, timestamp: Optional[float] = None):
        """发布RFID扫描数据
        
        Args:
            direction: 扫描方向 (front/back/left/right)
            tags: 检测到的标签列表
            signal_strengths: 信号强度列表
            timestamp: 时间戳
        """
        try:
            topic_name = f'/rfid/scan/{direction}'
            
            if topic_name not in self.publishers:
                self.node.get_logger().error(f"RFID发布器不存在: {topic_name}")
                return False
                
            # 创建消息
            msg = RFIDScan()
            msg.header = Header()
            msg.header.stamp = self.node.get_clock().now().to_msg()
            msg.header.frame_id = f"rfid_{direction}"
            
            if timestamp:
                msg.scan_timestamp = timestamp
            else:
                msg.scan_timestamp = time.time()
                
            msg.direction = direction
            msg.detected_tags = tags
            msg.signal_strengths = signal_strengths
            msg.scan_range = 0.5  # 检测范围
            msg.scan_angle = 90.0  # 扫描角度
            
            # 发布消息
            publisher_info = self.publishers[topic_name]
            publisher_info['publisher'].publish(msg)
            
            return True
            
        except Exception as e:
            self.node.get_logger().error(f"发布RFID扫描错误: {str(e)}")
            return False
            
    def publish_system_health(self, health_data: Dict[str, Any]):
        """发布系统健康状态
        
        Args:
            health_data: 健康数据字典
        """
        try:
            topic_name = '/system/health'
            
            if topic_name not in self.publishers:
                return False
                
            msg = SystemHealth()
            msg.header = Header()
            msg.header.stamp = self.node.get_clock().now().to_msg()
            
            # 填充健康数据
            msg.navigation_health = health_data.get('navigation_health', 0.0)
            msg.perception_health = health_data.get('perception_health', 0.0)
            msg.database_health = health_data.get('database_health', 0.0)
            msg.ui_health = health_data.get('ui_health', 0.0)
            
            msg.active_nodes = health_data.get('active_nodes', [])
            msg.inactive_nodes = health_data.get('inactive_nodes', [])
            msg.active_warnings = health_data.get('active_warnings', [])
            msg.active_errors = health_data.get('active_errors', [])
            
            msg.cpu_usage = health_data.get('cpu_usage', 0.0)
            msg.memory_usage = health_data.get('memory_usage', 0.0)
            msg.disk_usage = health_data.get('disk_usage', 0.0)
            
            # 发布消息
            publisher_info = self.publishers[topic_name]
            publisher_info['publisher'].publish(msg)
            
            return True
            
        except Exception as e:
            self.node.get_logger().error(f"发布系统健康状态错误: {str(e)}")
            return False
            
    def publish_book_location(self, book_id: str, position: Dict[str, float], 
                            status: str, confidence: float = 1.0):
        """发布图书位置更新
        
        Args:
            book_id: 图书ID
            position: 位置信息
            status: 图书状态
            confidence: 检测置信度
        """
        try:
            topic_name = '/books/locations'
            
            if topic_name not in self.publishers:
                return False
                
            msg = BookLocation()
            msg.header = Header()
            msg.header.stamp = self.node.get_clock().now().to_msg()
            
            msg.book_id = book_id
            msg.position.x = position.get('x', 0.0)
            msg.position.y = position.get('y', 0.0)
            msg.position.z = position.get('z', 0.0)
            
            msg.status = status
            msg.confidence = confidence
            msg.last_updated = time.time()
            
            msg.shelf_zone = position.get('shelf_zone', '')
            msg.shelf_level = position.get('shelf_level', 0)
            msg.shelf_position = position.get('shelf_position', 0)
            
            # 发布消息
            publisher_info = self.publishers[topic_name]
            publisher_info['publisher'].publish(msg)
            
            return True
            
        except Exception as e:
            self.node.get_logger().error(f"发布图书位置错误: {str(e)}")
            return False
            
    def publish_navigation_feedback(self, feedback_data: Dict[str, Any]):
        """发布导航反馈
        
        Args:
            feedback_data: 导航反馈数据
        """
        try:
            topic_name = '/nav2/feedback'
            
            if topic_name not in self.publishers:
                return False
                
            msg = NavigationFeedback()
            msg.header = Header()
            msg.header.stamp = self.node.get_clock().now().to_msg()
            
            # 填充导航反馈数据
            msg.current_pose.position.x = feedback_data.get('current_x', 0.0)
            msg.current_pose.position.y = feedback_data.get('current_y', 0.0)
            msg.current_pose.position.z = 0.0
            
            msg.goal_pose.position.x = feedback_data.get('goal_x', 0.0)
            msg.goal_pose.position.y = feedback_data.get('goal_y', 0.0)
            msg.goal_pose.position.z = 0.0
            
            msg.distance_to_goal = feedback_data.get('distance_to_goal', 0.0)
            msg.estimated_time_remaining = feedback_data.get('estimated_time', 0.0)
            msg.navigation_state = feedback_data.get('state', 'unknown')
            
            msg.path_length = feedback_data.get('path_length', 0.0)
            msg.path_progress = feedback_data.get('progress', 0.0)
            msg.current_velocity = feedback_data.get('velocity', 0.0)
            
            msg.warnings = feedback_data.get('warnings', [])
            msg.errors = feedback_data.get('errors', [])
            
            # 发布消息
            publisher_info = self.publishers[topic_name]
            publisher_info['publisher'].publish(msg)
            
            return True
            
        except Exception as e:
            self.node.get_logger().error(f"发布导航反馈错误: {str(e)}")
            return False
            
    def start_periodic_publishing(self):
        """启动周期性发布"""
        if self.is_running:
            return
            
        self.is_running = True
        
        # 为每个发布器启动独立线程
        for topic_name, pub_info in self.publishers.items():
            rate = pub_info.get('rate', 1.0)
            
            thread = threading.Thread(
                target=self._publishing_loop,
                args=(topic_name, rate),
                daemon=True,
                name=f"pub_{topic_name.replace('/', '_')}"
            )
            
            self.publishing_threads[topic_name] = thread
            thread.start()
            
        self.node.get_logger().info("周期性发布启动")
        
    def _publishing_loop(self, topic_name: str, rate: float):
        """发布循环
        
        Args:
            topic_name: Topic名称
            rate: 发布频率
        """
        period = 1.0 / rate
        
        while self.is_running and rclpy.ok():
            try:
                start_time = time.time()
                
                # 根据Topic类型执行相应的发布逻辑
                if topic_name.startswith('/rfid/scan/'):
                    self._publish_rfid_data(topic_name)
                elif topic_name == '/system/health':
                    self._publish_health_data()
                elif topic_name == '/books/locations':
                    self._publish_location_data()
                elif topic_name == '/nav2/feedback':
                    self._publish_navigation_data()
                    
                # 计算休眠时间
                elapsed = time.time() - start_time
                sleep_time = period - elapsed
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    self.node.get_logger().warn(
                        f"Topic {topic_name} 发布周期超时: {elapsed:.3f}s > {period:.3f}s"
                    )
                    
            except Exception as e:
                self.node.get_logger().error(
                    f"Topic {topic_name} 发布循环错误: {str(e)}"
                )
                time.sleep(0.1)
                
    def _publish_rfid_data(self, topic_name: str):
        """发布RFID数据（模拟数据）"""
        # TODO: 从实际RFID传感器获取数据
        direction = topic_name.split('/')[-1]
        
        # 模拟数据
        tags = []
        strengths = []
        
        # 随机生成一些检测数据用于测试
        import random
        if random.random() < 0.3:  # 30%概率检测到标签
            tags.append(f"tag_{random.randint(1, 100)}")
            strengths.append(random.uniform(0.5, 1.0))
            
        self.publish_rfid_scan(direction, tags, strengths)
        
    def _publish_health_data(self):
        """发布健康数据（模拟数据）"""
        # TODO: 从实际系统监控获取数据
        health_data = {
            'navigation_health': 0.95,
            'perception_health': 0.90,
            'database_health': 0.98,
            'ui_health': 0.88,
            'active_nodes': ['nav2', 'rfid', 'database'],
            'inactive_nodes': [],
            'active_warnings': [],
            'active_errors': [],
            'cpu_usage': 0.35,
            'memory_usage': 0.45,
            'disk_usage': 0.25
        }
        
        self.publish_system_health(health_data)
        
    def _publish_location_data(self):
        """发布位置数据（模拟数据）"""
        # TODO: 从实际数据库获取数据
        pass
        
    def _publish_navigation_data(self):
        """发布导航数据（模拟数据）"""
        # TODO: 从实际导航系统获取数据
        pass
        
    def stop_publishing(self):
        """停止发布"""
        self.is_running = False
        
        # 等待所有发布线程结束
        for topic_name, thread in self.publishing_threads.items():
            thread.join(timeout=2.0)
            
        self.publishing_threads.clear()
        
        self.node.get_logger().info("发布停止")
        
    def get_publisher_status(self) -> Dict[str, Any]:
        """获取发布器状态"""
        status = {
            'running': self.is_running,
            'publishers': {}
        }
        
        for topic_name, pub_info in self.publishers.items():
            status['publishers'][topic_name] = {
                'rate': pub_info.get('rate', 0.0),
                'message_type': str(pub_info.get('message_type', '')),
                'has_thread': topic_name in self.publishing_threads
            }
            
        return status
```

### Topic配置文件

```yaml
# config/topic_config.yaml

topics:
  # RFID扫描Topic配置
  rfid_scan:
    enable: true
    directions: ["front", "back", "left", "right"]
    
    # 发布频率配置
    publish_rate: 10.0           # Hz
    
    # QoS配置
    qos:
      reliability: "BEST_EFFORT"  # 尽力而为，允许丢包
      history: "KEEP_LAST"
      depth: 5
      
    # 数据配置
    scan_range: 0.5              # 检测范围(m)
    scan_angle: 90.0             # 扫描角度(度)
    
  # 系统健康Topic配置
  system_health:
    enable: true
    topic_name: "/system/health"
    publish_rate: 1.0            # Hz
    
    qos:
      reliability: "RELIABLE"     # 可靠传输
      history: "KEEP_LAST"
      depth: 10
      
    # 监控项配置
    monitor_items:
      - "navigation"
      - "perception"
      - "database"
      - "ui"
      - "cpu_usage"
      - "memory_usage"
      
  # 图书位置Topic配置
  book_location:
    enable: true
    topic_name: "/books/locations"
    publish_rate: 0.5            # Hz
    
    qos:
      reliability: "RELIABLE"
      history: "KEEP_LAST"
      depth: 10
      
  # 导航反馈Topic配置
  navigation_feedback:
    enable: true
    topic_name: "/nav2/feedback"
    publish_rate: 10.0           # Hz
    
    qos:
      reliability: "RELIABLE"
      history: "KEEP_LAST"
      depth: 10
      
# 全局Topic配置
global:
  # 默认QoS配置
  default_qos:
    reliability: "RELIABLE"
    history: "KEEP_LAST"
    depth: 10
    
  # 性能配置
  performance:
    max_publish_rate: 50.0       # 最大发布频率
    queue_size: 1000             # 内部队列大小
    thread_pool_size: 4          # 线程池大小
    
  # 调试配置
  debug:
    enable_topic_logging: true   # 启用Topic日志
    log_publish_timing: true     # 记录发布时间
    max_log_entries: 100         # 最大日志条目

# ROS2参数声明
/**:
  ros__parameters:
    topics.rfid_scan.enable: true
    topics.rfid_scan.publish_rate: 10.0
    topics.rfid_scan.scan_range: 0.5
    topics.rfid_scan.scan_angle: 90.0
    topics.system_health.enable: true
    topics.system_health.publish_rate: 1.0
    topics.book_location.enable: true
    topics.book_location.publish_rate: 0.5
    topics.navigation_feedback.enable: true
    topics.navigation_feedback.publish_rate: 10.0
```

---

## ✅ 完成检查清单

- [ ] TopicPublisherManager类实现
- [ ] RFID扫描Topic发布功能
- [ ] 系统健康Topic发布功能
- [ ] 图书位置Topic发布功能
- [ ] 导航反馈Topic发布功能
- [ ] QoS配置正确
- [ ] 周期性发布功能
- [ ] 错误处理和恢复
- [ ] 手动测试Topic通信

---

## 🔍 测试场景

### 测试1: RFID Topic发布
1. 启动RFID Topic发布
2. 使用ros2 topic echo验证数据
3. 验证四个方向的Topic都正常工作

### 测试2: 系统健康Topic
1. 启动健康监控
2. 验证健康数据定期发布
3. 验证数据格式正确

### 测试3: QoS验证
1. 测试RELIABLE QoS的可靠性
2. 测试BEST_EFFORT QoS的性能
3. 验证多订阅者场景

### 测试4: 性能测试
1. 测量Topic发布延迟
2. 验证发布频率稳定性
3. 测试高负载情况下的性能

---

## 📚 相关文档

- [Story 5-2: Service接口实现](./5-2-service-interfaces.md) - Service接口
- [Story 5-3: Action接口实现](./5-3-action-interfaces.md) - Action接口
- [Story 5-4: libbot_msgs消息包实现](./5-4-msgs-package.md) - 消息定义
- [docs/design_brainstorm_detailed.md#D5章节] - API设计详细设计

---

## 💡 实现提示

1. **QoS策略**: 根据数据重要性选择合适的QoS
2. **性能优化**: 高频率数据使用BEST_EFFORT减少开销
3. **线程安全**: 每个Topic使用独立的发布线程
4. **错误处理**: Topic错误不应影响其他Topic
5. **监控**: 实时监控Topic发布状态和性能

---
