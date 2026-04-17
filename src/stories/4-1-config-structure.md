# Story 4-1: YAML配置文件结构实现

> **Epic**: #4 配置管理系统
> **Priority**: P0 (Critical)
> **Points**: 3
> **Status**: ready-for-dev
> **Platform**: ROS2 / Python / YAML
> **Dependencies**: Story 5-4 (libbot_msgs消息包实现)

---

## 📋 用户故事 (User Story)

作为系统管理员，
我希望系统使用统一的YAML配置文件格式，
这样可以方便地管理和维护系统参数。

---

## 🎯 验收标准 (Acceptance Criteria)

### 功能性要求
- [ ] 实现主配置文件library_config.yaml
- [ ] 支持7大模块配置（导航、感知、任务等）
- [ ] 实现配置参数验证
- [ ] 支持配置热重载
- [ ] 实现配置版本管理
- [ ] 支持环境特定配置覆盖

### 性能要求
- [ ] 配置加载时间<100ms
- [ ] 热重载不影响系统运行
- [ ] 配置验证时间<50ms

### 代码质量
- [ ] 配置schema验证
- [ ] 详细的配置文档
- [ ] 向后兼容性

---

## 🔧 实现细节

### 文件清单
```
library_config/
├── library_config.yaml          # 新建 - 主配置文件
├── config_dev.yaml             # 新建 - 开发环境配置
├── config_test.yaml            # 新建 - 测试环境配置  
├── config_demo.yaml            # 新建 - 演示环境配置
└── config_schema.yaml          # 新建 - 配置schema定义

src/libbot_tasks/libbot_tasks/
├── config_manager.py           # 新建 - 配置管理器
└── config_validator.py         # 新建 - 配置验证器
```

### 主配置文件结构

```yaml
# library_config.yaml

# 图书馆机器人系统主配置文件
version: "1.0.0"
environment: "development"  # development/test/demo

# 1. 导航配置
navigation:
  # 基本导航参数
  basic:
    max_velocity: 0.3              # 最大线速度(m/s)
    max_angular_velocity: 0.5      # 最大角速度(rad/s)
    acceleration_limit: 0.2        # 加速度限制
    
  # AMCL定位配置  
  localization:
    min_particles: 3000           # 最小粒子数
    max_particles: 8000           # 最大粒子数
    update_min_d: 0.2             # 更新最小位移
    update_min_a: 0.5             # 更新最小角度
    
  # DWB控制器配置
  controller:
    max_vel_x: 0.3                # 最大X速度
    min_vel_x: -0.15              # 最小X速度
    max_vel_theta: 0.5            # 最大旋转速度
    
  # 代价地图配置
  costmap:
    global:
      inflation_radius: 0.5       # 全局膨胀半径
      cost_scaling_factor: 3.0    # 代价缩放因子
    local:
      inflation_radius: 0.3       # 局部膨胀半径
      width: 3.0                  # 局部地图宽度
      height: 3.0                 # 局部地图高度

# 2. 感知配置
perception:
  # RFID配置
  rfid:
    detection_range: 0.5          # 检测范围(m)
    scan_rate: 10.0               # 扫描频率(Hz)
    false_negative_rate: 0.15     # 漏检率
    
    # 四向扫描配置
    directions:
      front:
        angle: 0.0                # 前向角度
        fov: 90.0                 # 视野角度
      back:
        angle: 180.0              # 后向角度
        fov: 90.0                 # 视野角度
      left:
        angle: 90.0               # 左向角度
        fov: 90.0                 # 视野角度
      right:
        angle: -90.0              # 右向角度
        fov: 90.0                 # 视野角度
  
  # 激光雷达配置
  lidar:
    range_min: 0.12               # 最小检测距离
    range_max: 3.5                # 最大检测距离
    angle_increment: 0.017        # 角度增量
    
  # 相机配置
  camera:
    resolution: "640x480"        # 分辨率
    fps: 30                       # 帧率
    fov: 60.0                     # 视野角度

# 3. 任务管理配置
task_management:
  # FindBook任务配置
  findbook:
    max_search_time: 300          # 最大搜索时间(秒)
    retry_attempts: 3            # 重试次数
    scan_duration: 10.0          # 扫描持续时间
    
  # Inventory任务配置
  inventory:
    scan_speed: 0.2              # 扫描速度(m/s)
    coverage_threshold: 0.95     # 覆盖率阈值
    
  # 任务队列配置
  queue:
    max_queue_size: 100          # 最大队列大小
    priority_levels: 3           # 优先级级别
    timeout_default: 600         # 默认超时(秒)

# 4. 数据库配置
database:
  # SQLite配置
  sqlite:
    path: "library.db"           # 数据库路径
    timeout: 30                   # 连接超时
    
  # 表结构配置
  schema:
    books_table: "books"
    inventory_table: "inventory_log"
    task_table: "task_queue"
    
  # 性能配置
  performance:
    cache_size: 2000             # 缓存大小
    synchronous: "NORMAL"        # 同步模式
    journal_mode: "WAL"          # 日志模式

# 5. 仿真配置
simulation:
  # Gazebo配置
  gazebo:
    update_rate: 1000            # 更新频率(Hz)
    real_time_factor: 1.0        # 实时因子
    
  # 环境配置
  environment:
    library_width: 15.0          # 图书馆宽度(m)
    library_length: 20.0         # 图书馆长度(m)
    aisle_width: 1.2             # 过道宽度(m)
    
  # 书架配置
  bookshelves:
    count: 24                    # 书架数量
    height: 2.0                  # 书架高度(m)
    width: 1.0                   # 书架宽度(m)
    depth: 0.3                   # 书架深度(m)

# 6. UI配置
ui:
  # 主窗口配置
  main_window:
    width: 800                   # 窗口宽度
    height: 600                  # 窗口高度
    title: "图书馆机器人控制系统"
    
  # 刷新率配置
  refresh_rate: 10.0            # 刷新频率(Hz)
  
  # 日志显示配置
  logging:
    max_lines: 100               # 最大显示行数
    auto_scroll: true            # 自动滚动
    
  # 快捷键配置
  shortcuts:
    find_book: "Ctrl+N"          # 找书快捷键
    pause: "Space"               # 暂停快捷键
    cancel: "Esc"                # 取消快捷键

# 7. 系统配置
system:
  # 日志配置
  logging:
    level: "INFO"                # 日志级别
    file: "libbot.log"           # 日志文件
    max_size: 104857600          # 最大文件大小(100MB)
    
  # 性能配置
  performance:
    max_cpu_usage: 0.8           # 最大CPU使用率
    max_memory_usage: 1073741824 # 最大内存使用(1GB)
    
  # 安全配置
  safety:
    emergency_stop_distance: 0.3  # 紧急停止距离
    max_operating_time: 3600      # 最大运行时间(秒)
    auto_save_interval: 300       # 自动保存间隔(秒)

# 动态参数配置（可通过ROS2参数服务器修改）
dynamic_params:
  - navigation.basic.max_velocity
  - navigation.controller.max_vel_x
  - perception.rfid.scan_rate
  - task_management.findbook.max_search_time
  - ui.refresh_rate
  - system.performance.max_cpu_usage

# 环境特定配置覆盖
environments:
  development:
    logging:
      level: "DEBUG"
    simulation:
      real_time_factor: 0.5
      
  test:
    logging:
      level: "WARN"
    system:
      performance:
        max_cpu_usage: 0.6
        
  demo:
    logging:
      level: "INFO"
    ui:
      refresh_rate: 5.0
```

### 配置管理器

```python
# config_manager.py

import yaml
import os
import threading
from typing import Dict, Any, Optional
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.callback_groups import ReentrantCallbackGroup

class ConfigManager:
    """配置管理器 - 统一管理所有配置文件"""
    
    def __init__(self, node: Node, config_dir: str = "library_config"):
        """初始化配置管理器
        
        Args:
            node: ROS2节点实例
            config_dir: 配置文件目录
        """
        self.node = node
        self.config_dir = config_dir
        self.config_data = {}
        self.environment = "development"
        self.config_lock = threading.RLock()
        
        # 配置验证器
        self.validator = None
        
        # ROS2参数回调组
        self.callback_group = ReentrantCallbackGroup()
        
    def initialize(self, environment: str = "development") -> bool:
        """初始化配置管理器
        
        Args:
            environment: 环境名称
            
        Returns:
            bool: 初始化是否成功
        """
        try:
            self.environment = environment
            
            # 初始化验证器
            from .config_validator import ConfigValidator
            self.validator = ConfigValidator()
            
            # 加载配置文件
            if not self._load_configurations():
                return False
                
            # 验证配置
            if not self._validate_configurations():
                return False
                
            # 注册ROS2参数回调
            self._register_ros2_parameters()
            
            self.node.get_logger().info(
                f"配置管理器初始化完成 (环境: {environment})"
            )
            return True
            
        except Exception as e:
            self.node.get_logger().error(f"配置管理器初始化失败: {str(e)}")
            return False
            
    def _load_configurations(self) -> bool:
        """加载所有配置文件"""
        try:
            with self.config_lock:
                # 1. 加载主配置文件
                main_config = self._load_yaml_file("library_config.yaml")
                if not main_config:
                    return False
                    
                # 2. 加载环境特定配置
                env_config = self._load_yaml_file(f"config_{self.environment}.yaml")
                
                # 3. 合并配置
                self.config_data = self._merge_configs(main_config, env_config or {})
                
                # 4. 应用环境覆盖
                self._apply_environment_overrides()
                
                return True
                
        except Exception as e:
            self.node.get_logger().error(f"加载配置文件错误: {str(e)}")
            return False
            
    def _load_yaml_file(self, filename: str) -> Optional[Dict]:
        """加载单个YAML文件"""
        try:
            filepath = os.path.join(self.config_dir, filename)
            
            if not os.path.exists(filepath):
                self.node.get_logger().warn(f"配置文件不存在: {filepath}")
                return None
                
            with open(filepath, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            self.node.get_logger().debug(f"加载配置文件: {filename}")
            return config
            
        except Exception as e:
            self.node.get_logger().error(f"加载文件 {filename} 错误: {str(e)}")
            return None
            
    def _merge_configs(self, base_config: Dict, override_config: Dict) -> Dict:
        """深度合并配置字典"""
        def deep_merge(base, override):
            result = base.copy()
            
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
                    
            return result
            
        return deep_merge(base_config, override_config)
        
    def _apply_environment_overrides(self):
        """应用环境特定覆盖配置"""
        env_overrides = self.config_data.get('environments', {}).get(self.environment, {})
        
        if env_overrides:
            self.config_data = self._merge_configs(self.config_data, env_overrides)
            self.node.get_logger().info(
                f"应用了 {self.environment} 环境的配置覆盖"
            )
            
    def _validate_configurations(self) -> bool:
        """验证配置数据"""
        try:
            if not self.validator:
                return True
                
            is_valid, errors = self.validator.validate(self.config_data)
            
            if not is_valid:
                for error in errors:
                    self.node.get_logger().error(f"配置验证错误: {error}")
                return False
                
            self.node.get_logger().info("配置验证通过")
            return True
            
        except Exception as e:
            self.node.get_logger().error(f"配置验证错误: {str(e)}")
            return False
            
    def _register_ros2_parameters(self):
        """注册ROS2参数回调"""
        try:
            # 获取动态参数列表
            dynamic_params = self.config_data.get('dynamic_params', [])
            
            for param_path in dynamic_params:
                # 将参数路径转换为ROS2参数名
                param_name = param_path.replace('.', '_')
                
                # 获取参数值
                value = self.get_value_by_path(param_path)
                if value is None:
                    continue
                    
                # 设置ROS2参数
                param = Parameter(param_name, value)
                self.node.declare_parameter(param_name, value)
                
            self.node.get_logger().info(
                f"注册了 {len(dynamic_params)} 个ROS2动态参数"
            )
            
        except Exception as e:
            self.node.get_logger().error(f"注册ROS2参数错误: {str(e)}")
            
    def get_value_by_path(self, path: str, default=None) -> Any:
        """通过路径获取配置值
        
        Args:
            path: 配置路径 (如: "navigation.basic.max_velocity")
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        try:
            with self.config_lock:
                keys = path.split('.')
                value = self.config_data
                
                for key in keys:
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        return default
                        
                return value
                
        except Exception as e:
            self.node.get_logger().error(f"获取配置值错误: {str(e)}")
            return default
            
    def set_value_by_path(self, path: str, value: Any) -> bool:
        """通过路径设置配置值
        
        Args:
            path: 配置路径
            value: 新值
            
        Returns:
            bool: 设置是否成功
        """
        try:
            with self.config_lock:
                keys = path.split('.')
                config = self.config_data
                
                # 遍历到倒数第二个key
                for key in keys[:-1]:
                    if key not in config:
                        config[key] = {}
                    config = config[key]
                    
                # 设置值
                config[keys[-1]] = value
                
                # 如果是动态参数，更新ROS2参数
                if path in self.config_data.get('dynamic_params', []):
                    param_name = path.replace('.', '_')
                    self.node.set_parameter(Parameter(param_name, value))
                    
                return True
                
        except Exception as e:
            self.node.get_logger().error(f"设置配置值错误: {str(e)}")
            return False
            
    def reload_configuration(self) -> bool:
        """重新加载配置"""
        try:
            self.node.get_logger().info("重新加载配置文件...")
            
            # 重新加载配置
            if not self._load_configurations():
                return False
                
            # 重新验证
            if not self._validate_configurations():
                return False
                
            # 重新注册ROS2参数
            self._register_ros2_parameters()
            
            self.node.get_logger().info("配置重新加载完成")
            return True
            
        except Exception as e:
            self.node.get_logger().error(f"重新加载配置错误: {str(e)}")
            return False
            
    def get_config_snapshot(self) -> Dict:
        """获取配置快照"""
        with self.config_lock:
            return self.config_data.copy()
            
    def export_configuration(self, filepath: str) -> bool:
        """导出配置到文件"""
        try:
            with self.config_lock:
                with open(filepath, 'w', encoding='utf-8') as f:
                    yaml.dump(self.config_data, f, default_flow_style=False, allow_unicode=True)
                    
            self.node.get_logger().info(f"配置导出到: {filepath}")
            return True
            
        except Exception as e:
            self.node.get_logger().error(f"导出配置错误: {str(e)}")
            return False
            
    def get_section(self, section: str) -> Dict:
        """获取配置节
        
        Args:
            section: 配置节名称
            
        Returns:
            配置节数据
        """
        with self.config_lock:
            return self.config_data.get(section, {}).copy()
```

### 配置文件示例（开发环境）

```yaml
# config_dev.yaml

# 开发环境特定配置
version: "1.0.0"
environment: "development"

# 开发环境覆盖配置
system:
  logging:
    level: "DEBUG"
    file: "libbot_dev.log"
  
simulation:
  gazebo:
    real_time_factor: 0.5        # 降低仿真速度便于调试
    update_rate: 500             # 降低更新频率
    
ui:
  refresh_rate: 20.0            # 提高UI刷新率
  logging:
    max_lines: 200               # 增加日志显示行数
    
perception:
  rfid:
    false_negative_rate: 0.05    # 降低漏检率便于测试
    
# 开发调试配置
debug:
  enable_verbose_logging: true
  log_sensor_data: true
  simulate_perfect_detection: false
  record_test_data: true
```

---

## ✅ 完成检查清单

- [ ] 主配置文件library_config.yaml创建
- [ ] 环境特定配置文件创建
- [ ] ConfigManager类实现
- [ ] ConfigValidator类实现
- [ ] 配置schema验证
- [ ] ROS2参数集成
- [ ] 配置热重载功能
- [ ] 配置文件版本管理
- [ ] 手动测试配置加载和验证

---

## 🔍 测试场景

### 测试1: 配置文件加载
1. 加载主配置文件
2. 验证所有配置节正确加载
3. 验证环境覆盖生效

### 测试2: 配置验证
1. 修改配置文件制造错误
2. 验证配置验证器捕获错误
3. 验证系统拒绝加载错误配置

### 测试3: 动态参数更新
1. 通过ROS2参数服务器修改参数
2. 验证配置管理器同步更新
3. 验证参数变更生效

### 测试4: 热重载功能
1. 修改配置文件
2. 触发配置重载
3. 验证新配置生效且系统稳定

---

## 📚 相关文档

- [Story 4-2: 三环境配置实现](./4-2-multi-env-config.md) - 多环境配置
- [Story 4-3: 动态参数更新流程实现](./4-3-dynamic-params.md) - 动态参数
- [Story 4-4: 参数验证机制实现](./4-4-param-validation.md) - 参数验证
- [docs/design_brainstorm_detailed.md#D4章节] - 配置管理详细设计

---

## 💡 实现提示

1. **配置层次**: 主配置 → 环境配置 → 运行时覆盖
2. **验证优先**: 启动时验证所有配置，避免运行时错误
3. **向后兼容**: 新版本配置要兼容旧版本结构
4. **文档完整**: 每个配置项都要有清晰的文档说明
5. **默认值**: 提供合理的默认值，减少配置复杂度

---
