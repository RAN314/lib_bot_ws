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
src/libbot_logging/libbot_logging/
├── hybrid_logger.py              # 新建 - 混合日志管理器
├── ros2_logger.py               # 新建 - ROS2系统日志处理
├── sqlite_logger.py             # 新建 - SQLite业务日志存储
├── log_buffer.py                # 新建 - 日志缓冲区管理
├── query_interface.py           # 新建 - 日志查询接口
└── config/
    └── logging_config.yaml      # 新建 - 日志配置
```

### 核心组件设计

#### **1. HybridLogger - 混合日志管理器**
```python
# hybrid_logger.py

import time
import threading
import json
from typing import Dict, List, Optional
from datetime import datetime
import logging

class HybridLogger:
    """混合日志管理器 - 统一管理ROS2和SQLite日志"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.ros2_logger = ROS2Logger(config.get('ros2', {}))
        self.sqlite_logger = SQLiteLogger(config.get('sqlite', {}))
        self.log_buffer = LogBuffer(config.get('buffer', {}))
        
    def log_system(self, level: str, message: str, component: str = None):
        """系统日志记录"""
        # ROS2日志 + 缓冲区
        self.ros2_logger.log(level, message, component)
        self.log_buffer.add_log('system', level, message, component)
        
    def log_business(self, operation: str, details: dict, result: str = "success"):
        """业务日志记录"""
        # SQLite日志 + 缓冲区
        self.sqlite_logger.log_operation(operation, details, result)
        self.log_buffer.add_log('business', operation, str(details), result)
        
    def query_logs(self, filters: dict) -> List[dict]:
        """查询日志"""
        return self.sqlite_logger.query_logs(filters)
```

#### **2. ROS2Logger - ROS2系统日志处理**
```python
# ros2_logger.py

class ROS2Logger:
    """ROS2系统日志处理器"""
    
    def __init__(self, config: Dict):
        self.node = None  # ROS2节点引用
        self.log_levels = config.get('levels', ['DEBUG', 'INFO', 'WARN', 'ERROR'])
        
    def log(self, level: str, message: str, component: str = None):
        """ROS2日志记录"""
        if self.node:
            formatted_msg = f"[{component}] {message}" if component else message
            
            if level == "DEBUG":
                self.node.get_logger().debug(formatted_msg)
            elif level == "INFO":
                self.node.get_logger().info(formatted_msg)
            elif level == "WARN":
                self.node.get_logger().warn(formatted_msg)
            elif level == "ERROR":
                self.node.get_logger().error(formatted_msg)
```

#### **3. SQLiteLogger - SQLite业务日志存储**
```python
# sqlite_logger.py

import sqlite3
import json
import time
from typing import Dict, List

class SQLiteLogger:
    """SQLite业务日志管理器"""
    
    def __init__(self, config: Dict):
        self.db_path = config.get('database_path', 'library.db')
        self.init_database()
        
    def log_operation(self, operation_type: str, details: dict, result: str = "success"):
        """业务操作日志记录"""
        log_entry = {
            'timestamp': time.time(),
            'operation': operation_type,
            'details': json.dumps(details),
            'result': result,
            'component': self._get_component_name()
        }
        
        self._insert_log(log_entry)
        
    def query_logs(self, filters: dict) -> List[dict]:
        """多维度日志查询"""
        query = self._build_query(filters)
        return self._execute_query(query, filters)
        
    def _insert_log(self, log_entry: Dict):
        """插入日志到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO business_logs
            (timestamp, operation, details, result, component)
            VALUES (?, ?, ?, ?, ?)
        """, (
            log_entry['timestamp'],
            log_entry['operation'],
            log_entry['details'],
            log_entry['result'],
            log_entry['component']
        ))
        
        conn.commit()
        conn.close()
```

#### **4. LogBuffer - 日志缓冲区**
```python
# log_buffer.py

import threading
import time
from typing import Dict, List

class LogBuffer:
    """异步日志缓冲区 - 批量写入优化"""
    
    def __init__(self, config: Dict):
        self.buffer_size = config.get('buffer_size', 100)
        self.flush_interval = config.get('flush_interval', 5.0)
        self.write_buffer = []
        self.buffer_lock = threading.RLock()
        
    def add_log(self, log_type: str, level: str, message: str, component: str):
        """添加日志到缓冲区"""
        with self.buffer_lock:
            self.write_buffer.append({
                'type': log_type,
                'level': level,
                'message': message,
                'component': component,
                'timestamp': time.time()
            })
            
            # 检查是否需要立即写入
            if len(self.write_buffer) >= self.buffer_size:
                self._flush_buffer()
                
    def _flush_buffer(self):
        """批量写入数据库"""
        if not self.write_buffer:
            return
            
        # 批量写入实现
        self._batch_write_to_database(self.write_buffer)
        self.write_buffer.clear()
```

### ⚡ **性能特性**
- **处理能力**: ≥1000条日志/秒
- **写入延迟**: <10ms (P95)
- **缓冲区容量**: 10,000条
- **批量写入**: 100条/批次，5秒间隔
- **异步处理**: 非阻塞I/O操作

### 🔄 **工作流程**
```
其他ROS2节点
    ↓ (发布日志)
LogServerNode接收
    ↓ (标准化处理)
HybridLogger处理
    ├──→ ROS2Logger → /rosout话题
    ├──→ SQLiteLogger → 数据库存储
    └──→ LogBuffer → 批量写入
```

### 🛡️ **可靠性保障**
- **线程安全**: 所有操作都使用锁保护
- **错误恢复**: 写入失败自动重试
- **资源保护**: 内存和队列大小限制
- **数据完整性**: 事务性数据库操作

### 配置文件
```yaml
# config/logging_config.yaml

hybrid_logging:
  ros2:
    levels: ["INFO", "WARN", "ERROR"]
    enable_rosout: true

  sqlite:
    database_path: "library.db"
    batch_size: 100
    flush_interval: 5.0

  buffer:
    buffer_size: 10000
    flush_threshold: 100

  performance:
    async_processing: true
    compression_enabled: true

# ROS2参数声明
/**:
  ros__parameters:
    hybrid_logging.ros2.levels: ["INFO", "WARN", "ERROR"]
    hybrid_logging.sqlite.batch_size: 100
    hybrid_logging.buffer.buffer_size: 10000
    hybrid_logging.performance.async_processing: true
```

---

## ✅ 完成检查清单

- [ ] HybridLogger类实现并测试
- [ ] ROS2Logger类正常工作
- [ ] SQLiteLogger类正常工作
- [ ] LogBuffer异步处理正常
- [ ] 查询接口功能完整
- [ ] 配置文件参数合理
- [ ] 性能测试达标
- [ ] 错误处理机制完善
- [ ] 与LogServerNode集成正常
- [ ] 数据库表结构正确

---

## 🔍 测试场景

### 测试1: 混合日志记录
1. 同时记录ROS2系统日志和业务日志
2. 验证双引擎正常工作
3. 验证日志分类正确

### 测试2: 性能基准测试
1. 模拟1000条/秒写入压力
2. 验证延迟<10ms
3. 测试缓冲区溢出处理

### 测试3: 查询功能测试
1. 插入大量测试数据
2. 测试多维度查询
3. 验证查询响应时间<100ms

### 测试4: 集成测试
1. 与LogServerNode集成
2. 验证日志流转正确
3. 测试异常情况处理

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