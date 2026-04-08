#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QSplitter,
    QListView,
    QTextEdit,
    QLabel,
    QStatusBar,
    QApplication,
    QShortcut,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence
from .left_panel import LeftPanel
from .right_panel import RightPanel
from .ros2_manager import Ros2Manager
from .find_book_dialog import FindBookDialog


class MainWindow(QMainWindow):
    """主窗口类 - 800x600控制面板"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("libbot控制面板 v1.0")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(800, 600)

        # 中心组件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 设置主布局
        self.setup_ui()

        # 状态栏
        self.setup_status_bar()

        # ROS2管理器
        self.ros2_manager = Ros2Manager()

        # 找书对话框
        self.find_book_dialog = FindBookDialog(self, self.ros2_manager)

        self.setup_ros2_connections()

    def setup_ui(self):
        # 创建主水平分割器
        main_splitter = QSplitter(Qt.Horizontal)

        # 左侧面板
        self.left_panel = LeftPanel()
        main_splitter.addWidget(self.left_panel)

        # 右侧面板
        self.right_panel = RightPanel()
        main_splitter.addWidget(self.right_panel)

        # 设置分割器比例
        main_splitter.setSizes([200, 600])

        # 添加到主布局
        layout = QHBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(main_splitter)

    def setup_status_bar(self):
        """设置状态栏"""
        self.status_bar = self.statusBar()

        # 连接状态
        self.connection_status = QLabel("连接中...")
        self.connection_status.setObjectName("connection_status")
        self.status_bar.addWidget(self.connection_status)

        # 分隔符
        self.status_bar.addPermanentWidget(QLabel("|"))

        # FPS
        self.fps_label = QLabel("FPS: --")
        self.fps_label.setObjectName("fps_label")
        self.status_bar.addPermanentWidget(self.fps_label)

        # 机器人状态
        self.robot_status = QLabel("机器人: 正常")
        self.robot_status.setObjectName("robot_status")
        self.status_bar.addPermanentWidget(self.robot_status)

        # 导航状态
        self.nav_status = QLabel("导航: 待机")
        self.nav_status.setObjectName("nav_status")
        self.status_bar.addPermanentWidget(self.nav_status)

    def setup_ros2_connections(self):
        """连接ROS2管理器的信号到UI"""
        # 任务状态更新
        self.ros2_manager.task_status_updated.connect(self.on_task_status_updated)

        # 系统健康状态
        self.ros2_manager.system_health_updated.connect(self.on_system_health_updated)

        # 机器人位置更新
        self.ros2_manager.robot_pose_updated.connect(self.on_robot_pose_updated)

        # 错误处理
        self.ros2_manager.error_occurred.connect(self.on_error_occurred)

        # 图书信息
        self.ros2_manager.book_info_received.connect(self.on_book_info_received)

        # 左侧面板按钮信号
        self.left_panel.find_book_clicked.connect(self.show_find_book_dialog)
        self.left_panel.cancel_clicked.connect(self.on_cancel_clicked)
        # 删除pause_clicked连接
        self.left_panel.exit_clicked.connect(self.close)

        # 对话框信号
        self.find_book_dialog.find_book_confirmed.connect(self.on_find_book_confirmed)

        # 快捷键 - 使用应用级快捷键确保在ROS2环境中工作
        self.find_book_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        self.find_book_shortcut.setContext(Qt.ApplicationShortcut)  # 关键：设置为应用级快捷键
        self.find_book_shortcut.activated.connect(self.show_find_book_dialog)

        # 更新连接状态
        self.connection_status.setText("已连接")

        # 添加初始日志
        if hasattr(self.right_panel, 'add_timestamped_log'):
            self.right_panel.add_timestamped_log("🚀 libbot控制面板已启动", "INFO")
            self.right_panel.add_timestamped_log("💡 使用Ctrl+N快捷键打开找书对话框", "INFO")
        elif hasattr(self.right_panel, 'add_log_entry'):
            self.right_panel.add_log_entry("🚀 libbot控制面板已启动", "INFO")
            self.right_panel.add_log_entry("💡 使用Ctrl+N快捷键打开找书对话框", "INFO")

    def show_find_book_dialog(self):
        """显示找书对话框"""
        self.find_book_dialog.show()

    def on_find_book_confirmed(self, book_id, guide_patron):
        """找书确认处理"""
        # 发送找书任务
        success = self.ros2_manager.send_find_book_goal(
            book_id,
            guide_patron
        )

        if success:
            # 在日志面板显示任务已发送
            if hasattr(self.right_panel, 'add_timestamped_log'):
                self.right_panel.add_timestamped_log(
                    f"🎯 找书任务已发送: {book_id} (引导读者: {'是' if guide_patron else '否'})",
                    "INFO"
                )
            elif hasattr(self.right_panel, 'add_log_entry'):
                self.right_panel.add_log_entry(
                    f"🎯 找书任务已发送: {book_id} (引导读者: {'是' if guide_patron else '否'})",
                    "INFO"
                )
        else:
            # 显示错误
            if hasattr(self.right_panel, 'add_timestamped_log'):
                self.right_panel.add_timestamped_log(
                    f"❌ 找书任务发送失败: {book_id}",
                    "ERROR"
                )
            elif hasattr(self.right_panel, 'add_log_entry'):
                self.right_panel.add_log_entry(
                    f"❌ 找书任务发送失败: {book_id}",
                    "ERROR"
                )

    def on_cancel_clicked(self):
        """取消按钮点击处理"""
        success = self.ros2_manager.cancel_current_goal()
        if success:
            if hasattr(self.right_panel, 'add_timestamped_log'):
                self.right_panel.add_timestamped_log("⏹️ 已发送取消请求", "WARN")
            elif hasattr(self.right_panel, 'add_log_entry'):
                self.right_panel.add_log_entry("⏹️ 已发送取消请求", "WARN")
        else:
            if hasattr(self.right_panel, 'add_timestamped_log'):
                self.right_panel.add_timestamped_log("❌ 取消请求发送失败", "ERROR")
            elif hasattr(self.right_panel, 'add_log_entry'):
                self.right_panel.add_log_entry("❌ 取消请求发送失败", "ERROR")

    def on_task_status_updated(self, status):
        """处理任务状态更新"""
        status_text = status.get("status", "unknown")

        if status_text == "completed":
            self.nav_status.setText("导航: 完成")
            if hasattr(self.right_panel, 'add_timestamped_log'):
                self.right_panel.add_timestamped_log("✅ 找书任务已完成", "INFO")
            elif hasattr(self.right_panel, 'add_log_entry'):
                self.right_panel.add_log_entry("✅ 找书任务已完成", "INFO")
        elif status_text == "cancelled":
            self.nav_status.setText("导航: 已取消")
            if hasattr(self.right_panel, 'add_timestamped_log'):
                self.right_panel.add_timestamped_log("⏹️ 找书任务已取消", "WARN")
            elif hasattr(self.right_panel, 'add_log_entry'):
                self.right_panel.add_log_entry("⏹️ 找书任务已取消", "WARN")
        elif status_text == "failed":
            self.nav_status.setText("导航: 失败")
            if hasattr(self.right_panel, 'add_timestamped_log'):
                self.right_panel.add_timestamped_log("❌ 找书任务失败", "ERROR")
            elif hasattr(self.right_panel, 'add_log_entry'):
                self.right_panel.add_log_entry("❌ 找书任务失败", "ERROR")
        elif status_text in ["navigating", "scanning", "approaching"]:
            self.nav_status.setText(f"导航: {status_text}")
            # 只在状态变化时记录日志，避免过于频繁
            if not hasattr(self, '_last_logged_status') or self._last_logged_status != status_text:
                progress = status.get("progress", 0)
                if hasattr(self.right_panel, 'add_timestamped_log'):
                    self.right_panel.add_timestamped_log(
                        f"🔄 任务状态更新: {status_text} ({progress:.1f}%)", "INFO"
                    )
                elif hasattr(self.right_panel, 'add_log_entry'):
                    self.right_panel.add_log_entry(
                        f"🔄 任务状态更新: {status_text} ({progress:.1f}%)", "INFO"
                    )
                self._last_logged_status = status_text

        # 更新进度到右侧面板
        if hasattr(self.right_panel, "update_task_status"):
            self.right_panel.update_task_status(status)

    def on_system_health_updated(self, health):
        """处理系统健康状态更新"""
        # 更新机器人状态
        if health.get("navigation_health", 1.0) < 0.8:
            self.robot_status.setText("机器人: 警告")
        else:
            self.robot_status.setText("机器人: 正常")

    def on_robot_pose_updated(self, pose):
        """处理机器人位置更新"""
        # 可以更新位置显示
        pass

    def on_error_occurred(self, error):
        """处理错误"""
        if hasattr(self.right_panel, 'add_timestamped_log'):
            self.right_panel.add_timestamped_log(
                f"❌ ROS2错误 [{error['error_code']}]: {error['message']}", "ERROR"
            )
        elif hasattr(self.right_panel, 'add_log_entry'):
            self.right_panel.add_log_entry(
                f"❌ ROS2错误 [{error['error_code']}]: {error['message']}", "ERROR"
            )

    def on_book_info_received(self, info):
        """处理图书信息接收"""
        if hasattr(self.right_panel, "update_book_info"):
            self.right_panel.update_book_info(info)

    def closeEvent(self, event):
        """窗口关闭时清理资源"""
        self.ros2_manager.shutdown()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
