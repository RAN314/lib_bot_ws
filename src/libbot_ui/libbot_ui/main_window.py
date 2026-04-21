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
from .settings_dialog import SettingsDialog


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

        # 对话框
        book_database_file = "/home/lhl/lib_bot_ws/src/libbot_ui/config/book_database.yaml"
        self.find_book_dialog = FindBookDialog(self, self.ros2_manager, book_database_file)
        self.settings_dialog = None

        # 调试模式状态
        self.debug_mode_enabled = False

        self.setup_ros2_connections()

        # 初始隐藏L1和L2恢复按钮组
        self.update_l1_recovery_visibility()
        self.update_l2_recovery_visibility()

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
        # 任务状态更新（使用queued connection确保线程安全）
        self.ros2_manager.task_status_updated.connect(
            self.on_task_status_updated,
            type=Qt.QueuedConnection
        )

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
        self.left_panel.settings_clicked.connect(self.show_settings_dialog)
        # 删除pause_clicked连接
        self.left_panel.exit_clicked.connect(self.close)

        # L1恢复按钮信号
        self.left_panel.l1_rfid_recovery_clicked.connect(self.on_l1_rfid_recovery_clicked)
        self.left_panel.l1_localization_recovery_clicked.connect(self.on_l1_localization_recovery_clicked)
        self.left_panel.l1_target_redefinition_clicked.connect(self.on_l1_target_redefinition_clicked)

        # L2恢复按钮信号
        self.left_panel.l2_costmap_recovery_clicked.connect(self.on_l2_costmap_recovery_clicked)
        self.left_panel.l2_task_reset_recovery_clicked.connect(self.on_l2_task_reset_recovery_clicked)
        self.left_panel.l2_component_restart_recovery_clicked.connect(self.on_l2_component_restart_recovery_clicked)
        self.left_panel.l2_home_reset_recovery_clicked.connect(self.on_l2_home_reset_recovery_clicked)

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

    def show_settings_dialog(self):
        """显示设置对话框"""
        if self.settings_dialog is None:
            self.settings_dialog = SettingsDialog(self)

        # 执行对话框并检查结果
        result = self.settings_dialog.exec_()

        if result == SettingsDialog.Accepted:
            # 更新调试模式状态
            old_debug_mode = self.debug_mode_enabled
            self.debug_mode_enabled = self.settings_dialog.get_l1_debug_enabled()

            # 如果调试模式状态发生变化，更新UI
            if old_debug_mode != self.debug_mode_enabled:
                self.update_l1_recovery_visibility()
                self.update_l2_recovery_visibility()

                # 记录状态变化
                status = "启用" if self.debug_mode_enabled else "禁用"
                if hasattr(self.right_panel, 'add_timestamped_log'):
                    self.right_panel.add_timestamped_log(
                        f"🔧 L1/L2恢复调试功能已{status}", "INFO"
                    )
                elif hasattr(self.right_panel, 'add_log_entry'):
                    self.right_panel.add_log_entry(
                        f"🔧 L1/L2恢复调试功能已{status}", "INFO"
                    )

    def on_find_book_confirmed(self, book_id, guide_patron):
        """找书确认处理"""
        # 首先查找书籍位置信息
        book_database_file = "/home/lhl/lib_bot_ws/src/libbot_ui/config/book_database.yaml"
        book_info = self.ros2_manager.find_book_by_id(book_id, book_database_file)

        if book_info and 'position' in book_info:
            # 使用位置信息进行导航
            position = book_info['position']
            success = self.ros2_manager.send_find_book_goal_with_position(
                book_id, position, guide_patron
            )

            if success:
                # 在日志面板显示任务已发送
                if hasattr(self.right_panel, 'add_timestamped_log'):
                    self.right_panel.add_timestamped_log(
                        f"🎯 找书任务已发送: {book_id} 位置({position['x']:.1f}, {position['y']:.1f}) (引导读者: {'是' if guide_patron else '否'})",
                        "INFO"
                    )
                elif hasattr(self.right_panel, 'add_log_entry'):
                    self.right_panel.add_log_entry(
                        f"🎯 找书任务已发送: {book_id} 位置({position['x']:.1f}, {position['y']:.1f}) (引导读者: {'是' if guide_patron else '否'})",
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
        else:
            # 书籍信息未找到，使用传统方式
            if hasattr(self.right_panel, 'add_timestamped_log'):
                self.right_panel.add_timestamped_log(
                    f"⚠️ 书籍 {book_id} 位置信息未找到，使用传统找书模式",
                    "WARN"
                )

            success = self.ros2_manager.send_find_book_goal(book_id, guide_patron)

            if success:
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

    def on_l1_rfid_recovery_clicked(self):
        """L1 RFID恢复按钮点击处理"""
        # 使用测试数据触发RFID恢复
        test_book_id = "test_book_001"
        test_position = {'x': 1.0, 'y': 2.0, 'z': 0.0}

        self.ros2_manager.trigger_l1_rfid_recovery(test_book_id, test_position)

        if hasattr(self.right_panel, 'add_timestamped_log'):
            self.right_panel.add_timestamped_log(
                f"🔧 手动触发L1 RFID恢复: {test_book_id}", "INFO"
            )
        elif hasattr(self.right_panel, 'add_log_entry'):
            self.right_panel.add_log_entry(
                f"🔧 手动触发L1 RFID恢复: {test_book_id}", "INFO"
            )

    def on_l1_localization_recovery_clicked(self):
        """L1定位恢复按钮点击处理"""
        self.ros2_manager.trigger_l1_localization_recovery()

        if hasattr(self.right_panel, 'add_timestamped_log'):
            self.right_panel.add_timestamped_log(
                "🔧 手动触发L1定位恢复", "INFO"
            )
        elif hasattr(self.right_panel, 'add_log_entry'):
            self.right_panel.add_log_entry(
                "🔧 手动触发L1定位恢复", "INFO"
            )

    def on_l1_target_redefinition_clicked(self):
        """L1目标重定义按钮点击处理"""
        # 使用测试数据触发目标重定义
        test_goal = {
            'book_id': 'test_original_book',
            'position': {'x': 5.0, 'y': 3.0, 'z': 0.0}
        }

        self.ros2_manager.trigger_l1_target_redefinition(test_goal)

        if hasattr(self.right_panel, 'add_timestamped_log'):
            self.right_panel.add_timestamped_log(
                f"🔧 手动触发L1目标重定义: {test_goal['book_id']}", "INFO"
            )
        elif hasattr(self.right_panel, 'add_log_entry'):
            self.right_panel.add_log_entry(
                f"🔧 手动触发L1目标重定义: {test_goal['book_id']}", "INFO"
            )

    def on_l2_costmap_recovery_clicked(self):
        """L2代价地图恢复按钮点击处理"""
        # 使用测试数据触发L2代价地图恢复
        test_goal = {'x': 5.0, 'y': 3.0, 'z': 0.0}

        self.ros2_manager.trigger_l2_costmap_recovery(test_goal)

        if hasattr(self.right_panel, 'add_timestamped_log'):
            self.right_panel.add_timestamped_log(
                f"🔧 手动触发L2代价地图恢复: ({test_goal['x']}, {test_goal['y']})", "INFO"
            )
        elif hasattr(self.right_panel, 'add_log_entry'):
            self.right_panel.add_log_entry(
                f"🔧 手动触发L2代价地图恢复: ({test_goal['x']}, {test_goal['y']})", "INFO"
            )

    def on_l2_task_reset_recovery_clicked(self):
        """L2任务重置恢复按钮点击处理"""
        # 使用测试数据触发L2任务重置
        test_task = {
            'task_id': 'test_task_002',
            'progress': 60,
            'books_detected': ['book_001', 'book_002'],
            'navigation_attempts': 2,
            'scan_attempts': 4
        }

        self.ros2_manager.trigger_l2_task_reset_recovery(test_task)

        if hasattr(self.right_panel, 'add_timestamped_log'):
            self.right_panel.add_timestamped_log(
                f"🔧 手动触发L2任务重置恢复: {test_task['task_id']}", "INFO"
            )
        elif hasattr(self.right_panel, 'add_log_entry'):
            self.right_panel.add_log_entry(
                f"🔧 手动触发L2任务重置恢复: {test_task['task_id']}", "INFO"
            )

    def on_l2_component_restart_recovery_clicked(self):
        """L2组件重启恢复按钮点击处理"""
        # 使用默认组件列表触发L2组件重启
        self.ros2_manager.trigger_l2_component_restart_recovery()

        if hasattr(self.right_panel, 'add_timestamped_log'):
            self.right_panel.add_timestamped_log(
                "🔧 手动触发L2组件重启恢复", "INFO"
            )
        elif hasattr(self.right_panel, 'add_log_entry'):
            self.right_panel.add_log_entry(
                "🔧 手动触发L2组件重启恢复", "INFO"
            )

    def on_l2_home_reset_recovery_clicked(self):
        """L2返回Home重置恢复按钮点击处理"""
        self.ros2_manager.trigger_l2_home_reset_recovery()

        if hasattr(self.right_panel, 'add_timestamped_log'):
            self.right_panel.add_timestamped_log(
                "🔧 手动触发L2返回Home重置恢复", "INFO"
            )
        elif hasattr(self.right_panel, 'add_log_entry'):
            self.right_panel.add_log_entry(
                "🔧 手动触发L2返回Home重置恢复", "INFO"
            )

    def on_task_status_updated(self, status):
        """处理任务状态更新"""
        # 调试：打印收到的状态
        print(f"[DEBUG] 主窗口收到状态更新: {status.get('status', 'unknown')}, 进度: {status.get('progress', 0)}%")

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

        # L1恢复状态处理
        elif status_text.startswith("l1_"):
            recovery_type = status.get("recovery_type", "unknown")
            recovery_status = status.get("recovery_status", "unknown")

            if status_text == "l1_started":
                self.nav_status.setText(f"🔧 L1恢复: {recovery_type}")
                if hasattr(self.right_panel, 'add_timestamped_log'):
                    self.right_panel.add_timestamped_log(
                        f"🔧 L1恢复开始: {recovery_type}", "INFO"
                    )
                elif hasattr(self.right_panel, 'add_log_entry'):
                    self.right_panel.add_log_entry(
                        f"🔧 L1恢复开始: {recovery_type}", "INFO"
                    )

            elif status_text == "l1_in_progress":
                self.nav_status.setText(f"🔧 L1恢复中: {recovery_type}")
                # 只在状态变化时记录日志
                if not hasattr(self, '_last_recovery_status') or self._last_recovery_status != recovery_status:
                    if hasattr(self.right_panel, 'add_timestamped_log'):
                        self.right_panel.add_timestamped_log(
                            f"🔄 L1恢复执行中: {recovery_type}", "INFO"
                        )
                    elif hasattr(self.right_panel, 'add_log_entry'):
                        self.right_panel.add_log_entry(
                            f"🔄 L1恢复执行中: {recovery_type}", "INFO"
                        )
                    self._last_recovery_status = recovery_status

            elif status_text == "l1_recovery_completed":
                success = status.get("success", False)
                status_icon = "✅" if success else "❌"
                status_msg = "成功" if success else "失败"

                self.nav_status.setText(f"🔧 L1恢复: {status_msg}")
                if hasattr(self.right_panel, 'add_timestamped_log'):
                    self.right_panel.add_timestamped_log(
                        f"{status_icon} L1恢复完成: {recovery_type} {status_msg}",
                        "INFO" if success else "WARN"
                    )
                elif hasattr(self.right_panel, 'add_log_entry'):
                    self.right_panel.add_log_entry(
                        f"{status_icon} L1恢复完成: {recovery_type} {status_msg}",
                        "INFO" if success else "WARN"
                    )

        # L2恢复状态处理
        elif status_text.startswith("l2_"):
            recovery_type = status.get("recovery_type", "unknown")
            recovery_status = status.get("recovery_status", "unknown")
            recovery_level = status.get("recovery_level", "L2")
            elapsed_time = status.get("elapsed_time", 0.0)

            if status_text == "l2_started":
                self.nav_status.setText(f"🔧 {recovery_level}恢复: {recovery_type}")
                if hasattr(self.right_panel, 'add_timestamped_log'):
                    self.right_panel.add_timestamped_log(
                        f"🔧 {recovery_level}恢复开始: {recovery_type}", "INFO"
                    )
                elif hasattr(self.right_panel, 'add_log_entry'):
                    self.right_panel.add_log_entry(
                        f"🔧 {recovery_level}恢复开始: {recovery_type}", "INFO"
                    )

            elif status_text == "l2_in_progress":
                self.nav_status.setText(f"🔧 {recovery_level}恢复中: {recovery_type}")
                # 只在状态变化时记录日志
                if not hasattr(self, '_last_l2_recovery_status') or self._last_l2_recovery_status != recovery_status:
                    if hasattr(self.right_panel, 'add_timestamped_log'):
                        self.right_panel.add_timestamped_log(
                            f"🔄 {recovery_level}恢复执行中: {recovery_type} (耗时: {elapsed_time:.1f}s)", "INFO"
                        )
                    elif hasattr(self.right_panel, 'add_log_entry'):
                        self.right_panel.add_log_entry(
                            f"🔄 {recovery_level}恢复执行中: {recovery_type} (耗时: {elapsed_time:.1f}s)", "INFO"
                        )
                    self._last_l2_recovery_status = recovery_status

            elif status_text == "l2_recovery_completed":
                success = status.get("success", False)
                duration = status.get("duration", 0.0)
                status_icon = "✅" if success else "❌"
                status_msg = "成功" if success else "失败"

                self.nav_status.setText(f"🔧 {recovery_level}恢复: {status_msg}")
                if hasattr(self.right_panel, 'add_timestamped_log'):
                    self.right_panel.add_timestamped_log(
                        f"{status_icon} {recovery_level}恢复完成: {recovery_type} {status_msg} (耗时: {duration:.1f}s)",
                        "INFO" if success else "WARN"
                    )
                elif hasattr(self.right_panel, 'add_log_entry'):
                    self.right_panel.add_log_entry(
                        f"{status_icon} {recovery_level}恢复完成: {recovery_type} {status_msg} (耗时: {duration:.1f}s)",
                        "INFO" if success else "WARN"
                    )

            elif status_text == "escalated_to_l3":
                reason = status.get("reason", "未知原因")
                self.nav_status.setText("⚠️ 升级到L3恢复")
                if hasattr(self.right_panel, 'add_timestamped_log'):
                    self.right_panel.add_timestamped_log(
                        f"⚠️ L2恢复失败，升级到L3: {reason}", "WARN"
                    )
                elif hasattr(self.right_panel, 'add_log_entry'):
                    self.right_panel.add_log_entry(
                        f"⚠️ L2恢复失败，升级到L3: {reason}", "WARN"
                    )

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

    def update_l1_recovery_visibility(self):
        """更新L1恢复按钮组的可见性"""
        self.left_panel.set_l1_recovery_visible(self.debug_mode_enabled)

    def update_l2_recovery_visibility(self):
        """更新L2恢复按钮组的可见性"""
        self.left_panel.set_l2_recovery_visible(self.debug_mode_enabled)

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
