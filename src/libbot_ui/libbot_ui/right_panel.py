#!/usr/bin/env python3
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
    QTextEdit, QListView, QProgressBar, QLineEdit, QPushButton,
    QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import time
import json

from .status_panel import StatusPanel

class RightPanel(QWidget):
    """右侧面板 - 600px宽，显示信息"""

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 状态显示面板 (替换原有的task_card)
        self.status_panel = StatusPanel()
        layout.addWidget(self.status_panel)

        # 统计信息卡
        self.stats_card = StatsCard()
        layout.addWidget(self.stats_card)

        # 日志面板
        self.log_panel = LogPanel()
        layout.addWidget(self.log_panel)

    def update_task_status(self, status_dict):
        """更新任务状态

        Args:
            status_dict: 状态字典，格式取决于Ros2Manager的信号
        """
        try:
            print(f"[DEBUG] RightPanel.update_task_status called: {status_dict.get('status', 'unknown')}")
            # 使用新的StatusPanel更新状态
            if hasattr(self, 'status_panel'):
                print(f"[DEBUG] Calling status_panel.update_status")
                self.status_panel.update_status(status_dict)
                print(f"[DEBUG] status_panel.update_status completed")
            else:
                print(f"[DEBUG] status_panel not found!")

        except Exception as e:
            print(f"Error updating task status: {e}")

    def add_log_entry(self, message, level="INFO"):
        """添加日志条目（兼容旧接口）"""
        if hasattr(self, 'log_panel'):
            self.log_panel.add_log_entry(message, level)

class TaskCard(QFrame):
    """任务卡组件"""

    def __init__(self):
        super().__init__()
        self.setObjectName("task_card")
        self.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
        """)
        self.setMinimumHeight(200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # 标题
        title = QLabel("📖 当前任务")
        title.setObjectName("card_title")
        layout.addWidget(title)

        # 任务ID
        self.task_id_label = QLabel("任务ID: 无")
        self.task_id_label.setObjectName("task_id")
        layout.addWidget(self.task_id_label)

        # 状态
        self.task_status_label = QLabel("状态: 空闲")
        self.task_status_label.setObjectName("task_status")
        layout.addWidget(self.task_status_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # 信息区域
        self.task_info = QTextEdit()
        self.task_info.setObjectName("task_info")
        self.task_info.setReadOnly(True)
        self.task_info.setMaximumHeight(100)
        layout.addWidget(self.task_info)

    def update_task(self, task_id=None, status=None, progress=None, info=None):
        """更新任务信息"""
        if task_id is not None:
            self.task_id_label.setText(f"任务ID: {task_id}")
        if status is not None:
            self.task_status_label.setText(f"状态: {status}")
        if progress is not None:
            self.progress_bar.setValue(int(progress))
        if info is not None:
            self.task_info.setText(info)

class StatsCard(QFrame):
    """统计信息卡组件"""

    def __init__(self):
        super().__init__()
        self.setObjectName("stats_card")
        self.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
        """)
        self.setMinimumHeight(150)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # 标题
        title = QLabel("📊 今日统计")
        title.setObjectName("stats_title")
        layout.addWidget(title)

        # 统计信息
        self.stats_info = QTextEdit()
        self.stats_info.setObjectName("stats_info")
        self.stats_info.setReadOnly(True)
        self.stats_info.setText("已完成任务: 0\n成功率: 0%\n平均时长: --")
        self.stats_info.setMaximumHeight(80)
        layout.addWidget(self.stats_info)

    def update_stats(self, completed=0, success_rate=0, avg_time="--"):
        """更新统计信息"""
        self.stats_info.setText(
            f"已完成任务: {completed}\n"
            f"成功率: {success_rate}%\n"
            f"平均时长: {avg_time}"
        )

class LogPanel(QFrame):
    """日志面板组件 - 显示系统运行日志和错误信息"""

    def __init__(self):
        super().__init__()
        self.setObjectName("log_panel")
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
        """)
        self.setMinimumHeight(200)

        # 日志数据存储
        self.log_entries = []
        self.max_logs = 100
        self.current_filter = "ALL"
        self.search_text = ""

        self.setup_ui()
        self.setup_model()

    def setup_model(self):
        """设置日志模型"""
        self.log_model = QStandardItemModel()
        self.filtered_model = QStandardItemModel()

        # 使用过滤后的模型
        self.log_list.setModel(self.filtered_model)

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

    def setup_ui(self):
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

    def add_log(self, message, level="INFO"):
        """添加日志消息（兼容旧接口）

        Args:
            message: 日志消息
            level: 日志级别 (INFO/WARN/ERROR/DEBUG)
        """
        self.add_log_entry(message, level)

    def _get_status_text(self, status):
        """获取状态文本（保留用于兼容性）"""
        status_map = {
            "idle": "待机",
            "navigating": "导航中",
            "scanning": "扫描中",
            "approaching": "接近目标",
            "completed": "完成",
            "cancelled": "已取消",
            "failed": "失败"
        }
        return status_map.get(status, status)

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

    def show_error(self, error_dict):
        """显示错误

        Args:
            error_dict: 错误字典 {"error_code": "...", "message": "..."}
        """
        error_code = error_dict.get("error_code", "UNKNOWN")
        message = error_dict.get("message", "Unknown error")

        # 添加到日志
        self.add_log_entry(f"错误 [{error_code}]: {message}", "ERROR")

    def add_timestamped_log(self, message, level="INFO"):
        """添加时间戳的日志"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.add_log_entry(formatted_message, level)
