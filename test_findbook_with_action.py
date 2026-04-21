#!/usr/bin/env python3
"""
测试使用NavigateToPose Action的找书功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src/libbot_ui'))

from libbot_ui.libbot_ui.find_book_dialog import BookDatabase
from libbot_ui.libbot_ui.ros2_manager import Ros2Manager
import rclpy

def test_findbook_with_action():
    """测试使用Action的找书功能"""
    print("🚀 开始测试使用NavigateToPose Action的找书功能")
    print("=" * 60)

    # 初始化ROS2
    try:
        rclpy.init()
        print("✅ ROS2初始化成功")
    except Exception as e:
        print(f"❌ ROS2初始化失败: {e}")
        return

    # 测试书籍数据库
    print("\n🧪 测试书籍数据库...")
    database_file = "/home/lhl/lib_bot_ws/src/libbot_ui/config/book_database.yaml"

    if os.path.exists(database_file):
        book_db = BookDatabase(database_file)
        origin_book = book_db.get_book_info("ORIGIN_BOOK_001")

        if origin_book:
            print(f"✅ 找到原点书籍: {origin_book.get('title', '未知')}")
            pos = origin_book.get('position', {})
            print(f"   位置: ({pos.get('x', 0)}, {pos.get('y', 0)}, {pos.get('z', 0)})")
        else:
            print("❌ 未找到ORIGIN_BOOK_001书籍")
            return
    else:
        print(f"❌ 数据库文件不存在: {database_file}")
        return

    # 测试ROS2Manager和NavigateToPose Action
    print("\n🧪 测试ROS2Manager和NavigateToPose Action...")
    try:
        ros2_manager = Ros2Manager()

        # 等待Action客户端初始化
        import time
        time.sleep(2.0)

        # 测试导航功能
        if ros2_manager.navigate_to_position(0.0, 0.0):
            print("✅ NavigateToPose Action调用成功")
            print("   机器人应该正在导航到原点...")
        else:
            print("❌ NavigateToPose Action调用失败")

        # 等待一段时间观察导航
        print("\n⏳ 等待导航执行...")
        time.sleep(10.0)

        # 清理
        ros2_manager.shutdown()

    except Exception as e:
        print(f"❌ ROS2Manager测试失败: {e}")

    # 关闭ROS2
    try:
        rclpy.shutdown()
    except:
        pass

    print("\n" + "=" * 60)
    print("📋 测试完成")
    print("\n🎯 下一步操作:")
    print("1. 确保Nav2导航系统正在运行")
    print("2. 启动UI系统: ros2 launch libbot_ui ui_findbook_demo.launch.py")
    print("3. 在UI中选择'图书馆指南'进行测试")
    print("4. 观察机器人是否通过NavigateToPose Action导航到原点")

if __name__ == "__main__":
    test_findbook_with_action()
