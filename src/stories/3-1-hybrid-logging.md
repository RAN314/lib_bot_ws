# Story 3-1: 混合日志方案实现

> **Epic**: #3 日志与监控系统
> **Priority**: P0 (Critical)
> **Points**: 3
> **Status**: ready-for-dev
> **Platform**: ROS2 / Python / SQLite
> **Dependencies**: Story 5-4 (libbot_msgs消息包实现)

---

## 📋 用户故事 (User Story)

作为系统管理员，
我希望系统能够同时记录ROS2系统日志和业务操作日志，
这样可以全面了解系统运行状态和业务处理情况。

---

## 🎯 验收标准 (Acceptance Criteria)

### 功能性要求
- [ ] 实现ROS2日志捕获和存储
- [ ] 实现业务日志记录到SQLite
- [ ] 支持日志分类（系统日志 vs 业务日志）
- [ ] 实现日志级别管理（INFO/WARN/ERROR）
- [ ] 支持日志查询和检索
- [ ] 实现日志自动轮转机制

### 性能要求
- [ ] 日志写入延迟<10ms
- [ ] 查询响应时间<100ms
- [ ] 支持1000条/秒的写入性能

### 代码质量
- [ ] 统一的日志接口
- [ ] 异步日志写入
- [ ] 错误处理和恢复

---

## 🔧 实现细节

### 文件清单
```
src/libbot_database/libbot_database/
├── log_manager.py              # 新建 - 日志管理器
├── log_handlers/
│   ├── ros2_log_handler.py     # 新建 - ROS2日志处理器
│   ├── business_log_handler.py # 新建 - 业务日志处理器
│   └── database_handler.py     # 新建 - 数据库处理器
└── config/
    └── logging_config.yaml     # 新建 - 日志配置
```

### 日志管理器主类

```python
# log_manager.py

import rclpy
from rclpy.node import Node
import sqlite3
import threading
import queue
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from rcl_interfaces.msg import Log
from std_msgs.msg import String

class HybridLogManager:
    """混合日志管理器 - 统一管理ROS2日志和业务日志"""
    
    def __init__(self, node: Node, db_path: str = "libbot.db"):
        """初始化混合日志管理器
        
        Args:
            node: ROS2节点实例
            db_path: 数据库路径
        """
        self.node = node
        self.db_path = db_path
        self.is_running = False
        
        # 日志队列（异步处理）
        self.log_queue = queue.Queue(maxsize=10000)
        self.processing_thread = None
        
        # 日志处理器
        self.ros2_handler = None
        self.business_handler = None
        self.db_handler = None
        
        # 配置参数
        self.config = self._load_config()
        
        # 初始化处理器
        self._init_handlers()
        
    def _load_config(self) -> Dict:
        """加载日志配置"""
        # 默认配置
        default_config = {
            'ros2_log': {
                'enable': True,
                'levels': ['INFO', 'WARN', 'ERROR', 'FATAL'],
                'topics': ['/rosout', '/rosout_agg']
            },
            'business_log': {
                'enable': True,
                'levels': ['INFO', 'WARN', 'ERROR'],
                'categories': ['navigation', 'perception', 'task', 'system']
            },
            'database': {
                'enable': True,
                'batch_size': 100,
                'flush_interval': 5.0,  # 秒
                'retention_days': 30
            },
            'performance': {
                'async_processing': True,
                'queue_size': 10000,
                'write_timeout': 0.01  # 10ms
            }
        }
        
        # TODO: 从配置文件加载
        return default_config
        
    def _init_handlers(self):
        """初始化日志处理器"""
        from .log_handlers.ros2_log_handler import ROS2LogHandler
        from .log_handlers.business_log_handler import BusinessLogHandler
        from .log_handlers.database_handler import DatabaseLogHandler
        
        self.ros2_handler = ROS2LogHandler(self.node, self.config['ros2_log'])
        self.business_handler = BusinessLogHandler(self.node, self.config['business_log'])
        self.db_handler = DatabaseLogHandler(self.db_path, self.config['database'])
        
        # 设置处理器回调
        self.ros2_handler.set_log_callback(self._on_log_received)
        self.business_handler.set_log_callback(self._on_log_received)
        
    def start(self):
        """启动日志管理器"""
        if self.is_running:
            return
            
        self.is_running = True
        
        # 启动数据库处理器
        self.db_handler.initialize_database()
        
        # 启动日志处理器
        if self.config['ros2_log']['enable']:
            self.ros2_handler.start()
            
        if self.config['business_log']['enable']:
            self.business_handler.start()
            
        # 启动异步处理线程
        if self.config['performance']['async_processing']:
            self.processing_thread = threading.Thread(
                target=self._log_processing_loop,
                daemon=True
            )
            self.processing_thread.start()
            
        self.node.get_logger().info("混合日志管理器启动")
        
    def stop(self):
        """停止日志管理器"""
        self.is_running = False
        
        # 停止处理器
        if self.ros2_handler:
            self.ros2_handler.stop()
        if self.business_handler:
            self.business_handler.stop()
            
        # 等待处理线程结束
        if self.processing_thread:
            self.processing_thread.join(timeout=2.0)
            
        # 确保所有日志写入完成
        self._flush_all_logs()
        
        self.node.get_logger().info("混合日志管理器停止")
        
    def _on_log_received(self, log_entry: Dict):
        """日志接收回调
        
        Args:
            log_entry: 日志条目
        """
        try:
            # 添加到处理队列
            if self.config['performance']['async_processing']:
                self.log_queue.put_nowait(log_entry)
            else:
                # 同步处理
                self._process_log_entry(log_entry)
                
        except queue.Full:
            self.node.get_logger().warn("日志队列已满，丢弃日志条目")
        except Exception as e:
            self.node.get_logger().error(f"日志接收错误: {str(e)}")
            
    def _log_processing_loop(self):
        """日志处理主循环"""
        batch_logs = []
        last_flush_time = time.time()
        flush_interval = self.config['database']['flush_interval']
        
        while self.is_running:
            try:
                # 从队列获取日志
                try:
                    log_entry = self.log_queue.get(timeout=0.1)
                    batch_logs.append(log_entry)
                except queue.Empty:
                    pass
                    
                current_time = time.time()
                
                # 检查是否需要刷新
                should_flush = (
                    len(batch_logs) >= self.config['database']['batch_size'] or
                    (current_time - last_flush_time) >= flush_interval
                )
                
                if should_flush and batch_logs:
                    self._flush_log_batch(batch_logs)
                    batch_logs.clear()
                    last_flush_time = current_time
                    
            except Exception as e:
                self.node.get_logger().error(f"日志处理循环错误: {str(e)}")
                time.sleep(0.1)
                
        # 退出前刷新剩余日志
        if batch_logs:
            self._flush_log_batch(batch_logs)
            
    def _process_log_entry(self, log_entry: Dict):
        """处理单个日志条目"""
        try:
            # 写入数据库
            if self.config['database']['enable']:
                self.db_handler.write_log(log_entry)
                
        except Exception as e:
            self.node.get_logger().error(f"处理日志条目错误: {str(e)}")
            
    def _flush_log_batch(self, log_batch: List[Dict]):
        """批量刷新日志到数据库"""
        try:
            if self.config['database']['enable']:
                self.db_handler.write_log_batch(log_batch)
                
        except Exception as e:
            self.node.get_logger().error(f"批量刷新日志错误: {str(e)}")
            
    def _flush_all_logs(self):
        """强制刷新所有待处理日志"""
        remaining_logs = []
        
        # 获取队列中剩余的所有日志
        while not self.log_queue.empty():
            try:
                log_entry = self.log_queue.get_nowait()
                remaining_logs.append(log_entry)
            except queue.Empty:
                break
                
        if remaining_logs:
            self._flush_log_batch(remaining_logs)
            
    def log_business(self, level: str, category: str, message: str, 
                     metadata: Optional[Dict] = None):
        """记录业务日志
        
        Args:
            level: 日志级别 (INFO/WARN/ERROR)
            category: 日志分类
            message: 日志消息
            metadata: 附加元数据
        """
        log_entry = {
            'timestamp': time.time(),
            'level': level,
            'category': category,
            'message': message,
            'metadata': metadata or {},
            'source': 'business'
        }
        
        self._on_log_received(log_entry)
        
    def query_logs(self, start_time: Optional[float] = None, 
                  end_time: Optional[float] = None,
                  level: Optional[str] = None,
                  category: Optional[str] = None,
                  limit: int = 100) -> List[Dict]:
        """查询日志
        
        Args:
            start_time: 开始时间戳
            end_time: 结束时间戳
            level: 日志级别过滤
            category: 日志分类过滤
            limit: 返回结果数量限制
            
        Returns:
            日志条目列表
        """
        try:
            return self.db_handler.query_logs(
                start_time, end_time, level, category, limit
            )
        except Exception as e:
            self.node.get_logger().error(f"查询日志错误: {str(e)}")
            return []
            
    def cleanup_old_logs(self):
        """清理过期日志"""
        try:
            retention_days = self.config['database']['retention_days']
            cutoff_time = time.time() - (retention_days * 24 * 3600)
            
            self.db_handler.delete_logs_before(cutoff_time)
            
            self.node.get_logger().info(
                f"清理了 {retention_days} 天前的日志"
            )
            
        except Exception as e:
            self.node.get_logger().error(f"清理日志错误: {str(e)}")
            
    def get_log_statistics(self) -> Dict:
        """获取日志统计信息"""
        try:
            return self.db_handler.get_statistics()
        except Exception as e:
            self.node.get_logger().error(f"获取日志统计错误: {str(e)}")
            return {}
```

### ROS2日志处理器

```python
# log_handlers/ros2_log_handler.py

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import Log
from typing import Callable, Dict, List
import time

class ROS2LogHandler:
    """ROS2日志处理器 - 捕获和处理ROS2系统日志"""
    
    def __init__(self, node: Node, config: Dict):
        """初始化ROS2日志处理器
        
        Args:
            node: ROS2节点实例
            config: 配置参数
        """
        self.node = node
        self.config = config
        self.log_callback = None
        self.subscribers = {}
        self.is_running = False
        
    def set_log_callback(self, callback: Callable):
        """设置日志回调函数"""
        self.log_callback = callback
        
    def start(self):
        """启动ROS2日志处理"""
        if self.is_running:
            return
            
        self.is_running = True
        
        # 订阅配置的Topic
        for topic in self.config['topics']:
            if topic == '/rosout':
                sub = self.node.create_subscription(
                    Log,
                    topic,
                    self._rosout_callback,
                    100  # 高队列大小
                )
                self.subscribers[topic] = sub
                
            elif topic == '/rosout_agg':
                sub = self.node.create_subscription(
                    Log,
                    topic,
                    self._rosout_callback,
                    100
                )
                self.subscribers[topic] = sub
                
        self.node.get_logger().info(
            f"ROS2日志处理器启动，订阅了 {len(self.subscribers)} 个Topic"
        )
        
    def stop(self):
        """停止ROS2日志处理"""
        self.is_running = False
        
        # 销毁所有订阅者
        for topic, sub in self.subscribers.items():
            self.node.destroy_subscription(sub)
            
        self.subscribers.clear()
        
        self.node.get_logger().info("ROS2日志处理器停止")
        
    def _rosout_callback(self, msg: Log):
        """ROS2日志消息回调"""
        try:
            # 过滤日志级别
            if not self._should_process_level(msg.level):
                return
                
            # 转换日志级别
            level_str = self._ros_level_to_string(msg.level)
            
            # 构建日志条目
            log_entry = {
                'timestamp': time.time(),
                'level': level_str,
                'category': 'ros2_system',
                'message': msg.msg,
                'metadata': {
                    'node_name': msg.name,
                    'file': msg.file,
                    'function': msg.function,
                    'line': msg.line,
                    'topic': msg.topic if hasattr(msg, 'topic') else '',
                    'ros_timestamp': msg.stamp.sec + msg.stamp.nanosec * 1e-9
                },
                'source': 'ros2'
            }
            
            # 调用回调
            if self.log_callback:
                self.log_callback(log_entry)
                
        except Exception as e:
            self.node.get_logger().error(f"处理ROS2日志错误: {str(e)}")
            
    def _should_process_level(self, level: int) -> bool:
        """检查是否应该处理该级别的日志"""
        level_names = {
            1: 'DEBUG',
            2: 'INFO', 
            4: 'WARN',
            8: 'ERROR',
            16: 'FATAL'
        }
        
        level_str = level_names.get(level, 'UNKNOWN')
        return level_str in self.config['levels']
        
    def _ros_level_to_string(self, level: int) -> str:
        """将ROS2日志级别转换为字符串"""
        level_names = {
            1: 'DEBUG',
            2: 'INFO',
            4: 'WARN', 
            8: 'ERROR',
            16: 'FATAL'
        }
        return level_names.get(level, 'UNKNOWN')
```

### 配置文件

```yaml
# config/logging_config.yaml

logging:
  # ROS2日志配置
  ros2_log:
    enable: true
    levels: 
      - "INFO"
      - "WARN" 
      - "ERROR"
      - "FATAL"
    topics:
      - "/rosout"
      - "/rosout_agg"
    
  # 业务日志配置
  business_log:
    enable: true
    levels:
      - "INFO"
      - "WARN"
      - "ERROR"
    categories:
      - "navigation"
      - "perception"
      - "task"
      - "system"
      - "database"
      - "ui"
      
  # 数据库配置
  database:
    enable: true
    batch_size: 100
    flush_interval: 5.0
    retention_days: 30
    
    # 表结构
    tables:
      system_logs:
        - id INTEGER PRIMARY KEY AUTOINCREMENT
        - timestamp REAL NOT NULL
        - level TEXT NOT NULL
        - category TEXT NOT NULL
        - message TEXT NOT NULL
        - metadata TEXT
        - source TEXT NOT NULL
        
      log_statistics:
        - date TEXT PRIMARY KEY
        - info_count INTEGER DEFAULT 0
        - warn_count INTEGER DEFAULT 0
        - error_count INTEGER DEFAULT 0
        - fatal_count INTEGER DEFAULT 0
        
  # 性能配置
  performance:
    async_processing: true
    queue_size: 10000
    write_timeout: 0.01
    
  # 轮转配置
  rotation:
    enable: true
    max_file_size: 104857600  # 100MB
    backup_count: 5
    compress_old_files: true

# ROS2参数声明
/**:
  ros__parameters:
    logging.ros2_log.enable: true
    logging.ros2_log.levels: ["INFO", "WARN", "ERROR", "FATAL"]
    logging.business_log.enable: true
    logging.business_log.categories: ["navigation", "perception", "task", "system"]
    logging.database.batch_size: 100
    logging.database.flush_interval: 5.0
    logging.database.retention_days: 30
    logging.performance.async_processing: true
    logging.performance.queue_size: 10000
```

---

## ✅ 完成检查清单

- [ ] HybridLogManager类实现并测试
- [ ] ROS2日志处理器正常工作
- [ ] 业务日志处理器正常工作
- [ ] 数据库日志处理器正常工作
- [ ] 配置文件参数合理
- [ ] 异步日志处理性能达标
- [ ] 日志查询功能正常
- [ ] 日志轮转机制正确
- [ ] 错误处理和恢复机制
- [ ] 手动测试日志记录和查询

---

## 🔍 测试场景

### 测试1: ROS2日志捕获
1. 启动ROS2节点并生成各种级别日志
2. 验证日志被捕获并存储
3. 验证日志级别过滤正确

### 测试2: 业务日志记录
1. 调用业务日志接口记录不同类别日志
2. 验证日志正确写入数据库
3. 验证元数据保存完整

### 测试3: 异步处理性能
1. 模拟高频率日志写入
2. 验证队列处理不阻塞
3. 验证批量写入性能

### 测试4: 日志查询功能
1. 插入测试日志数据
2. 测试各种查询条件
3. 验证查询结果正确

---

## 📚 相关文档

- [Story 3-2: 系统健康指标监控实现](./3-2-health-monitoring.md) - 健康监控
- [Story 3-3: UI日志面板实现](./3-3-log-panel-ui.md) - UI日志显示
- [Story 3-4: 日志存储与轮转实现](./3-4-log-rotation.md) - 日志轮转
- [docs/design_brainstorm_detailed.md#D3章节] - 日志系统详细设计

---

## 💡 实现提示

1. **性能优化**: 使用异步处理和批量写入提高性能
2. **可靠性**: 确保日志不会丢失，队列满时适当处理
3. **查询效率**: 为常用查询字段建立数据库索引
4. **存储空间**: 定期清理过期日志，避免数据库过大
5. **错误隔离**: 日志系统错误不应影响主系统运行

---
