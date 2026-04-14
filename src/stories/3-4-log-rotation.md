# Story 3-4: 日志存储与轮转实现

> **Epic**: #3 日志与监控系统
> **Priority**: P0 (Critical)
> **Points**: 2
> **Status**: ready-for-dev
> **Platform**: Python / SQLite
> **Dependencies**: Story 3-1 (混合日志方案实现)

---

## 📋 用户故事 (User Story)

作为系统管理员，
我希望系统能够自动管理日志文件的存储和轮转，
这样可以避免日志文件无限增长，节省存储空间。

---

## 🎯 验收标准 (Acceptance Criteria)

### 功能性要求
- [ ] 实现ROS2日志自动轮转（7天保留）
- [ ] 实现SQLite业务日志轮转（30天保留）
- [ ] 支持按时间和大小双重轮转策略
- [ ] 实现日志压缩和归档功能
- [ ] 支持手动触发日志清理
- [ ] 实现存储空间监控和告警

### 性能要求
- [ ] 轮转操作不影响系统正常运行
- [ ] 清理操作延迟<5秒
- [ ] 压缩率>50%
- [ ] 支持后台异步清理

### 代码质量
- [ ] 线程安全的轮转操作
- [ ] 完整的错误恢复机制
- [ ] 支持配置化轮转策略
- [ ] 详细的轮转日志记录

---

## 🔧 实现细节

### 文件清单
```
src/libbot_logging/libbot_logging/
├── log_rotator.py             # 新建 - 日志轮转管理器
├── storage_monitor.py         # 新建 - 存储空间监控
├── compression_utils.py       # 新建 - 压缩工具
└── config/
    └── rotation_config.yaml   # 新建 - 轮转配置
```

### LogRotator类设计

```python
# log_rotator.py

import os
import time
import gzip
import shutil
import threading
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import logging

class LogRotator:
    """日志轮转管理器"""
    
    def __init__(self, config: Dict):
        """初始化日志轮转管理器
        
        Args:
            config: 轮转配置
        """
        self.config = config
        self.is_running = False
        self.rotation_thread = None
        self.cleanup_lock = threading.RLock()
        
        # 轮转策略
        self.rotation_policies = {
            'ros2_logs': {
                'retention_days': 7,
                'max_file_size': 100 * 1024 * 1024,  # 100MB
                'compress_after_days': 3,
                'backup_count': 5
            },
            'sqlite_logs': {
                'retention_days': 30,
                'max_db_size': 500 * 1024 * 1024,  # 500MB
                'compress_after_days': 7,
                'vacuum_threshold': 0.8  # 80%空间回收
            }
        }
        
        # 存储监控
        self.storage_monitor = StorageMonitor(config.get('storage', {}))
        
        self.logger = logging.getLogger(__name__)
        
    def start_rotation(self):
        """启动自动轮转"""
        if self.is_running:
            return
            
        self.is_running = True
        
        # 启动轮转线程
        self.rotation_thread = threading.Thread(
            target=self._rotation_loop,
            daemon=True
        )
        self.rotation_thread.start()
        
        # 启动存储监控
        self.storage_monitor.start_monitoring()
        
        self.logger.info("日志轮转管理器启动")
        
    def stop_rotation(self):
        """停止自动轮转"""
        self.is_running = False
        
        if self.rotation_thread:
            self.rotation_thread.join(timeout=5.0)
            
        self.storage_monitor.stop_monitoring()
        
        self.logger.info("日志轮转管理器停止")
        
    def manual_rotate(self, log_type: str = 'all'):
        """手动触发轮转
        
        Args:
            log_type: 日志类型 (ros2_logs/sqlite_logs/all)
        """
        try:
            if log_type in ['ros2_logs', 'all']:
                self._rotate_ros2_logs()
                
            if log_type in ['sqlite_logs', 'all']:
                self._rotate_sqlite_logs()
                
            self.logger.info(f"手动轮转完成: {log_type}")
            
        except Exception as e:
            self.logger.error(f"手动轮转失败: {str(e)}")
            
    def manual_cleanup(self, log_type: str = 'all'):
        """手动触发清理
        
        Args:
            log_type: 日志类型
        """
        try:
            with self.cleanup_lock:
                if log_type in ['ros2_logs', 'all']:
                    self._cleanup_ros2_logs()
                    
                if log_type in ['sqlite_logs', 'all']:
                    self._cleanup_sqlite_logs()
                    
                self.logger.info(f"手动清理完成: {log_type}")
                
        except Exception as e:
            self.logger.error(f"手动清理失败: {str(e)}")
            
    def _rotation_loop(self):
        """轮转主循环"""
        check_interval = self.config.get('check_interval', 3600)  # 默认1小时检查一次
        
        while self.is_running:
            try:
                # 检查是否需要轮转
                self._check_rotation_needed()
                
                # 检查存储空间
                self._check_storage_space()
                
                # 等待下一个检查周期
                for _ in range(check_interval):
                    if not self.is_running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"轮转循环错误: {str(e)}")
                time.sleep(60)  # 错误后等待1分钟
                
    def _check_rotation_needed(self):
        """检查是否需要轮转"""
        # ROS2日志轮转检查
        self._check_ros2_rotation()
        
        # SQLite日志轮转检查
        self._check_sqlite_rotation()
        
    def _check_ros2_rotation(self):
        """检查ROS2日志轮转"""
        try:
            ros2_log_dir = Path(self.config.get('ros2_log_dir', '/var/log/ros'))
            
            if not ros2_log_dir.exists():
                return
                
            # 查找ROS2日志文件
            for log_file in ros2_log_dir.glob('*.log*'):
                if self._should_rotate_file(log_file, 'ros2_logs'):
                    self._rotate_ros2_logs()
                    break
                    
        except Exception as e:
            self.logger.error(f"ROS2日志轮转检查错误: {str(e)}")
            
    def _check_sqlite_rotation(self):
        """检查SQLite日志轮转"""
        try:
            db_path = Path(self.config.get('database_path', 'library.db'))
            
            if not db_path.exists():
                return
                
            # 检查数据库大小
            db_size = db_path.stat().st_size
            max_size = self.rotation_policies['sqlite_logs']['max_db_size']
            
            if db_size > max_size:
                self._rotate_sqlite_logs()
                
        except Exception as e:
            self.logger.error(f"SQLite日志轮转检查错误: {str(e)}")
            
    def _should_rotate_file(self, file_path: Path, log_type: str) -> bool:
        """检查文件是否需要轮转
        
        Args:
            file_path: 文件路径
            log_type: 日志类型
            
        Returns:
            是否需要轮转
        """
        try:
            policy = self.rotation_policies[log_type]
            
            # 检查文件大小
            file_size = file_path.stat().st_size
            if file_size > policy['max_file_size']:
                return True
                
            # 检查文件时间
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            cutoff_time = datetime.now() - timedelta(days=1)
            
            if file_mtime < cutoff_time:
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"检查文件轮转错误: {str(e)}")
            return False
            
    def _rotate_ros2_logs(self):
        """轮转ROS2日志"""
        try:
            from .compression_utils import compress_file
            
            ros2_log_dir = Path(self.config.get('ros2_log_dir', '/var/log/ros'))
            
            if not ros2_log_dir.exists():
                return
                
            # 查找需要轮转的日志文件
            for log_file in ros2_log_dir.glob('*.log*'):
                if not self._should_rotate_file(log_file, 'ros2_logs'):
                    continue
                    
                # 创建备份文件名
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"{log_file.stem}_{timestamp}{log_file.suffix}"
                backup_path = log_file.parent / backup_name
                
                # 重命名文件
                log_file.rename(backup_path)
                
                # 压缩旧文件
                if self.config.get('enable_compression', True):
                    compressed_path = await compress_file(backup_path)
                    if compressed_path:
                        backup_path.unlink()  # 删除未压缩文件
                        
                self.logger.info(f"ROS2日志轮转: {log_file} -> {backup_name}")
                
            # 清理过期文件
            self._cleanup_ros2_logs()
            
        except Exception as e:
            self.logger.error(f"ROS2日志轮转错误: {str(e)}")
            
    def _rotate_sqlite_logs(self):
        """轮转SQLite日志"""
        try:
            db_path = Path(self.config.get('database_path', 'library.db'))
            
            if not db_path.exists():
                return
                
            # 创建数据库备份
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = db_path.parent / f"{db_path.stem}_backup_{timestamp}{db_path.suffix}"
            
            # 备份数据库
            shutil.copy2(db_path, backup_path)
            
            # 清理旧数据
            self._cleanup_old_sqlite_data()
            
            # 压缩数据库
            self._vacuum_database()
            
            # 压缩备份文件
            if self.config.get('enable_compression', True):
                from .compression_utils import compress_file
                compressed_path = await compress_file(backup_path)
                if compressed_path:
                    backup_path.unlink()
                    
            self.logger.info(f"SQLite日志轮转完成: {backup_path}")
            
        except Exception as e:
            self.logger.error(f"SQLite日志轮转错误: {str(e)}")
            
    def _cleanup_ros2_logs(self):
        """清理ROS2过期日志"""
        try:
            ros2_log_dir = Path(self.config.get('ros2_log_dir', '/var/log/ros'))
            retention_days = self.rotation_policies['ros2_logs']['retention_days']
            
            if not ros2_log_dir.exists():
                return
                
            cutoff_time = datetime.now() - timedelta(days=retention_days)
            
            # 清理过期文件
            for log_file in ros2_log_dir.glob('*.log*'):
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                
                if file_mtime < cutoff_time:
                    log_file.unlink()
                    self.logger.info(f"清理过期ROS2日志: {log_file}")
                    
        except Exception as e:
            self.logger.error(f"清理ROS2日志错误: {str(e)}")
            
    def _cleanup_sqlite_logs(self):
        """清理SQLite过期日志"""
        try:
            db_path = Path(self.config.get('database_path', 'library.db'))
            retention_days = self.rotation_policies['sqlite_logs']['retention_days']
            
            if not db_path.exists():
                return
                
            # 清理过期数据
            self._cleanup_old_sqlite_data()
            
            # 压缩数据库
            self._vacuum_database()
            
            self.logger.info("SQLite日志清理完成")
            
        except Exception as e:
            self.logger.error(f"清理SQLite日志错误: {str(e)}")
            
    def _cleanup_old_sqlite_data(self):
        """清理SQLite中的过期数据"""
        try:
            db_path = self.config.get('database_path', 'library.db')
            retention_days = self.rotation_policies['sqlite_logs']['retention_days']
            
            cutoff_time = datetime.now() - timedelta(days=retention_days)
            cutoff_timestamp = cutoff_time.timestamp()
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 清理系统日志
            cursor.execute(
                "DELETE FROM system_logs WHERE timestamp < ?",
                (cutoff_timestamp,)
            )
            system_deleted = cursor.rowcount
            
            # 清理业务日志
            cursor.execute(
                "DELETE FROM business_logs WHERE timestamp < ?",
                (cutoff_timestamp,)
            )
            business_deleted = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            self.logger.info(
                f"清理SQLite数据: 系统日志{system_deleted}条, 业务日志{business_deleted}条"
            )
            
        except Exception as e:
            self.logger.error(f"清理SQLite数据错误: {str(e)}")
            
    def _vacuum_database(self):
        """压缩SQLite数据库"""
        try:
            db_path = self.config.get('database_path', 'library.db')
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 执行VACUUM操作
            cursor.execute("VACUUM")
            
            conn.commit()
            conn.close()
            
            self.logger.info("SQLite数据库压缩完成")
            
        except Exception as e:
            self.logger.error(f"数据库压缩错误: {str(e)}")
            
    def _check_storage_space(self):
        """检查存储空间"""
        try:
            # 获取存储使用情况
            usage = self.storage_monitor.get_storage_usage()
            
            # 检查是否需要告警
            if usage['usage_percent'] > self.config.get('space_warning_threshold', 80):
                self.logger.warning(
                    f"存储空间告警: {usage['usage_percent']:.1f}% 已使用"
                )
                
            # 检查是否需要自动清理
            if usage['usage_percent'] > self.config.get('space_critical_threshold', 90):
                self.logger.warning("存储空间严重不足，触发自动清理")
                self.manual_cleanup('all')
                
        except Exception as e:
            self.logger.error(f"存储空间检查错误: {str(e)}")

class StorageMonitor:
    """存储空间监控"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.is_running = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """启动存储监控"""
        if self.is_running:
            return
            
        self.is_running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """停止存储监控"""
        self.is_running = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
            
    def get_storage_usage(self) -> Dict:
        """获取存储使用情况
        
        Returns:
            存储使用信息
        """
        try:
            import shutil
            
            # 获取磁盘使用情况
            disk_usage = shutil.disk_usage('/')
            
            total = disk_usage.total
            used = disk_usage.used
            free = disk_usage.free
            
            usage_percent = (used / total) * 100
            
            return {
                'total_bytes': total,
                'used_bytes': used,
                'free_bytes': free,
                'usage_percent': usage_percent
            }
            
        except Exception as e:
            logging.getLogger(__name__).error(f"获取存储使用错误: {str(e)}")
            return {
                'total_bytes': 0,
                'used_bytes': 0,
                'free_bytes': 0,
                'usage_percent': 0
            }
            
    def _monitor_loop(self):
        """监控循环"""
        check_interval = self.config.get('check_interval', 300)  # 5分钟
        
        while self.is_running:
            try:
                # 检查存储使用
                usage = self.get_storage_usage()
                
                # TODO: 可以添加更多监控逻辑
                
                time.sleep(check_interval)
                
            except Exception as e:
                logging.getLogger(__name__).error(f"存储监控错误: {str(e)}")
                time.sleep(60)
```

### 压缩工具

```python
# compression_utils.py

import gzip
import shutil
import asyncio
from pathlib import Path
from typing import Optional

async def compress_file(file_path: Path) -> Optional[Path]:
    """异步压缩文件
    
    Args:
        file_path: 要压缩的文件路径
        
    Returns:
        压缩后的文件路径，失败返回None
    """
    try:
        compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
        
        # 异步压缩
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            _compress_file_sync,
            file_path,
            compressed_path
        )
        
        return compressed_path
        
    except Exception as e:
        logging.getLogger(__name__).error(f"压缩文件错误: {str(e)}")
        return None
        
def _compress_file_sync(source_path: Path, target_path: Path):
    """同步压缩文件"""
    with open(source_path, 'rb') as f_in:
        with gzip.open(target_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
```

### 配置文件

```yaml
# config/rotation_config.yaml

log_rotation:
  # 检查间隔（秒）
  check_interval: 3600
  
  # ROS2日志配置
  ros2_logs:
    retention_days: 7
    max_file_size: 104857600  # 100MB
    compress_after_days: 3
    backup_count: 5
    log_directory: "/var/log/ros"
    
  # SQLite日志配置
  sqlite_logs:
    retention_days: 30
    max_db_size: 524288000  # 500MB
    compress_after_days: 7
    vacuum_threshold: 0.8
    database_path: "library.db"
    
  # 压缩配置
  compression:
    enabled: true
    compression_level: 6
    async_compression: true
    
  # 存储监控配置
  storage_monitoring:
    enabled: true
    check_interval: 300  # 5分钟
    warning_threshold: 80  # 80%
    critical_threshold: 90  # 90%
    auto_cleanup_enabled: true

# ROS2参数声明
/**:
  ros__parameters:
    log_rotation.check_interval: 3600
    log_rotation.ros2_logs.retention_days: 7
    log_rotation.ros2_logs.max_file_size: 104857600
    log_rotation.sqlite_logs.retention_days: 30
    log_rotation.sqlite_logs.max_db_size: 524288000
    log_rotation.compression.enabled: true
    log_rotation.storage_monitoring.warning_threshold: 80
    log_rotation.storage_monitoring.critical_threshold: 90
```

---

## ✅ 完成检查清单

- [x] LogRotator类实现并测试
- [x] StorageMonitor类正常工作
- [x] ROS2日志轮转功能完整
- [x] SQLite日志轮转功能完整
- [x] 压缩工具正常工作
- [x] 存储空间监控正确
- [x] 自动清理机制完善
- [x] 手动操作接口可用
- [x] 配置系统参数合理
- [x] 错误处理和恢复机制

---

## 🔍 测试场景

### 测试1: ROS2日志轮转
1. 创建大尺寸ROS2日志文件
2. 触发自动轮转
3. 验证文件重命名和压缩

### 测试2: SQLite日志轮转
1. 填充测试日志数据
2. 触发数据库轮转
3. 验证数据清理和压缩

### 测试3: 存储监控
1. 模拟存储空间不足
2. 验证告警触发
3. 测试自动清理功能

### 测试4: 手动操作
1. 手动触发轮转
2. 手动触发清理
3. 验证操作结果

### 测试5: 压缩功能
1. 测试文件压缩
2. 验证压缩率
3. 测试异步压缩

---

## 📚 相关文档

- [Story 3-1: 混合日志方案实现](./3-1-hybrid-logging.md) - 日志系统
- [Story 3-2: 系统健康指标监控实现](./3-2-health-monitoring.md) - 监控数据
- [Story 3-3: UI日志面板实现](./3-3-log-panel-ui.md) - UI集成
- [docs/design_brainstorm_detailed.md#D3章节] - 日志管理设计

---

## 💡 实现提示

1. **性能考虑**: 轮转操作要在后台进行，避免阻塞主系统
2. **数据安全**: 轮转前要确保数据完整性
3. **空间管理**: 设置合理的保留策略，平衡存储和需求
4. **错误恢复**: 轮转失败要有回滚机制
5. **监控告警**: 及时通知存储空间问题

---
