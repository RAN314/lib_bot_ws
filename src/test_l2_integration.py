#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L2恢复完整集成测试脚本
验证L2恢复功能与UI的完整集成
"""

import sys
import os
import time
import threading

# 添加模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libbot_ui'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libbot_tasks'))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from libbot_ui.main_window import MainWindow

def test_l2_integration():
    """完整的L2恢复集成测试"""
    print("🧪 开始L2恢复完整集成测试")

    # 创建Qt应用
    app = QApplication(sys.argv)

    # 创建主窗口
    window = MainWindow()

    # 启用调试模式以显示L2恢复按钮
    window.debug_mode_enabled = True
    window.update_l1_recovery_visibility()
    window.update_l2_recovery_visibility()

    # 显示窗口
    window.show()

    # 测试L2恢复功能
    def test_l2_recovery_buttons():
        print("\n=== 测试L2恢复按钮 ===")

        # 模拟点击L2恢复按钮
        print("1. 触发L2代价地图恢复...")
        window.on_l2_costmap_recovery_clicked()

        time.sleep(2)

        print("2. 触发L2任务重置恢复...")
        window.on_l2_task_reset_recovery_clicked()

        time.sleep(2)

        print("3. 触发L2组件重启恢复...")
        window.on_l2_component_restart_recovery_clicked()

        time.sleep(2)

        print("4. 触发L2返回Home重置恢复...")
        window.on_l2_home_reset_recovery_clicked()

        time.sleep(3)

        print("✅ L2恢复按钮测试完成")

        # 关闭应用
        QTimer.singleShot(1000, app.quit)

    # 延迟启动测试
    QTimer.singleShot(1000, test_l2_recovery_buttons)

    # 运行应用
    exit_code = app.exec_()

    print("\n✅ L2恢复完整集成测试完成")
    return exit_code

if __name__ == "__main__":
    try:
        exit_code = test_l2_integration()
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        sys.exit(1)