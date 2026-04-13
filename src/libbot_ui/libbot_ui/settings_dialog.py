#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置对话框 - 用于配置UI的各种选项
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox,
    QPushButton, QLabel, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt
import json
import os


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setMinimumWidth(400)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """设置UI界面"""
        main_layout = QVBoxLayout(self)

        # 调试设置组
        debug_group = QGroupBox("调试选项")
        debug_layout = QFormLayout()

        # L1恢复调试复选框
        self.l1_debug_checkbox = QCheckBox("启用L1恢复调试功能")
        self.l1_debug_checkbox.setToolTip("显示RFID重扫、重定位等测试按钮")
        debug_layout.addRow(self.l1_debug_checkbox)

        # 添加更多调试选项的占位符
        self.extra_debug_checkbox = QCheckBox("启用额外调试信息")
        self.extra_debug_checkbox.setToolTip("在日志中显示更详细的调试信息")
        self.extra_debug_checkbox.setEnabled(False)  # 暂时禁用
        debug_layout.addRow(self.extra_debug_checkbox)

        debug_group.setLayout(debug_layout)
        main_layout.addWidget(debug_group)

        # 界面设置组
        ui_group = QGroupBox("界面选项")
        ui_layout = QFormLayout()

        # 日志级别设置
        self.log_level_checkbox = QCheckBox("显示详细日志")
        self.log_level_checkbox.setToolTip("显示INFO级别以上的所有日志")
        ui_layout.addRow(self.log_level_checkbox)

        ui_group.setLayout(ui_layout)
        main_layout.addWidget(ui_group)

        # 系统信息组
        info_group = QGroupBox("系统信息")
        info_layout = QFormLayout()

        # 版本信息
        version_label = QLabel("libbot控制面板 v1.0")
        info_layout.addRow("版本:", version_label)

        # ROS2连接状态
        self.ros2_status_label = QLabel("已连接")
        self.ros2_status_label.setStyleSheet("color: green;")
        info_layout.addRow("ROS2状态:", self.ros2_status_label)

        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)

        # 添加弹性空间
        main_layout.addStretch()

        # 按钮区域
        button_layout = QHBoxLayout()

        self.reset_btn = QPushButton("恢复默认")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(self.reset_btn)

        button_layout.addStretch()

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton("确定")
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)

        main_layout.addLayout(button_layout)

    def load_settings(self):
        """从配置文件加载设置"""
        settings = self._load_settings_from_file()

        # 设置复选框状态
        self.l1_debug_checkbox.setChecked(
            settings.get('l1_debug_enabled', False)
        )
        self.extra_debug_checkbox.setChecked(
            settings.get('extra_debug_enabled', False)
        )
        self.log_level_checkbox.setChecked(
            settings.get('detailed_logging', True)
        )

    def save_settings(self):
        """保存设置到配置文件"""
        settings = {
            'l1_debug_enabled': self.l1_debug_checkbox.isChecked(),
            'extra_debug_enabled': self.extra_debug_checkbox.isChecked(),
            'detailed_logging': self.log_level_checkbox.isChecked(),
            'last_updated': __import__('time').time()
        }

        self._save_settings_to_file(settings)

    def get_l1_debug_enabled(self):
        """获取L1调试是否启用"""
        return self.l1_debug_checkbox.isChecked()

    def reset_to_defaults(self):
        """恢复默认设置"""
        self.l1_debug_checkbox.setChecked(False)
        self.extra_debug_checkbox.setChecked(False)
        self.log_level_checkbox.setChecked(True)

    def _get_settings_file_path(self):
        """获取设置文件路径"""
        # 使用用户主目录下的配置文件
        home_dir = os.path.expanduser('~')
        config_dir = os.path.join(home_dir, '.libbot')

        # 确保配置目录存在
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        return os.path.join(config_dir, 'ui_settings.json')

    def _load_settings_from_file(self):
        """从文件加载设置"""
        settings_file = self._get_settings_file_path()

        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载设置失败: {e}")

        # 返回默认设置
        return {
            'l1_debug_enabled': False,
            'extra_debug_enabled': False,
            'detailed_logging': True
        }

    def _save_settings_to_file(self, settings):
        """保存设置到文件"""
        settings_file = self._get_settings_file_path()

        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存设置失败: {e}")

    def accept(self):
        """确定按钮点击"""
        self.save_settings()
        super().accept()


# 测试代码
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = SettingsDialog()

    if dialog.exec_() == QDialog.Accepted:
        print(f"L1调试启用: {dialog.get_l1_debug_enabled()}")

    sys.exit()