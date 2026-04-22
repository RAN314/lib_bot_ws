#!/usr/bin/env python3
"""
状态显示面板 - 实时显示机器人任务状态
Story 1-4: 状态显示和进度条实现
"""

import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame,
    QHBoxLayout, QPushButton
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QPalette

from .progress_widget import ProgressBar


class StatusPanel(QWidget):
    """状态显示面板 - 实时显示机器人任务状态"""

    refresh_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_status = "idle"
        self.status_history = []
        self.max_history = 10
        self.setup_ui()

    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 设置面板背景色以便调试
        self.setStyleSheet("background-color: #e0f0ff;")

        # 当前状态标题
        title = QLabel("🤖 机器人状态")
        title.setObjectName("status_title")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        layout.addWidget(title)

        # 任务状态卡片
        self.task_card = TaskStatusCard()
        layout.addWidget(self.task_card)

        # 机器人位置信息
        self.position_card = PositionCard()
        layout.addWidget(self.position_card)

        # 传感器信息
        self.sensor_card = SensorCard()
        layout.addWidget(self.sensor_card)

        # 刷新按钮
        refresh_layout = QHBoxLayout()
        refresh_layout.addStretch()

        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.clicked.connect(self.on_refresh_clicked)
        refresh_layout.addWidget(self.refresh_btn)

        layout.addLayout(refresh_layout)

    def update_status(self, status_data):
        """更新状态信息

        Args:
            status_data: 状态数据字典
                {
                    "status": "navigating",
                    "progress": 75.5,
                    "estimated_remaining": 30.2,
                    "robot_pose": {"x": 1.2, "y": 3.4},
                    "books_detected": 3,
                    "signal_strength": 0.85
                }
        """
        try:
            print(f"[DEBUG] StatusPanel.update_status: {status_data.get('status', 'unknown')}, progress: {status_data.get('progress', 0)}")

            # 更新任务状态卡片
            self.task_card.update_status(
                status=status_data.get("status", "unknown"),
                progress=status_data.get("progress", 0),
                remaining_time=status_data.get("estimated_remaining", 0)
            )

            # 更新位置信息（带轻量级节流）
            pose_data = status_data.get("robot_pose") or status_data.get("current_pose")
            if pose_data:
                current_time = time.time()
                # 位置信息每0.3秒更新一次，避免过于频繁的UI刷新
                if not hasattr(self, '_last_pose_update') or (current_time - self._last_pose_update) >= 0.3:
                    self.position_card.update_position(pose_data)
                    self._last_pose_update = current_time

            # 更新传感器信息
            self.sensor_card.update_sensor_data({
                "books_detected": status_data.get("books_detected", 0),
                "signal_strength": status_data.get("signal_strength", 0)
            })

            # 添加到历史记录
            self.add_to_history(status_data)

            print(f"[DEBUG] StatusPanel.update_status completed")

        except Exception as e:
            print(f"Error updating status: {e}")
            import traceback
            traceback.print_exc()

    def add_to_history(self, status_data):
        """添加状态到历史记录"""
        import time
        history_entry = {
            "timestamp": time.time(),
            "status": status_data.get("status", "unknown"),
            "progress": status_data.get("progress", 0)
        }

        self.status_history.insert(0, history_entry)

        # 限制历史记录数量
        if len(self.status_history) > self.max_history:
            self.status_history = self.status_history[:self.max_history]

    def on_refresh_clicked(self):
        """手动刷新按钮点击"""
        # 发送刷新信号
        self.refresh_clicked.emit()

    def clear_status(self):
        """清除状态信息"""
        self.task_card.clear()
        self.position_card.clear()
        self.sensor_card.clear()
        self.status_history.clear()


class TaskStatusCard(QFrame):
    """任务状态卡片"""

    def __init__(self):
        super().__init__()
        self.setObjectName("task_status_card")
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
        """设置任务状态UI"""
        layout = QVBoxLayout(self)

        # 状态文本
        self.status_label = QLabel("状态: 待机")
        self.status_label.setObjectName("status_label")
        self.status_label.setStyleSheet("font-size: 14px; color: #333; margin: 5px;")
        layout.addWidget(self.status_label)

        # 进度条
        self.progress_bar = ProgressBar()
        layout.addWidget(self.progress_bar)

        # 剩余时间
        self.time_label = QLabel("预计剩余: --")
        self.time_label.setObjectName("time_label")
        self.time_label.setStyleSheet("font-size: 14px; color: #333; margin: 5px;")
        layout.addWidget(self.time_label)

    def update_status(self, status, progress, remaining_time):
        """更新任务状态"""
        print(f"[DEBUG] TaskStatusCard.update_status: {status}, progress: {progress}")

        # 更新状态文本
        status_text = self._get_status_text(status)
        print(f"[DEBUG] Setting status text: {status_text}")
        self.status_label.setText(f"状态: {status_text}")

        # 更新进度条
        print(f"[DEBUG] Setting progress: {progress}")
        self.progress_bar.set_progress(progress)

        # 更新剩余时间
        if remaining_time > 0:
            time_text = f"预计剩余: {remaining_time:.1f}秒"
            print(f"[DEBUG] Setting time text: {time_text}")
            self.time_label.setText(time_text)
        else:
            print(f"[DEBUG] Setting time text: --")
            self.time_label.setText("预计剩余: --")

        print(f"[DEBUG] TaskStatusCard.update_status completed")

        # 强制UI刷新
        self.status_label.repaint()
        self.progress_bar.repaint()
        self.time_label.repaint()

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

    def clear(self):
        """清除状态"""
        print(f"[DEBUG] TaskStatusCard.clear() called")
        self.status_label.setText("状态: 待机")
        self.progress_bar.set_progress(0)
        self.time_label.setText("预计剩余: --")


class PositionCard(QFrame):
    """位置信息卡片"""

    def __init__(self):
        super().__init__()
        self.setObjectName("position_card")
        self.setup_ui()

    def setup_ui(self):
        """设置位置信息UI"""
        layout = QVBoxLayout(self)

        title = QLabel("📍 位置信息")
        title.setObjectName("card_title")
        layout.addWidget(title)

        self.position_label = QLabel("位置: (--, --)")
        self.position_label.setObjectName("position_label")
        layout.addWidget(self.position_label)

    def update_position(self, pose):
        """更新位置信息"""
        print(f"[DEBUG] PositionCard.update_position: {pose}")
        x = pose.get("x", 0)
        y = pose.get("y", 0)
        position_text = f"位置: ({x:.2f}, {y:.2f})"
        print(f"[DEBUG] Setting position text: {position_text}")
        self.position_label.setText(position_text)

    def clear(self):
        """清除位置信息"""
        self.position_label.setText("位置: (--, --)")


class SensorCard(QFrame):
    """传感器信息卡片"""

    def __init__(self):
        super().__init__()
        self.setObjectName("sensor_card")

        # 添加清除延迟机制
        self.clear_timer = None

        self.setup_ui()

    def setup_ui(self):
        """设置传感器信息UI"""
        layout = QVBoxLayout(self)

        title = QLabel("📡 传感器信息")
        title.setObjectName("card_title")
        layout.addWidget(title)

        self.books_label = QLabel("检测到图书: 0")
        self.books_label.setObjectName("books_label")
        layout.addWidget(self.books_label)

        self.signal_label = QLabel("信号强度: 0%")
        self.signal_label.setObjectName("signal_label")
        layout.addWidget(self.signal_label)

        # 最高信号强度书籍信息
        self.best_book_label = QLabel("最强信号书籍: --")
        self.best_book_label.setObjectName("best_book_label")
        layout.addWidget(self.best_book_label)

    def update_sensor_data(self, sensor_data, detected_books=None, signal_strengths=None, direction="unknown"):
        """更新传感器数据"""
        current_time = time.time()

        # 提高刷新率 - 只有数据变化时才更新，但允许更频繁的更新
        if hasattr(self, 'last_update_time') and (current_time - self.last_update_time) < 0.1:
            return  # 100ms最小间隔，提高响应速度

        books = sensor_data.get("books_detected", 0)
        signal = sensor_data.get("signal_strength", 0)

        # 如果有具体的书籍和信号强度数据，找出最强的
        best_book_info = ""
        if detected_books and signal_strengths and len(detected_books) == len(signal_strengths):
            max_index = signal_strengths.index(max(signal_strengths))
            best_book = detected_books[max_index]
            best_signal = signal_strengths[max_index]
            best_book_info = f" (最强: {best_book} {best_signal*100:.0f}%)"

        self.books_label.setText(f"检测到图书: {books}")
        self.signal_label.setText(f"信号强度: {signal*100:.0f}%{best_book_info}")
        self.best_book_label.setText(f"最强信号书籍: {best_book if detected_books and signal_strengths else '--'}")

        # 如果有检测到数据，取消之前的清除定时器
        if detected_books and signal_strengths:
            if self.clear_timer:
                self.clear_timer.stop()
                self.clear_timer = None
        else:
            # 没有检测到数据，设置1.5秒后清除
            if not self.clear_timer:
                from PyQt5.QtCore import QTimer
                self.clear_timer = QTimer(self)
                self.clear_timer.setSingleShot(True)
                self.clear_timer.timeout.connect(self._delayed_clear)
                self.clear_timer.start(1500)  # 1.5秒后清除

        # 强制UI刷新
        self.books_label.repaint()
        self.signal_label.repaint()
        self.best_book_label.repaint()

        # 存储最后的数据用于下次比较
        self._last_detected_books = detected_books or []
        self._last_signal = signal
        self.last_update_time = current_time

    def clear(self):
        """清除传感器信息"""
        self.books_label.setText("检测到图书: 0")
        self.signal_label.setText("信号强度: 0%")
        self.best_book_label.setText("最强信号书籍: --")
        # 停止清除定时器
        if hasattr(self, 'clear_timer') and self.clear_timer:
            self.clear_timer.stop()
            self.clear_timer = None

    def _delayed_clear(self):
        """延迟清除传感器信息"""
        if not hasattr(self, '_last_detected_books') or not self._last_detected_books:
            self.clear()