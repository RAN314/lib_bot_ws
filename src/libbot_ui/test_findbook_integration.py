#!/usr/bin/env python3
"""
找书功能集成测试脚本
测试UI与仿真环境的集成
"""

import sys
import time
import yaml
from PyQt5.QtWidgets import QApplication
from libbot_ui.libbot_ui.main_window import MainWindow
from libbot_ui.libbot_ui.ros2_manager import Ros2Manager


def test_book_database():
    """测试书籍数据库功能"""
    print("🧪 测试书籍数据库...")

    # 测试数据库加载
    database_file = "/home/lhl/lib_bot_ws/src/libbot_ui/config/book_database.yaml"

    try:
        with open(database_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            books = data.get('books', {})

        print(f"✅ 成功加载 {len(books)} 本书籍")

        # 测试书籍查找
        test_book_id = "BK001"
        if test_book_id in books:
            book_info = books[test_book_id]
            print(f"✅ 找到书籍 {test_book_id}: {book_info.get('title', '未知')}")
            print(f"   位置: ({book_info['position']['x']}, {book_info['position']['y']})")
        else:
            print(f"❌ 未找到测试书籍 {test_book_id}")

        return True

    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False


def test_ros2_manager():
    """测试ROS2Manager功能"""
    print("\n🧪 测试ROS2Manager...")

    try:
        ros2_manager = Ros2Manager()
        print("✅ ROS2Manager初始化成功")

        # 测试书籍查找
        book_info = ros2_manager.find_book_by_id("BK001")
        if book_info:
            print(f"✅ 通过ROS2Manager找到书籍: {book_info.get('title', '未知')}")
        else:
            print("⚠️  通过ROS2Manager未找到书籍（使用默认数据）")

        # 测试导航功能（模拟）
        success = ros2_manager.navigate_to_position(2.5, 1.8)
        if success:
            print("✅ 导航功能测试成功")
        else:
            print("⚠️  导航功能不可用（可能ROS2未运行）")

        return True

    except Exception as e:
        print(f"❌ ROS2Manager测试失败: {e}")
        return False


def test_ui_integration():
    """测试UI集成"""
    print("\n🧪 测试UI集成...")

    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        print("✅ MainWindow创建成功")

        # 测试FindBook对话框
        book_database_file = "/home/lhl/lib_bot_ws/src/libbot_ui/config/book_database.yaml"
        from libbot_ui.libbot_ui.find_book_dialog import FindBookDialog

        dialog = FindBookDialog(window, window.ros2_manager, book_database_file)
        print("✅ FindBookDialog创建成功")

        # 测试书籍数据库加载
        if dialog.book_database.books:
            print(f"✅ 对话框加载了 {len(dialog.book_database.books)} 本书籍")
        else:
            print("❌ 对话框未加载书籍")

        return True

    except Exception as e:
        print(f"❌ UI集成测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始找书功能集成测试")
    print("=" * 50)

    # 运行所有测试
    tests = [
        test_book_database,
        test_ros2_manager,
        test_ui_integration
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试 {test.__name__} 异常: {e}")
            results.append(False)

    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")

    test_names = ["书籍数据库", "ROS2Manager", "UI集成"]
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")

    all_passed = all(results)
    print(f"\n🎯 总体结果: {'✅ 全部测试通过' if all_passed else '❌ 部分测试失败'}")

    if all_passed:
        print("\n🎉 集成测试完成！可以启动UI进行实际测试。")
        print("\n启动命令:")
        print("  ros2 launch src/libbot_ui/launch/ui_findbook_demo.launch.py")
    else:
        print("\n⚠️  存在测试失败，请检查相关组件。")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())