#!/usr/bin/env python3
"""
自定义进度条组件 - 支持颜色动画和状态指示
Story 1-4: 状态显示和进度条实现
"""

from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPalette, QColor


class ProgressBar(QProgressBar):
    """自定义进度条 - 支持颜色动画和状态指示"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 100)
        self.setValue(0)
        self.setup_appearance()

        # 动画效果
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.setDuration(300)

    def setup_appearance(self):
        """设置外观"""
        self.setMinimumHeight(20)
        self.setFormat("%p% 完成")

        # 设置样式
        self.setStyleSheet("""
            QProgressBar {
                border: 2px solid #cccccc;
                border-radius: 10px;
                text-align: center;
                background-color: #f0f0f0;
            }

            QProgressBar::chunk {
                border-radius: 8px;
            }
        """)

    def set_progress(self, value, animate=True):
        """设置进度值

        Args:
            value: 进度值 (0-100)
            animate: 是否使用动画效果
        """
        # 限制范围
        value = max(0, min(100, value))

        if animate:
            self.animation.setStartValue(self.value())
            self.animation.setEndValue(int(value))
            self.animation.start()
        else:
            self.setValue(int(value))

        # 根据进度设置颜色
        self.update_color(value)

    def update_color(self, progress):
        """根据进度更新颜色"""
        if progress < 30:
            color = "#ff6b6b"  # 红色
        elif progress < 70:
            color = "#ffd93d"  # 黄色
        else:
            color = "#6bcf7f"  # 绿色

        self.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid #cccccc;
                border-radius: 10px;
                text-align: center;
                background-color: #f0f0f0;
            }}

            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 8px;
            }}
        """)

    def set_error_state(self):
        """设置为错误状态（红色）"""
        self.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ff6b6b;
                border-radius: 10px;
                text-align: center;
                background-color: #ffebee;
            }

            QProgressBar::chunk {
                background-color: #ff6b6b;
                border-radius: 8px;
            }
        """)

    def set_warning_state(self):
        """设置为警告状态（黄色）"""
        self.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ffd93d;
                border-radius: 10px;
                text-align: center;
                background-color: #fffbf0;
            }

            QProgressBar::chunk {
                background-color: #ffd93d;
                border-radius: 8px;
            }
        """)

    def set_success_state(self):
        """设置为成功状态（绿色）"""
        self.setStyleSheet("""
            QProgressBar {
                border: 2px solid #6bcf7f;
                border-radius: 10px;
                text-align: center;
                background-color: #f0fff4;
            }

            QProgressBar::chunk {
                background-color: #6bcf7f;
                border-radius: 8px;
            }
        """)

    def set_normal_state(self):
        """设置为正常状态"""
        self.setup_appearance()
        self.update_color(self.value())