#!/usr/bin/env python3
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QLabel,
    QTextEdit, QListView, QProgressBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

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

        # 当前任务卡
        self.task_card = TaskCard()
        layout.addWidget(self.task_card)

        # 统计信息卡
        self.stats_card = StatsCard()
        layout.addWidget(self.stats_card)

        # 日志面板
        self.log_panel = LogPanel()
        layout.addWidget(self.log_panel)

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
    """日志面板组件"""

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
        self.setup_ui()

        # 日志模型
        self.log_model = QStandardItemModel()
        self.log_model.setColumnCount(1)
        self.log_list.setModel(self.log_model)

        # 最大日志数量
        self.max_logs = 100

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # 标题
        title = QLabel("📝 实时日志")
        title.setObjectName("log_title")
        layout.addWidget(title)

        # 日志列表
        self.log_list = QListView()
        self.log_list.setObjectName("log_list")
        layout.addWidget(self.log_list)

    def add_log(self, message, level="INFO"):
        """添加日志消息

        Args:
            message: 日志消息
            level: 日志级别 (INFO/WARN/ERROR/DEBUG)
        """
        # 根据不同的级别设置颜色
        colors = {
            "INFO": "#2196F3",  # 蓝色
            "WARN": "#FF9800",  # 橙色
            "ERROR": "#F44336",  # 红色
            "DEBUG": "#9E9E9E"  # 灰色
        }

        color = colors.get(level, "#000000")

        # 创建日志项
        item = QStandardItem(message)

        # 设置文本颜色（前景色）
        text_colors = {
            "INFO": Qt.blue,
            "WARN": Qt.darkYellow,
            "ERROR": Qt.red,
            "DEBUG": Qt.gray
        }
        text_color = text_colors.get(level, Qt.black)
        item.setForeground(text_color)

        # 添加到模型
        self.log_model.insertRow(0, item)

        # 限制日志数量
        if self.log_model.rowCount() > self.max_logs:
            self.log_model.removeRow(self.log_model.rowCount() - 1)

    def update_task_status(self, status_dict):
        """更新任务状态

        Args:
            status_dict: 状态字典，格式取决于Ros2Manager的信号
        """
        try:
            # 提取状态信息
            status = status_dict.get("status", "unknown")
            progress = status_dict.get("progress", 0)
            estimated_remaining = status_dict.get("estimated_remaining", 0)

            # 更新任务卡片
            if hasattr(self.task_card, 'update_task'):
                self.task_card.update_task(
                    status=status,
                    progress=progress,
                    info=f"预计剩余时间: {estimated_remaining:.1f}秒" if estimated_remaining > 0 else None
                )

            # 更新状态文本
            status_text = self._get_status_text(status)
            if hasattr(self.task_card, 'task_status_label'):
                self.task_card.task_status_label.setText(f"状态: {status_text}")

            # 更新进度条
            if hasattr(self.task_card, 'progress_bar'):
                self.task_card.progress_bar.setValue(int(progress))

        except Exception as e:
            print(f"Error updating task status: {e}")

    def _get_status_text(self, status):
        """获取状态文本"""
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

    def show_error(self, error_dict):
        """显示错误

        Args:
            error_dict: 错误字典 {"error_code": "...", "message": "..."}
        """
        error_code = error_dict.get("error_code", "UNKNOWN")
        message = error_dict.get("message", "Unknown error")

        # 添加到日志
        self.add_log(f"错误 [{error_code}]: {message}", "ERROR")

    def clear_logs(self):
        """清空所有日志"""
        self.log_model.clear()

    def add_log_entry(self, message, level="INFO"):
        """添加日志条目（兼容旧接口）"""
        self.add_log(message, level)

    def add_timestamped_log(self, message, level="INFO"):
        """添加时间戳的日志"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.add_log(formatted_message, level)
