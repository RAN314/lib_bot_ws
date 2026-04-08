#!/usr/bin/env python3
"""
手动UI测试脚本
可以在终端单独启动，测试书籍录入、查找和任务取消功能
"""

import sys
import os
import time
import threading

# 添加UI包路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../src/libbot_ui'))

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit, QLabel, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal, QObject

from libbot_ui.ros2_manager import Ros2Manager


class ManualTestUI(QMainWindow):
    """手动测试UI"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Library Robot 手动测试")
        self.setGeometry(100, 100, 800, 600)

        # ROS2管理器
        self.ros2_manager = Ros2Manager()

        # 当前任务状态
        self.current_task = None
        self.task_active = False

        self.setup_ui()
        self.setup_ros2_connections()

    def setup_ui(self):
        """设置UI界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 标题
        title_label = QLabel("📚 Library Robot 手动测试")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 书籍ID输入区域
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("图书ID:"))

        self.book_id_input = QLineEdit()
        self.book_id_input.setPlaceholderText("请输入图书ID，例如: book_001")
        input_layout.addWidget(self.book_id_input)

        layout.addLayout(input_layout)

        # 按钮区域
        button_layout = QHBoxLayout()

        self.find_book_btn = QPushButton("🔍 开始找书")
        self.find_book_btn.clicked.connect(self.start_find_book)
        button_layout.addWidget(self.find_book_btn)

        self.cancel_btn = QPushButton("⏹️ 取消任务")
        self.cancel_btn.clicked.connect(self.cancel_task)
        self.cancel_btn.setEnabled(False)
        button_layout.addWidget(self.cancel_btn)

        self.clear_btn = QPushButton("🧹 清空日志")
        self.clear_btn.clicked.connect(self.clear_logs)
        button_layout.addWidget(self.clear_btn)

        layout.addLayout(button_layout)

        # 状态显示
        status_layout = QHBoxLayout()

        self.status_label = QLabel("状态: 空闲")
        self.status_label.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(self.status_label)

        self.progress_label = QLabel("进度: 0%")
        status_layout.addWidget(self.progress_label)

        layout.addLayout(status_layout)

        # 日志显示区域
        layout.addWidget(QLabel("📝 任务日志:"))

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        # 初始化日志
        self.add_log("✅ 手动测试UI已启动，可以开始测试")
        self.add_log("💡 提示: 输入图书ID后点击'开始找书'按钮")

    def setup_ros2_connections(self):
        """设置ROS2信号连接"""
        # 任务状态更新
        self.ros2_manager.task_status_updated.connect(self.on_task_status_updated)

        # 错误处理
        self.ros2_manager.error_occurred.connect(self.on_error_occurred)

        # 图书信息
        self.ros2_manager.book_info_received.connect(self.on_book_info_received)

    def start_find_book(self):
        """开始找书任务"""
        book_id = self.book_id_input.text().strip()
        if not book_id:
            QMessageBox.warning(self, "输入错误", "请输入图书ID")
            return

        self.add_log(f"🔍 开始找书任务: {book_id}")

        success = self.ros2_manager.send_find_book_goal(book_id)
        if success:
            self.task_active = True
            self.current_task = "find_book"
            self.find_book_btn.setEnabled(False)
            self.cancel_btn.setEnabled(True)
            self.status_label.setText("状态: 找书中...")
            self.status_label.setStyleSheet("color: blue; font-weight: bold;")
        else:
            self.add_log("❌ 发送找书任务失败")
            QMessageBox.critical(self, "错误", "发送找书任务失败")

    def cancel_task(self):
        """取消当前任务"""
        if not self.task_active:
            return

        self.add_log("⏹️ 正在取消任务...")

        success = self.ros2_manager.cancel_current_goal()
        if success:
            self.add_log("✅ 取消请求已发送")
            self.status_label.setText("状态: 取消中...")
            self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.add_log("❌ 发送取消请求失败")
            QMessageBox.warning(self, "警告", "发送取消请求失败")

    def on_task_status_updated(self, status):
        """处理任务状态更新"""
        if status.get("status") == "completed":
            self.add_log("✅ 任务完成")
            self.task_active = False
            self.current_task = None
            self.find_book_btn.setEnabled(True)
            self.cancel_btn.setEnabled(False)
            self.status_label.setText("状态: 完成")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")

        elif status.get("status") == "cancelled":
            self.add_log("⏹️ 任务已取消")
            self.task_active = False
            self.current_task = None
            self.find_book_btn.setEnabled(True)
            self.cancel_btn.setEnabled(False)
            self.status_label.setText("状态: 已取消")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

        elif status.get("status") == "navigating":
            progress = status.get("progress", 0)
            distance = status.get("distance_to_goal", 0)
            self.add_log(f"🚗 导航中: {progress:.1f}%, 距离目标: {distance:.2f}m")

        elif status.get("status") == "scanning":
            progress = status.get("progress", 0)
            signal = status.get("signal_strength", 0)
            books = status.get("books_detected", [])
            self.add_log(f"📡 扫描中: {progress:.1f}%, 信号强度: {signal:.2f}, 检测到图书: {len(books)}")

        elif status.get("status") == "approaching":
            progress = status.get("progress", 0)
            self.add_log(f"🎯 接近目标: {progress:.1f}%")

        # 更新进度显示
        if "progress" in status:
            self.progress_label.setText(f"进度: {status['progress']:.1f}%")

    def on_error_occurred(self, error):
        """处理错误"""
        error_code = error.get("error_code", "UNKNOWN")
        message = error.get("message", "未知错误")
        self.add_log(f"❌ 错误: {error_code} - {message}")

        # 重置UI状态
        self.task_active = False
        self.current_task = None
        self.find_book_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.status_label.setText("状态: 错误")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")

    def on_book_info_received(self, info):
        """处理图书信息"""
        book_id = info.get("id", "未知")
        title = info.get("title", "未知")
        author = info.get("author", "未知")
        self.add_log(f"📖 图书信息: {book_id} - {title} by {author}")

    def clear_logs(self):
        """清空日志"""
        self.log_text.clear()
        self.add_log("🧹 日志已清空")

    def add_log(self, message):
        """添加日志消息"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

        # 自动滚动到底部
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.End)
        self.log_text.setTextCursor(cursor)

    def closeEvent(self, event):
        """窗口关闭事件"""
        self.add_log("🛑 正在关闭UI...")
        self.ros2_manager.shutdown()
        event.accept()


def main():
    """主函数"""
    print("=== Library Robot 手动测试UI ===")
    print("此程序将启动一个图形界面，用于手动测试找书和取消功能")
    print("请确保ROS2环境已正确设置")
    print()

    app = QApplication(sys.argv)
    window = ManualTestUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()