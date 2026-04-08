#!/usr/bin/env python3
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
from PyQt5.QtCore import Qt, pyqtSignal


class LeftPanel(QWidget):
    """左侧面板 - 200px宽，包含功能按钮"""

    # 按钮点击信号
    find_book_clicked = pyqtSignal()
    inventory_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    cancel_clicked = pyqtSignal()
    home_clicked = pyqtSignal()
    emergency_stop_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    logs_clicked = pyqtSignal()
    exit_clicked = pyqtSignal()

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
        frame_layout.addWidget(self.inventory_btn)

        self.pause_btn = QPushButton("⏸️ 暂停")
        self.pause_btn.setObjectName("pause_btn")
        self.pause_btn.setMinimumHeight(40)
        frame_layout.addWidget(self.pause_btn)

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

    def connect_signals(self):
        """连接按钮信号"""
        self.find_book_btn.clicked.connect(self.find_book_clicked.emit)
        self.inventory_btn.clicked.connect(self.inventory_clicked.emit)
        self.pause_btn.clicked.connect(self.pause_clicked.emit)
        self.cancel_btn.clicked.connect(self.cancel_clicked.emit)
        self.home_btn.clicked.connect(self.home_clicked.emit)
        self.emergency_stop_btn.clicked.connect(self.emergency_stop_clicked.emit)
        self.settings_btn.clicked.connect(self.settings_clicked.emit)
        self.logs_btn.clicked.connect(self.logs_clicked.emit)
        self.exit_btn.clicked.connect(self.exit_clicked.emit)
