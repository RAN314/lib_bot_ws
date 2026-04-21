#!/usr/bin/env python3
"""
测试UI集成导航功能 - 验证使用NavigateToPose Action
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'src/libbot_ui'))

from libbot_ui.libbot_ui.ros2_manager import Ros2Manager
from libbot_ui.libbot_ui.find_book_dialog import BookDatabase
import rclpy

def test_navigation_integration():
    """测试导航集成"""
    print("🚀 开始测试UI导航集成")
    print("=" * 50)

    # 初始化ROS2
    try:
        rclpy.init()
        print("✅ ROS2初始化成功")
    except Exception as e:
        print(f"❌ ROS2初始化失败: {e}")
        return False

    try:
        # 创建ROS2管理器
        ros2_manager = Ros2Manager()
        time.sleep(2.0)  # 等待初始化

        # 测试书籍数据库
        database_file = "/home/lhl/lib_bot_ws/src/libbot_ui/config/book_database.yaml"
        book_db = BookDatabase(database_file)

        # 测试几本书籍
        test_books = ["BK001", "BK002", "ORIGIN_BOOK_001"]

        for book_id in test_books:
            print(f"\n🧪 测试书籍: {book_id}")
            book_info = book_db.get_book_info(book_id)

            if book_info:
                print(f"   书名: {book_info.get('title', '未知')}")
                position = book_info.get('position', {})
                print(f"   位置: ({position.get('x', 0)}, {position.get('y', 0)})")

                # 测试使用位置的找书功能
                print(f"   发送导航请求到 ({position.get('x', 0)}, {position.get('y', 0)})")
                success = ros2_manager.send_find_book_goal_with_position(
                    book_id, position, guide_patron=False
                )

                if success:
                    print(f"   ✅ 导航请求发送成功")
                else:
                    print(f"   ❌ 导航请求发送失败")

                time.sleep(1.0)  # 等待一下
            else:
                print(f"   ❌ 未找到书籍信息")

        # 等待一段时间观察导航
        print("\n⏳ 等待导航执行 (10秒)...")
        time.sleep(10.0)

        # 清理
        ros2_manager.shutdown()
        return True

    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

    finally:
        try:
            rclpy.shutdown()
        except:
            pass

if __name__ == "__main__":
    success = test_navigation_integration()
    print("\n" + "=" * 50)
    if success:
        print("✅ 导航集成测试完成")
    else:
        print("❌ 导航集成测试失败")
    print("=" * 50)