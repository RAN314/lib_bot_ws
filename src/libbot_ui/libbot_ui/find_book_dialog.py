#!/usr/bin/env python3
import yaml
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QCheckBox, QPushButton, QComboBox,
    QGroupBox, QFormLayout, QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QKeySequence


class BookDatabase(QObject):
    """书籍数据库管理类"""

    def __init__(self, database_file=None):
        super().__init__()
        self.database_file = database_file
        self.books = {}
        self.load_database()

    def load_database(self):
        """加载书籍数据库"""
        if self.database_file and os.path.exists(self.database_file):
            try:
                with open(self.database_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    self.books = data.get('books', {})
            except Exception as e:
                print(f"加载书籍数据库失败: {e}")
                self.books = {}
        else:
            # 使用默认示例数据
            self.books = {
                "BK001": {
                    "title": "人工智能导论",
                    "author": "张三",
                    "isbn": "978-7-111-12345-6",
                    "position": {"x": 2.5, "y": 1.8, "z": 0.0},
                    "shelf_zone": "A",
                    "shelf_level": 2
                },
                "BK002": {
                    "title": "机器学习实战",
                    "author": "李四",
                    "isbn": "978-7-111-54321-0",
                    "position": {"x": 4.2, "y": 3.1, "z": 0.0},
                    "shelf_zone": "B",
                    "shelf_level": 1
                }
            }

    def get_book_info(self, book_id):
        """获取书籍信息"""
        return self.books.get(book_id)

    def search_books(self, keyword):
        """搜索书籍"""
        results = []
        keyword = keyword.lower()
        for book_id, info in self.books.items():
            if (keyword in book_id.lower() or
                keyword in info.get('title', '').lower() or
                keyword in info.get('author', '').lower()):
                results.append((book_id, info))
        return results


class FindBookDialog(QDialog):
    """找书对话框 - 输入图书信息并发起找书任务"""

    # 信号：用户确认找书
    find_book_confirmed = pyqtSignal(str, bool)  # (book_id, guide_patron)

    def __init__(self, parent=None, ros2_manager=None, book_database_file=None):
        """初始化找书对话框

        Args:
            parent: 父窗口
            ros2_manager: Ros2Manager实例（用于历史记录）
            book_database_file: 书籍数据库文件路径
        """
        super().__init__(parent)
        self.ros2_manager = ros2_manager

        # 初始化书籍数据库
        self.book_database = BookDatabase(book_database_file)

        self.setup_ui()
        self.load_book_list()
        self.load_history()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("查找图书")
        self.setModal(True)
        self.resize(500, 400)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 图书搜索输入
        search_group = QGroupBox("图书搜索")
        search_layout = QFormLayout()

        # 支持输入和历史记录下拉
        self.book_id_combo = QComboBox()
        self.book_id_combo.setEditable(True)
        self.book_id_combo.setMinimumWidth(300)
        self.book_id_combo.setPlaceholderText("输入图书ID、书名或作者进行搜索...")
        self.book_id_combo.currentTextChanged.connect(self.on_book_id_changed)
        search_layout.addRow("图书搜索:", self.book_id_combo)

        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # 图书信息显示
        info_group = QGroupBox("图书信息")
        info_layout = QFormLayout()

        self.title_label = QLabel("未知")
        self.author_label = QLabel("未知")
        self.isbn_label = QLabel("未知")
        self.location_label = QLabel("未知")

        info_layout.addRow("书名:", self.title_label)
        info_layout.addRow("作者:", self.author_label)
        info_layout.addRow("ISBN:", self.isbn_label)
        info_layout.addRow("位置:", self.location_label)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # 引导读者选项
        self.guide_patron_check = QCheckBox("引导读者前往图书位置")
        self.guide_patron_check.setChecked(False)
        layout.addWidget(self.guide_patron_check)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_button = QPushButton("开始找书")
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

    def load_book_list(self):
        """加载书籍列表"""
        # 添加所有书籍ID到下拉框
        for book_id in sorted(self.book_database.books.keys()):
            book_info = self.book_database.books[book_id]
            title = book_info.get('title', '未知书名')
            display_text = f"{book_id} - {title}"
            self.book_id_combo.addItem(display_text, book_id)

    def load_history(self):
        """加载历史记录"""
        # TODO: 从SQLite数据库加载最近5本查找的图书
        # 临时使用示例数据
        sample_books = [
            "BK001",
            "BK002",
            "BK003"
        ]
        for book_id in sample_books:
            if book_id in self.book_database.books:
                title = self.book_database.books[book_id].get('title', '未知书名')
                display_text = f"{book_id} - {title}"
                self.book_id_combo.addItem(display_text, book_id)

    def on_book_id_changed(self, text):
        """图书ID改变时的处理"""
        # 从组合框中获取实际的book_id（去掉显示文本）
        current_data = self.book_id_combo.currentData()
        book_id = current_data if current_data else text

        # 查询书籍信息
        book_info = self.book_database.get_book_info(book_id)
        if book_info:
            self.title_label.setText(book_info.get('title', '未知'))
            self.author_label.setText(book_info.get('author', '未知'))
            self.isbn_label.setText(book_info.get('isbn', '未知'))

            # 显示位置信息
            pos = book_info.get('position', {})
            zone = book_info.get('shelf_zone', '未知')
            level = book_info.get('shelf_level', 0)
            location_text = f"区域{zone}-第{level}层 (x:{pos.get('x', 0):.1f}, y:{pos.get('y', 0):.1f})"
            self.location_label.setText(location_text)

            # 启用确定按钮
            self.ok_button.setEnabled(True)
        else:
            # 清除信息
            self.title_label.setText("未知")
            self.author_label.setText("未知")
            self.isbn_label.setText("未知")
            self.location_label.setText("未知")

            # 如果输入的ID不存在，禁用确定按钮
            if text and not current_data:
                self.ok_button.setEnabled(False)
            else:
                self.ok_button.setEnabled(True)

    def on_ok_clicked(self):
        """确定按钮点击处理"""
        # 获取实际的book_id
        current_data = self.book_id_combo.currentData()
        if current_data:
            book_id = current_data
        else:
            book_id = self.book_id_combo.currentText().strip()

        if not book_id:
            # TODO: 显示错误提示
            return

        # 验证书籍是否存在
        book_info = self.book_database.get_book_info(book_id)
        if not book_info:
            # TODO: 显示错误提示 - 书籍不存在
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
        # 更新combobox - 将使用的书籍移到顶部
        for i in range(self.book_id_combo.count()):
            if self.book_id_combo.itemData(i) == book_id:
                self.book_id_combo.removeItem(i)
                break

        # 添加到顶部
        if book_id in self.book_database.books:
            title = self.book_database.books[book_id].get('title', '未知书名')
            display_text = f"{book_id} - {title}"
            self.book_id_combo.insertItem(0, display_text, book_id)
            self.book_id_combo.setCurrentIndex(0)

    def showEvent(self, event):
        """显示事件"""
        super().showEvent(event)
        # 聚焦到输入框
        self.book_id_combo.setFocus()
        self.book_id_combo.lineEdit().selectAll()