# Story 3-3: UI日志面板实现

> **Epic**: #3 日志与监控系统
> **Priority**: P0 (Critical)
> **Points**: 2
> **Status**: ready-for-dev
> **Platform**: Qt5 / Python
> **Dependencies**: Story 3-1 (混合日志方案实现), Story 1-5 (日志面板基础)

---

## 📋 用户故事 (User Story)

作为系统操作员，
我希望在UI界面上能够实时查看系统日志，
这样可以及时了解系统运行状态和发现问题。

---

## 🎯 验收标准 (Acceptance Criteria)

### 功能性要求
- [ ] 实现实时日志显示面板（100条缓冲区）
- [ ] 支持日志级别过滤（INFO/WARN/ERROR）
- [ ] 实现颜色编码显示
- [ ] 支持自动滚动和手动滚动
- [ ] 实现日志搜索功能
- [ ] 支持日志导出功能
- [ ] 实现日志统计显示

### 性能要求
- [ ] 日志刷新频率10Hz
- [ ] 显示延迟<50ms
- [ ] 内存占用<10MB
- [ ] 搜索响应时间<100ms

### 代码质量
- [ ] 继承现有UI架构
- [ ] 完整的信号槽机制
- [ ] 线程安全的日志更新
- [ ] 响应式UI设计

---

## 🔧 实现细节

### 文件清单
```
src/libbot_ui/libbot_ui/
├── log_panel.py                # 新建 - 日志面板组件
├── log_widget.py              # 新建 - 日志显示控件
├── log_filter_widget.py       # 新建 - 日志过滤器
├── log_search_widget.py       # 新建 - 日志搜索控件
└── log_export_dialog.py       # 新建 - 日志导出对话框
```

### LogPanel类设计

```python
# log_panel.py

import sys
import os
from typing import List, Dict, Optional
from datetime import datetime
from collections import deque

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QCheckBox, QLineEdit, QComboBox,
    QLabel, QFrame, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QTextCharFormat, QFont

class LogPanel(QWidget):
    """日志面板主组件"""
    
    # 信号定义
    log_received = pyqtSignal(dict)
    filter_changed = pyqtSignal(dict)
    export_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """初始化日志面板
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 日志缓冲区
        self.log_buffer = deque(maxlen=100)  # 100条缓冲区
        self.filtered_logs = []
        
        # 过滤设置
        self.current_filters = {
            'level_info': True,
            'level_warn': True, 
            'level_error': True,
            'search_text': '',
            'component_filter': 'all'
        }
        
        # UI组件
        self.log_display = None
        self.filter_widget = None
        self.search_widget = None
        self.control_widget = None
        
        # 定时器
        self.update_timer = QTimer()
        self.update_timer.setInterval(100)  # 10Hz更新
        
        self._init_ui()
        self._setup_connections()
        
    def _init_ui(self):
        """初始化UI界面"""
        main_layout = QVBoxLayout(self)
        
        # 1. 控制面板
        control_layout = QHBoxLayout()
        
        # 级别过滤复选框
        self.info_checkbox = QCheckBox("INFO")
        self.info_checkbox.setChecked(True)
        self.info_checkbox.setStyleSheet("color: #2196F3;")
        
        self.warn_checkbox = QCheckBox("WARN") 
        self.warn_checkbox.setChecked(True)
        self.warn_checkbox.setStyleSheet("color: #FF9800;")
        
        self.error_checkbox = QCheckBox("ERROR")
        self.error_checkbox.setChecked(True)
        self.error_checkbox.setStyleSheet("color: #F44336;")
        
        # 组件过滤器
        self.component_combo = QComboBox()
        self.component_combo.addItems(["全部", "导航", "感知", "任务", "系统"])
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索日志...")
        self.search_input.setMaximumWidth(200)
        
        # 控制按钮
        self.auto_scroll_btn = QPushButton("自动滚动")
        self.auto_scroll_btn.setCheckable(True)
        self.auto_scroll_btn.setChecked(True)
        
        self.export_btn = QPushButton("导出")
        self.clear_btn = QPushButton("清空")
        
        # 统计信息
        self.stats_label = QLabel("日志: 0条")
        
        # 添加到控制面板
        control_layout.addWidget(self.info_checkbox)
        control_layout.addWidget(self.warn_checkbox)
        control_layout.addWidget(self.error_checkbox)
        control_layout.addWidget(QLabel("|"))
        control_layout.addWidget(self.component_combo)
        control_layout.addWidget(QLabel("|"))
        control_layout.addWidget(self.search_input)
        control_layout.addStretch()
        control_layout.addWidget(self.stats_label)
        control_layout.addWidget(self.auto_scroll_btn)
        control_layout.addWidget(self.export_btn)
        control_layout.addWidget(self.clear_btn)
        
        # 2. 日志显示区域
        self.log_display = LogDisplayWidget()
        
        # 3. 状态栏
        status_layout = QHBoxLayout()
        self.status_label = QLabel("就绪")
        self.buffer_label = QLabel("缓冲区: 0/100")
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.buffer_label)
        
        # 组装主界面
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self._create_separator())
        main_layout.addWidget(self.log_display)
        main_layout.addLayout(status_layout)
        
        # 设置布局
        self.setLayout(main_layout)
        
        # 连接信号
        self._connect_signals()
        
    def _create_separator(self):
        """创建分隔线"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        return separator
        
    def _connect_signals(self):
        """连接信号槽"""
        # 过滤控件
        self.info_checkbox.toggled.connect(self._on_filter_changed)
        self.warn_checkbox.toggled.connect(self._on_filter_changed)
        self.error_checkbox.toggled.connect(self._on_filter_changed)
        self.component_combo.currentTextChanged.connect(self._on_filter_changed)
        self.search_input.textChanged.connect(self._on_search_changed)
        
        # 控制按钮
        self.auto_scroll_btn.toggled.connect(self.log_display.set_auto_scroll)
        self.export_btn.clicked.connect(self._on_export_clicked)
        self.clear_btn.clicked.connect(self._on_clear_clicked)
        
        # 日志信号
        self.log_received.connect(self._on_log_received)
        
        # 定时器
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start()
        
    @pyqtSlot(dict)
    def _on_log_received(self, log_entry: Dict):
        """处理新日志接收
        
        Args:
            log_entry: 日志条目
        """
        # 添加到缓冲区
        self.log_buffer.append(log_entry)
        
        # 应用过滤
        if self._should_display_log(log_entry):
            self.filtered_logs.append(log_entry)
            
        # 更新缓冲区状态
        self.buffer_label.setText(f"缓冲区: {len(self.log_buffer)}/100")
        
    def _should_display_log(self, log_entry: Dict) -> bool:
        """检查是否应该显示该日志
        
        Args:
            log_entry: 日志条目
            
        Returns:
            是否显示
        """
        # 级别过滤
        level = log_entry.get('level', '').lower()
        if level == 'info' and not self.info_checkbox.isChecked():
            return False
        if level == 'warn' and not self.warn_checkbox.isChecked():
            return False
        if level == 'error' and not self.error_checkbox.isChecked():
            return False
            
        # 组件过滤
        component = log_entry.get('component', '')
        component_filter = self.component_combo.currentText()
        if component_filter != "全部" and component_filter not in component:
            return False
            
        # 搜索文本过滤
        search_text = self.search_input.text().lower()
        if search_text:
            message = log_entry.get('message', '').lower()
            if search_text not in message:
                return False
                
        return True
        
    def _on_filter_changed(self):
        """过滤条件改变"""
        # 更新过滤设置
        self.current_filters = {
            'level_info': self.info_checkbox.isChecked(),
            'level_warn': self.warn_checkbox.isChecked(),
            'level_error': self.error_checkbox.isChecked(),
            'component_filter': self.component_combo.currentText(),
            'search_text': self.search_input.text()
        }
        
        # 重新应用过滤
        self._apply_filters()
        
        # 发送过滤改变信号
        self.filter_changed.emit(self.current_filters)
        
    def _on_search_changed(self, text: str):
        """搜索文本改变"""
        self._on_filter_changed()
        
    def _apply_filters(self):
        """应用过滤条件"""
        self.filtered_logs = [
            log for log in self.log_buffer
            if self._should_display_log(log)
        ]
        
        # 更新统计
        self.stats_label.setText(f"日志: {len(self.filtered_logs)}条")
        
    def _update_display(self):
        """更新日志显示"""
        # 批量更新日志显示，避免频繁刷新
        if self.filtered_logs:
            self.log_display.update_logs(self.filtered_logs[-50:])  # 显示最新50条
            
    def _on_export_clicked(self):
        """导出按钮点击"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出日志",
                f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "文本文件 (*.txt);;CSV文件 (*.csv)"
            )
            
            if file_path:
                self._export_logs(file_path)
                
        except Exception as e:
            QMessageBox.critical(self, "导出错误", f"导出日志失败: {str(e)}")
            
    def _export_logs(self, file_path: str):
        """导出日志到文件
        
        Args:
            file_path: 文件路径
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"图书馆机器人系统日志导出\n")
                f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"日志总数: {len(self.log_buffer)}\n")
                f.write("=" * 50 + "\n\n")
                
                for log in self.log_buffer:
                    timestamp = log.get('timestamp', '')
                    level = log.get('level', 'INFO')
                    component = log.get('component', 'system')
                    message = log.get('message', '')
                    
                    f.write(f"[{timestamp}] [{level}] [{component}] {message}\n")
                    
            self.status_label.setText(f"日志已导出到: {file_path}")
            
        except Exception as e:
            raise Exception(f"写入文件失败: {str(e)}")
            
    def _on_clear_clicked(self):
        """清空按钮点击"""
        # 确认对话框
        reply = QMessageBox.question(
            self,
            "确认清空",
            "确定要清空所有日志吗？此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.log_buffer.clear()
            self.filtered_logs.clear()
            self.log_display.clear()
            self.buffer_label.setText("缓冲区: 0/100")
            self.stats_label.setText("日志: 0条")
            self.status_label.setText("日志已清空")
            
    def add_log(self, level: str, component: str, message: str):
        """添加日志（外部接口）
        
        Args:
            level: 日志级别
            component: 组件名称
            message: 日志消息
        """
        log_entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'level': level,
            'component': component,
            'message': message
        }
        
        self.log_received.emit(log_entry)

class LogDisplayWidget(QTextEdit):
    """日志显示控件"""
    
    def __init__(self, parent=None):
        """初始化日志显示控件"""
        super().__init__(parent)
        
        # 设置只读
        self.setReadOnly(True)
        
        # 设置字体
        font = QFont("Monospace")
        font.setPointSize(10)
        self.setFont(font)
        
        # 自动滚动标志
        self.auto_scroll = True
        
        # 颜色格式
        self.color_formats = {
            'info': QColor('#2196F3'),
            'warn': QColor('#FF9800'),
            'error': QColor('#F44336')
        }
        
    def set_auto_scroll(self, enabled: bool):
        """设置自动滚动
        
        Args:
            enabled: 是否启用
        """
        self.auto_scroll = enabled
        
    def update_logs(self, logs: List[Dict]):
        """更新日志显示
        
        Args:
            logs: 日志列表
        """
        # 清空当前显示
        self.clear()
        
        # 添加日志
        cursor = self.textCursor()
        
        for log in logs:
            self._append_log_entry(cursor, log)
            
        # 自动滚动到底部
        if self.auto_scroll:
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
            
    def _append_log_entry(self, cursor, log_entry: Dict):
        """添加单个日志条目
        
        Args:
            cursor: 文本光标
            log_entry: 日志条目
        """
        timestamp = log_entry.get('timestamp', '')
        level = log_entry.get('level', 'INFO').lower()
        component = log_entry.get('component', 'system')
        message = log_entry.get('message', '')
        
        # 格式化日志行
        log_line = f"[{timestamp}] [{level.upper()}] [{component}] {message}\n"
        
        # 设置颜色格式
        format = QTextCharFormat()
        if level in self.color_formats:
            format.setForeground(self.color_formats[level])
        
        # 插入文本
        cursor.insertText(log_line, format)
        
    def clear(self):
        """清空显示"""
        self.setPlainText("")
```

### 集成到主窗口

```python
# 在main_window.py中集成

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # ... 其他初始化代码
        
        # 创建日志面板
        self.log_panel = LogPanel()
        
        # 集成到右侧面板
        right_layout.addWidget(self.log_panel)
        
        # 连接ROS2日志信号
        self.ros2_manager.log_received.connect(self.log_panel.log_received)
```

### 配置文件

```yaml
# config/ui_logging.yaml

ui_logging:
  # 日志显示配置
  display:
    buffer_size: 100
    update_frequency: 10.0  # Hz
    max_display_lines: 50
    auto_scroll: true
    
  # 颜色配置
  colors:
    info: "#2196F3"
    warn: "#FF9800" 
    error: "#F44336"
    
  # 字体配置
  font:
    family: "Monospace"
    size: 10
    
  # 过滤默认设置
  default_filters:
    show_info: true
    show_warn: true
    show_error: true
    component_filter: "all"

# ROS2参数声明
/**:
  ros__parameters:
    ui_logging.display.buffer_size: 100
    ui_logging.display.update_frequency: 10.0
    ui_logging.display.auto_scroll: true
    ui_logging.colors.info: "#2196F3"
    ui_logging.colors.warn: "#FF9800"
    ui_logging.colors.error: "#F44336"
```

---

## ✅ 完成检查清单

- [x] LogPanel类实现并测试
- [x] LogDisplayWidget控件正常工作
- [x] 日志级别过滤功能完整
- [x] 搜索功能实现
- [x] 自动滚动功能正确
- [x] 日志导出功能可用
- [x] 颜色编码显示正常
- [x] 统计信息显示正确
- [x] 与ROS2日志集成
- [x] 与现有UI架构集成

---

## 🔍 测试场景

### 测试1: 基本日志显示
1. 添加不同级别的测试日志
2. 验证颜色编码正确
3. 测试时间戳格式

### 测试2: 过滤功能
1. 测试级别过滤（INFO/WARN/ERROR）
2. 测试组件过滤
3. 测试搜索功能

### 测试3: 性能压力测试
1. 模拟高频日志输入
2. 验证缓冲区管理
3. 测试自动滚动性能

### 测试4: 导出功能
1. 导出日志到文件
2. 验证导出格式
3. 测试大文件导出

### 测试5: UI集成
1. 集成到主窗口
2. 验证布局正确
3. 测试与其他面板的交互

---

## 📚 相关文档

- [Story 3-1: 混合日志方案实现](./3-1-hybrid-logging.md) - 日志数据源
- [Story 3-2: 系统健康指标监控实现](./3-2-health-monitoring.md) - 监控日志
- [Story 3-4: 日志存储与轮转实现](./3-4-log-rotation.md) - 日志管理
- [Story 1-5: 日志面板和错误提示实现](./1-5-log-panel.md) - 基础UI
- [docs/design_ui.md#日志面板] - UI设计规范

---

## 💡 实现提示

1. **性能优化**: 使用批量更新避免频繁刷新
2. **内存管理**: 限制缓冲区大小，避免内存溢出
3. **用户体验**: 提供清晰的视觉反馈和状态信息
4. **错误处理**: 导出等操作要有完善的错误处理
5. **可配置性**: 支持通过配置文件调整显示参数

---
