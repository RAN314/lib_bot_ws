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
)
from PyQt5.QtCore import Qt, QTimer
from .left_panel import LeftPanel
from .right_panel import RightPanel
from .ros2_manager import Ros2Manager


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
        self.left_panel.find_book_clicked.connect(self.on_find_book_clicked)
        self.left_panel.cancel_clicked.connect(self.on_cancel_clicked)
        self.left_panel.exit_clicked.connect(self.close)

        # 更新连接状态
        self.connection_status.setText("已连接")

    def on_find_book_clicked(self):
        """找书按钮点击处理"""
        # TODO: 打开对话框获取图书ID，目前使用测试ID
        success = self.ros2_manager.send_find_book_goal("test_book_001")
        if success and hasattr(self.right_panel, "add_log_entry"):
            self.right_panel.add_log_entry("已发送找书请求: test_book_001", "info")

    def on_cancel_clicked(self):
        """取消按钮点击处理"""
        success = self.ros2_manager.cancel_current_goal()
        if success and hasattr(self.right_panel, "add_log_entry"):
            self.right_panel.add_log_entry("已发送取消请求", "warning")

    def on_task_status_updated(self, status):
        """处理任务状态更新"""
        if status.get("status") == "completed":
            self.nav_status.setText("导航: 完成")
        elif status.get("status") == "cancelled":
            self.nav_status.setText("导航: 已取消")
        elif status.get("status"):
            self.nav_status.setText(f"导航: {status['status']}")

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
        if hasattr(self.right_panel, "add_log_entry"):
            self.right_panel.add_log_entry(
                f"错误: {error['error_code']} - {error['message']}", "error"
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
