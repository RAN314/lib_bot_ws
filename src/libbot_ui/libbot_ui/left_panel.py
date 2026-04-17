#!/usr/bin/env python3
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
from PyQt5.QtCore import Qt, pyqtSignal


class LeftPanel(QWidget):
    """左侧面板 - 200px宽，包含功能按钮"""

    # 按钮点击信号
    find_book_clicked = pyqtSignal()
    inventory_clicked = pyqtSignal()
    cancel_clicked = pyqtSignal()  # 删除pause_clicked
    home_clicked = pyqtSignal()
    emergency_stop_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    logs_clicked = pyqtSignal()
    exit_clicked = pyqtSignal()

    # L1恢复信号
    l1_rfid_recovery_clicked = pyqtSignal()
    l1_localization_recovery_clicked = pyqtSignal()
    l1_target_redefinition_clicked = pyqtSignal()

    # L2恢复信号
    l2_costmap_recovery_clicked = pyqtSignal()
    l2_task_reset_recovery_clicked = pyqtSignal()
    l2_component_restart_recovery_clicked = pyqtSignal()
    l2_home_reset_recovery_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(200)
        self.setMaximumWidth(200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 任务控制
        self.add_task_group(layout)

        # 状态控制
        self.add_state_group(layout)

        # 系统控制
        self.add_system_group(layout)

        # L1恢复控制
        self.add_l1_recovery_group(layout)

        # L2恢复控制
        self.add_l2_recovery_group(layout)

        # 添加弹性空间
        layout.addStretch()

        # 连接按钮信号
        self.connect_signals()

    def add_task_group(self, layout):
        """添加任务控制按钮组"""
        frame = QFrame()
        frame.setObjectName("task_group")
        frame_layout = QVBoxLayout(frame)

        title = QLabel("任务控制")
        title.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(title)

        self.find_book_btn = QPushButton("🎯 找书")
        self.find_book_btn.setObjectName("find_book_btn")
        self.find_book_btn.setMinimumHeight(40)
        frame_layout.addWidget(self.find_book_btn)

        self.inventory_btn = QPushButton("📚 盘点")
        self.inventory_btn.setObjectName("inventory_btn")
        self.inventory_btn.setMinimumHeight(40)
        self.inventory_btn.setEnabled(False)  # 禁用盘点按钮
        frame_layout.addWidget(self.inventory_btn)

        # 删除暂停按钮
        self.cancel_btn = QPushButton("⏹️ 取消")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.setMinimumHeight(40)
        frame_layout.addWidget(self.cancel_btn)

        layout.addWidget(frame)

    def add_state_group(self, layout):
        """添加状态控制按钮组"""
        frame = QFrame()
        frame.setObjectName("state_group")
        frame_layout = QVBoxLayout(frame)

        title = QLabel("状态控制")
        title.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(title)

        self.home_btn = QPushButton("🏠 Home")
        self.home_btn.setObjectName("home_btn")
        self.home_btn.setMinimumHeight(40)
        frame_layout.addWidget(self.home_btn)

        self.emergency_stop_btn = QPushButton("🚨 急停")
        self.emergency_stop_btn.setObjectName("emergency_stop_btn")
        self.emergency_stop_btn.setMinimumHeight(40)
        self.emergency_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        frame_layout.addWidget(self.emergency_stop_btn)

        layout.addWidget(frame)

    def add_system_group(self, layout):
        """添加系统控制按钮组"""
        frame = QFrame()
        frame.setObjectName("system_group")
        frame_layout = QVBoxLayout(frame)

        title = QLabel("系统控制")
        title.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(title)

        self.settings_btn = QPushButton("⚙️ 设置")
        self.settings_btn.setObjectName("settings_btn")
        self.settings_btn.setMinimumHeight(35)
        frame_layout.addWidget(self.settings_btn)

        self.logs_btn = QPushButton("📝 日志")
        self.logs_btn.setObjectName("logs_btn")
        self.logs_btn.setMinimumHeight(35)
        frame_layout.addWidget(self.logs_btn)

        self.exit_btn = QPushButton("❌ 退出")
        self.exit_btn.setObjectName("exit_btn")
        self.exit_btn.setMinimumHeight(35)
        frame_layout.addWidget(self.exit_btn)

        layout.addWidget(frame)

    def add_l1_recovery_group(self, layout):
        """添加L1恢复控制按钮组"""
        frame = QFrame()
        frame.setObjectName("l1_recovery_group")
        frame_layout = QVBoxLayout(frame)

        title = QLabel("L1恢复测试")
        title.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(title)

        self.l1_rfid_recovery_btn = QPushButton("📡 RFID重扫")
        self.l1_rfid_recovery_btn.setObjectName("l1_rfid_recovery_btn")
        self.l1_rfid_recovery_btn.setMinimumHeight(35)
        frame_layout.addWidget(self.l1_rfid_recovery_btn)

        self.l1_localization_recovery_btn = QPushButton("🎯 重定位")
        self.l1_localization_recovery_btn.setObjectName("l1_localization_recovery_btn")
        self.l1_localization_recovery_btn.setMinimumHeight(35)
        frame_layout.addWidget(self.l1_localization_recovery_btn)

        self.l1_target_redefinition_btn = QPushButton("🔄 目标重定义")
        self.l1_target_redefinition_btn.setObjectName("l1_target_redefinition_btn")
        self.l1_target_redefinition_btn.setMinimumHeight(35)
        frame_layout.addWidget(self.l1_target_redefinition_btn)

        layout.addWidget(frame)

    def add_l2_recovery_group(self, layout):
        """添加L2恢复控制按钮组"""
        frame = QFrame()
        frame.setObjectName("l2_recovery_group")
        frame_layout = QVBoxLayout(frame)

        title = QLabel("L2恢复测试")
        title.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(title)

        self.l2_costmap_recovery_btn = QPushButton("🗺️ 代价地图重置")
        self.l2_costmap_recovery_btn.setObjectName("l2_costmap_recovery_btn")
        self.l2_costmap_recovery_btn.setMinimumHeight(35)
        frame_layout.addWidget(self.l2_costmap_recovery_btn)

        self.l2_task_reset_recovery_btn = QPushButton("📋 任务重置")
        self.l2_task_reset_recovery_btn.setObjectName("l2_task_reset_recovery_btn")
        self.l2_task_reset_recovery_btn.setMinimumHeight(35)
        frame_layout.addWidget(self.l2_task_reset_recovery_btn)

        self.l2_component_restart_recovery_btn = QPushButton("🔧 组件重启")
        self.l2_component_restart_recovery_btn.setObjectName("l2_component_restart_recovery_btn")
        self.l2_component_restart_recovery_btn.setMinimumHeight(35)
        frame_layout.addWidget(self.l2_component_restart_recovery_btn)

        self.l2_home_reset_recovery_btn = QPushButton("🏠 Home重置")
        self.l2_home_reset_recovery_btn.setObjectName("l2_home_reset_recovery_btn")
        self.l2_home_reset_recovery_btn.setMinimumHeight(35)
        frame_layout.addWidget(self.l2_home_reset_recovery_btn)

        layout.addWidget(frame)

    def connect_signals(self):
        """连接按钮信号"""
        self.find_book_btn.clicked.connect(self.find_book_clicked.emit)
        self.inventory_btn.clicked.connect(self.inventory_clicked.emit)
        # 删除pause_btn连接
        self.cancel_btn.clicked.connect(self.cancel_clicked.emit)
        self.home_btn.clicked.connect(self.home_clicked.emit)
        self.emergency_stop_btn.clicked.connect(self.emergency_stop_clicked.emit)
        self.settings_btn.clicked.connect(self.settings_clicked.emit)
        self.logs_btn.clicked.connect(self.logs_clicked.emit)
        self.exit_btn.clicked.connect(self.exit_clicked.emit)

        # L1恢复按钮信号
        self.l1_rfid_recovery_btn.clicked.connect(self.l1_rfid_recovery_clicked.emit)
        self.l1_localization_recovery_btn.clicked.connect(self.l1_localization_recovery_clicked.emit)
        self.l1_target_redefinition_btn.clicked.connect(self.l1_target_redefinition_clicked.emit)

        # L2恢复按钮信号
        self.l2_costmap_recovery_btn.clicked.connect(self.l2_costmap_recovery_clicked.emit)
        self.l2_task_reset_recovery_btn.clicked.connect(self.l2_task_reset_recovery_clicked.emit)
        self.l2_component_restart_recovery_btn.clicked.connect(self.l2_component_restart_recovery_clicked.emit)
        self.l2_home_reset_recovery_btn.clicked.connect(self.l2_home_reset_recovery_clicked.emit)

    def get_find_book_button(self):
        """获取找书按钮（供MainWindow连接）"""
        return self.find_book_btn

    def set_l1_recovery_visible(self, visible):
        """设置L1恢复按钮组的可见性

        Args:
            visible: 是否显示L1恢复按钮组
        """
        # 查找L1恢复组框架
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QFrame) and widget.objectName() == "l1_recovery_group":
                widget.setVisible(visible)
                break

    def set_l2_recovery_visible(self, visible):
        """设置L2恢复按钮组的可见性

        Args:
            visible: 是否显示L2恢复按钮组
        """
        # 查找L2恢复组框架
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QFrame) and widget.objectName() == "l2_recovery_group":
                widget.setVisible(visible)
                break

    def is_l1_recovery_visible(self):
        """检查L1恢复按钮组是否可见

        Returns:
            bool: L1恢复按钮组是否可见
        """
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QFrame) and widget.objectName() == "l1_recovery_group":
                return widget.isVisible()
        return False

    def is_l2_recovery_visible(self):
        """检查L2恢复按钮组是否可见

        Returns:
            bool: L2恢复按钮组是否可见
        """
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QFrame) and widget.objectName() == "l2_recovery_group":
                return widget.isVisible()
        return False
