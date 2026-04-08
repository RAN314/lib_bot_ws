# Story 1-5: 日志面板和错误提示实现

> **Epic**: #1 人机交互细节
> **Priority**: P0 (Critical)
> **Points**: 3
> **Status**: backlog
> **Platform**: ROS2 / Python / Qt5
> **Dependencies**: Story 1-2 (Ros2Manager通信封装), Story 1-4 (状态显示)

---

## 📋 用户故事 (User Story)

作为图书馆机器人操作员，
我希望能够查看系统运行日志和错误信息，
这样可以了解系统运行状况，快速定位问题，并进行故障排除。

---

## 🎯 验收标准 (Acceptance Criteria)

### 功能性要求
- [ ] 实时日志显示（INFO/WARN/ERROR/DEBUG级别）
- [ ] 日志自动滚动到最新消息
- [ ] 支持日志级别过滤
- [ ] 支持日志搜索功能
- [ ] 错误信息突出显示（红色背景、图标）
- [ ] 支持日志导出到文件
- [ ] 日志自动轮转（最大100条，超出时删除旧日志）
- [ ] 支持清空日志功能
- [ ] 错误提示弹窗（严重错误时）
- [ ] 日志时间戳显示（精确到毫秒）

### 界面要求
- [ ] 日志面板在右侧区域清晰显示
- [ ] 不同级别日志使用不同颜色和图标
- [ ] 支持日志面板展开/折叠
- [ ] 搜索框在日志面板顶部
- [ ] 过滤按钮组（全部/INFO/WARN/ERROR）
- [ ] 导出和清空按钮
- [ ] 错误弹窗模态显示，需要用户确认
- [ ] 日志条目支持多行显示

### 性能要求
- [ ] 日志显示延迟 < 50ms
- [ ] 搜索响应时间 < 100ms
- [ ] 日志导出时间 < 1秒（1000条以内）
- [ ] 内存占用优化，避免日志无限增长
- [ ] UI响应流畅，不因日志更新而卡顿

---

## 🔧 实现细节

### 文件清单
```
src/libbot_ui/libbot_ui/
├── log_panel.py                # 新建 - 日志面板组件
├── log_entry.py               # 新建 - 日志条目组件
├── error_dialog.py            # 新建 - 错误提示弹窗
├── log_filter.py              # 新建 - 日志过滤组件
└── right_panel.py             # 修改 - 集成日志面板
```

### LogPanel类设计

```python
# log_panel.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListView,
    QLineEdit, QPushButton, QFrame, QLabel
)
from PyQt5.QtCore import Qt, QStringListModel, QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import time
import json

class LogPanel(QFrame):
    """日志面板 - 显示系统运行日志和错误信息"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("log_panel")
        self.log_entries = []
        self.max_logs = 100
        self.current_filter = "ALL"
        self.search_text = ""
        
        self.setup_ui()
        self.setup_model()

    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 标题和控制按钮
        title_layout = QHBoxLayout()
        
        title = QLabel("📝 实时日志")
        title.setObjectName("log_title")
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        
        # 展开/折叠按钮
        self.toggle_btn = QPushButton("▼")
        self.toggle_btn.setFixedSize(30, 30)
        self.toggle_btn.clicked.connect(self.toggle_panel)
        title_layout.addWidget(self.toggle_btn)
        
        layout.addLayout(title_layout)

        # 搜索和过滤控件
        self.setup_controls(layout)

        # 日志列表
        self.log_list = QListView()
        self.log_list.setObjectName("log_list")
        self.log_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        layout.addWidget(self.log_list)

        # 底部按钮
        self.setup_bottom_buttons(layout)

    def setup_controls(self, layout):
        """设置搜索和过滤控件"""
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(8)

        # 搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索:")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索日志...")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(self.search_input)
        
        controls_layout.addLayout(search_layout)

        # 过滤按钮
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("级别:"))
        
        self.filter_buttons = {}
        filter_levels = ["ALL", "INFO", "WARN", "ERROR", "DEBUG"]
        
        for level in filter_levels:
            btn = QPushButton(level)
            btn.setCheckable(True)
            btn.setChecked(level == "ALL")
            btn.clicked.connect(lambda checked, l=level: self.on_filter_changed(l))
            filter_layout.addWidget(btn)
            self.filter_buttons[level] = btn
        
        filter_layout.addStretch()
        controls_layout.addLayout(filter_layout)
        
        layout.addLayout(controls_layout)

    def setup_bottom_buttons(self, layout):
        """设置底部按钮"""
        button_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("📤 导出")
        self.export_btn.clicked.connect(self.export_logs)
        button_layout.addWidget(self.export_btn)
        
        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.clicked.connect(self.clear_logs)
        button_layout.addWidget(self.clear_btn)
        
        button_layout.addStretch()
        
        self.log_count_label = QLabel("日志: 0 条")
        button_layout.addWidget(self.log_count_label)
        
        layout.addLayout(button_layout)

    def setup_model(self):
        """设置日志模型"""
        self.log_model = QStandardItemModel()
        self.filtered_model = QStandardItemModel()
        
        # 使用过滤后的模型
        self.log_list.setModel(self.filtered_model)

    def add_log_entry(self, message, level="INFO", timestamp=None):
        """添加日志条目

        Args:
            message: 日志消息
            level: 日志级别 (INFO/WARN/ERROR/DEBUG)
            timestamp: 时间戳（可选，默认当前时间）
        """
        if timestamp is None:
            timestamp = time.time()
            
        # 创建日志条目
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "formatted_time": self.format_timestamp(timestamp)
        }
        
        # 添加到日志列表
        self.log_entries.insert(0, log_entry)  # 最新的在前面
        
        # 限制日志数量
        if len(self.log_entries) > self.max_logs:
            self.log_entries = self.log_entries[:self.max_logs]
        
        # 更新显示
        self.update_display()
        
        # 如果是ERROR级别，显示错误弹窗
        if level == "ERROR":
            self.show_error_dialog(message)

    def format_timestamp(self, timestamp):
        """格式化时间戳"""
        from datetime import datetime
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%H:%M:%S.%f")[:-3]  # 精确到毫秒

    def update_display(self):
        """更新显示"""
        # 清空过滤模型
        self.filtered_model.clear()
        
        # 根据过滤条件添加条目
        for entry in self.log_entries:
            if self.should_show_entry(entry):
                item = self.create_log_item(entry)
                self.filtered_model.appendRow(item)
        
        # 更新计数
        self.log_count_label.setText(f"日志: {len(self.log_entries)} 条")
        
        # 滚动到顶部（最新消息）
        if self.filtered_model.rowCount() > 0:
            self.log_list.scrollToTop()

    def should_show_entry(self, entry):
        """判断是否应该显示该条目"""
        # 检查级别过滤
        if self.current_filter != "ALL" and entry["level"] != self.current_filter:
            return False
        
        # 检查搜索过滤
        if self.search_text and self.search_text.lower() not in entry["message"].lower():
            return False
            
        return True

    def create_log_item(self, entry):
        """创建日志项"""
        # 格式化显示文本
        display_text = f"[{entry['formatted_time']}] {self.get_level_icon(entry['level'])} {entry['message']}"
        
        item = QStandardItem(display_text)
        
        # 设置颜色
        color = self.get_level_color(entry["level"])
        item.setForeground(color)
        
        # 设置字体粗细
        if entry["level"] == "ERROR":
            font = item.font()
            font.setBold(True)
            item.setFont(font)
        
        return item

    def get_level_icon(self, level):
        """获取级别图标"""
        icons = {
            "INFO": "ℹ️",
            "WARN": "⚠️", 
            "ERROR": "❌",
            "DEBUG": "🔍"
        }
        return icons.get(level, "📝")

    def get_level_color(self, level):
        """获取级别颜色"""
        colors = {
            "INFO": Qt.blue,
            "WARN": Qt.darkYellow,
            "ERROR": Qt.red,
            "DEBUG": Qt.gray
        }
        return colors.get(level, Qt.black)

    def on_search_changed(self, text):
        """搜索文本变化"""
        self.search_text = text
        self.update_display()

    def on_filter_changed(self, level):
        """过滤级别变化"""
        # 更新按钮状态
        for btn_level, btn in self.filter_buttons.items():
            btn.setChecked(btn_level == level)
        
        self.current_filter = level
        self.update_display()

    def toggle_panel(self):
        """展开/折叠面板"""
        is_visible = self.log_list.isVisible()
        
        self.log_list.setVisible(not is_visible)
        self.search_input.setVisible(not is_visible)
        
        # 更新按钮文本
        if is_visible:
            self.toggle_btn.setText("▶")
        else:
            self.toggle_btn.setText("▼")

    def export_logs(self):
        """导出日志到文件"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "导出日志", "", "JSON文件 (*.json);;文本文件 (*.txt)"
            )
            
            if filename:
                if filename.endswith('.json'):
                    self.export_to_json(filename)
                else:
                    self.export_to_text(filename)
                    
                # 添加导出成功的日志
                self.add_log_entry(f"日志已导出到: {filename}", "INFO")
                
        except Exception as e:
            self.add_log_entry(f"导出日志失败: {e}", "ERROR")

    def export_to_json(self, filename):
        """导出为JSON格式"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.log_entries, f, ensure_ascii=False, indent=2)

    def export_to_text(self, filename):
        """导出为文本格式"""
        with open(filename, 'w', encoding='utf-8') as f:
            for entry in reversed(self.log_entries):  # 按时间顺序
                f.write(f"[{entry['formatted_time']}] {self.get_level_icon(entry['level'])} {entry['message']}\n")

    def clear_logs(self):
        """清空所有日志"""
        self.log_entries.clear()
        self.update_display()

    def show_error_dialog(self, message):
        """显示错误弹窗"""
        from .error_dialog import ErrorDialog
        
        dialog = ErrorDialog(message, self)
        dialog.exec_()


class LogFilter:
    """日志过滤器"""
    
    def __init__(self):
        self.level_filter = "ALL"
        self.search_filter = ""
        self.time_range = None
    
    def matches(self, log_entry):
        """检查日志条目是否匹配过滤条件"""
        # 级别过滤
        if self.level_filter != "ALL" and log_entry["level"] != self.level_filter:
            return False
            
        # 搜索过滤
        if self.search_filter and self.search_filter.lower() not in log_entry["message"].lower():
            return False
            
        # 时间范围过滤
        if self.time_range:
            start_time, end_time = self.time_range
            if not (start_time <= log_entry["timestamp"] <= end_time):
                return False
                
        return True
```

### ErrorDialog错误弹窗

```python
# error_dialog.py

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QFrame
)
from PyQt5.QtCore import Qt
import traceback

class ErrorDialog(QDialog):
    """错误提示弹窗 - 用于显示严重错误信息"""

    def __init__(self, error_message, parent=None, show_details=True):
        super().__init__(parent)
        self.error_message = error_message
        self.show_details = show_details
        
        self.setWindowTitle("❌ 系统错误")
        self.setModal(True)
        self.resize(500, 300)
        
        self.setup_ui()

    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        
        # 错误图标和标题
        header_layout = QHBoxLayout()
        
        icon_label = QLabel("❌")
        icon_label.setStyleSheet("font-size: 32px;")
        header_layout.addWidget(icon_label)
        
        title_label = QLabel("系统发生错误")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 错误信息
        message_frame = QFrame()
        message_frame.setObjectName("message_frame")
        message_layout = QVBoxLayout(message_frame)
        
        message_label = QLabel("错误信息:")
        message_layout.addWidget(message_label)
        
        self.message_text = QTextEdit()
        self.message_text.setReadOnly(True)
        self.message_text.setText(self.error_message)
        self.message_text.setMaximumHeight(100)
        message_layout.addWidget(self.message_text)
        
        layout.addWidget(message_frame)
        
        # 详细信息（可选）
        if self.show_details:
            details_frame = QFrame()
            details_frame.setObjectName("details_frame")
            details_layout = QVBoxLayout(details_frame)
            
            details_label = QLabel("详细信息:")
            details_layout.addWidget(details_label)
            
            self.details_text = QTextEdit()
            self.details_text.setReadOnly(True)
            self.details_text.setText(self.get_error_details())
            details_layout.addWidget(self.details_text)
            
            layout.addWidget(details_frame)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)

    def get_error_details(self):
        """获取错误详细信息"""
        try:
            import sys
            exc_type, exc_value, exc_traceback = sys.exc_info()
            
            if exc_traceback:
                details = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            else:
                details = f"错误类型: {type(self.error_message).__name__}\n错误信息: {self.error_message}"
                
            return details
        except:
            return str(self.error_message)
```

### RightPanel集成

```python
# right_panel.py 修改

from .log_panel import LogPanel

class RightPanel(QWidget):
    def __init__(self):
        super().__init__()
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 状态面板
        self.status_panel = StatusPanel()
        layout.addWidget(self.status_panel)
        
        # 日志面板
        self.log_panel = LogPanel()
        layout.addWidget(self.log_panel)

    def add_log_entry(self, message, level="INFO"):
        """添加日志条目（兼容旧接口）"""
        self.log_panel.add_log_entry(message, level)

    def update_task_status(self, status_dict):
        """更新任务状态"""
        self.status_panel.update_status(status_dict)
        
        # 同时记录到日志
        status = status_dict.get("status", "unknown")
        progress = status_dict.get("progress", 0)
        
        if status in ["completed", "cancelled", "failed"]:
            level = "ERROR" if status == "failed" else "INFO"
            self.log_panel.add_log_entry(
                f"任务状态更新: {status} ({progress:.1f}%)", level
            )
```

---

## ✅ 完成检查清单

- [ ] LogPanel类实现并测试
- [ ] ErrorDialog错误弹窗实现
- [ ] 日志搜索功能实现
- [ ] 日志过滤功能实现
- [ ] 日志导出功能实现（JSON和TXT格式）
- [ ] 日志轮转机制实现（最大100条）
- [ ] 错误弹窗自动显示
- [ ] 时间戳显示（精确到毫秒）
- [ ] 不同级别日志颜色区分
- [ ] 日志面板展开/折叠功能
- [ ] RightPanel集成LogPanel
- [ ] 日志性能优化验证
- [ ] 手动测试所有日志功能
- [ ] 代码通过Black格式化检查

---

## 🔍 测试场景

### 测试1: 基础日志功能
1. 启动UI程序
2. 验证日志面板正常显示
3. 添加不同级别的日志
4. 验证颜色和图标显示正确

### 测试2: 日志过滤功能
1. 添加多个不同级别的日志
2. 测试级别过滤（INFO/WARN/ERROR）
3. 验证只有符合条件的日志显示
4. 测试"ALL"过滤恢复正常显示

### 测试3: 搜索功能
1. 添加包含不同关键词的日志
2. 在搜索框输入关键词
3. 验证只有包含关键词的日志显示
4. 测试清空搜索恢复正常显示

### 测试4: 日志导出功能
1. 添加多条测试日志
2. 点击导出按钮
3. 选择JSON格式导出
4. 验证导出的文件内容正确
5. 测试TXT格式导出

### 测试5: 错误弹窗
1. 触发ERROR级别日志
2. 验证错误弹窗自动显示
3. 验证弹窗内容正确
4. 测试点击确定关闭弹窗

### 测试6: 日志轮转
1. 添加超过100条日志
2. 验证只保留最新的100条
3. 验证旧日志被正确删除

### 测试7: 性能压测
1. 快速添加大量日志（1000条）
2. 验证UI不卡顿
3. 验证内存使用正常
4. 测试搜索和过滤响应速度

---

## 📚 相关文档

- [Story 1-1: UI主窗口实现](./1-1-ui-main-window.md) - UI基础结构
- [Story 1-2: Ros2Manager通信封装](./1-2-ros2-manager.md) - ROS2通信层
- [Story 1-3: 找书对话框和按钮实现](./1-3-find-book-dialog.md) - 任务触发
- [Story 1-4: 状态显示和进度条实现](./1-4-status-display.md) - 状态显示

---

## 💡 实现提示

1. **性能优化**: 使用QTimer批处理日志更新，避免频繁UI刷新
2. **内存管理**: 严格限制日志数量，避免无限增长
3. **用户体验**: 最新消息显示在最上面，自动滚动到顶部
4. **错误处理**: 严重错误自动弹窗，确保用户注意到
5. **数据导出**: 支持多种格式导出，便于问题分析
6. **搜索性能**: 使用高效的字符串匹配算法
7. **界面响应**: 异步处理耗时操作，保持UI流畅
8. **日志格式**: 统一的时间戳格式，便于排序和分析