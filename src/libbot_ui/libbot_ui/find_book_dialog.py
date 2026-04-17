#!/usr/bin/env python3
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QCheckBox, QPushButton, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence


class FindBookDialog(QDialog):
    """找书对话框 - 输入图书信息并发起找书任务"""

    # 信号：用户确认找书
    find_book_confirmed = pyqtSignal(str, bool)  # (book_id, guide_patron)

    def __init__(self, parent=None, ros2_manager=None):
        """初始化找书对话框

        Args:
            parent: 父窗口
            ros2_manager: Ros2Manager实例（用于历史记录）
        """
        super().__init__(parent)
        self.ros2_manager = ros2_manager
        self.setup_ui()
        self.load_history()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("查找图书")
        self.setModal(True)
        self.resize(400, 200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 图书ID输入
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("图书ID:"))

        # 支持输入和历史记录下拉
        self.book_id_combo = QComboBox()
        self.book_id_combo.setEditable(True)
        self.book_id_combo.setMinimumWidth(250)
        self.book_id_combo.setPlaceholderText("输入或选择图书ID...")
        id_layout.addWidget(self.book_id_combo)

        layout.addLayout(id_layout)

        # 引导读者选项
        self.guide_patron_check = QCheckBox("引导读者前往图书位置")
        self.guide_patron_check.setChecked(False)
        layout.addWidget(self.guide_patron_check)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_button = QPushButton("确定")
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.on_ok_clicked)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        # 设置快捷键
        self.ok_button.setShortcut(QKeySequence(Qt.Key_Return))
        self.cancel_button.setShortcut(QKeySequence(Qt.Key_Escape))

    def load_history(self):
        """加载历史记录"""
        # TODO: 从SQLite数据库加载最近5本查找的图书
        # 临时使用示例数据
        sample_books = [
            "9787115426273",
            "9787115426274",
            "9787115426275"
        ]
        self.book_id_combo.addItems(sample_books)

    def on_ok_clicked(self):
        """确定按钮点击处理"""
        book_id = self.book_id_combo.currentText().strip()

        if not book_id:
            # TODO: 显示错误提示
            return

        guide_patron = self.guide_patron_check.isChecked()

        # 发射信号
        self.find_book_confirmed.emit(book_id, guide_patron)

        # 保存到历史记录
        self.save_to_history(book_id)

        self.accept()

    def save_to_history(self, book_id):
        """保存到历史记录"""
        # TODO: 保存到SQLite数据库
        # 更新combobox
        index = self.book_id_combo.findText(book_id)
        if index >= 0:
            self.book_id_combo.removeItem(index)
        self.book_id_combo.insertItem(0, book_id)
        self.book_id_combo.setCurrentIndex(0)

        # 限制历史记录数量
        while self.book_id_combo.count() > 5:
            self.book_id_combo.removeItem(self.book_id_combo.count() - 1)

    def showEvent(self, event):
        """显示事件"""
        super().showEvent(event)
        # 聚焦到输入框
        self.book_id_combo.setFocus()
        self.book_id_combo.lineEdit().selectAll()