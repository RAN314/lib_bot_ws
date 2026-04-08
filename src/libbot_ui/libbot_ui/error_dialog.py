#!/usr/bin/env python3

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