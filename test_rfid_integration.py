#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RFID标签与书籍映射集成测试
验证ORIGIN_BOOK_001的完整找书流程
"""

import yaml
import os

def test_database_integration():
    """测试书籍数据库集成"""
    print("🧪 测试书籍数据库集成...")

    # 读取书籍数据库
    db_path = "/home/lhl/lib_bot_ws/src/libbot_ui/config/book_database.yaml"
    with open(db_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    books = data.get('books', {})

    # 验证ORIGIN_BOOK_001存在
    if 'ORIGIN_BOOK_001' in books:
        book = books['ORIGIN_BOOK_001']
        print(f"✅ 找到书籍: {book['title']}")
        print(f"   作者: {book['author']}")
        print(f"   ISBN: {book['isbn']}")
        print(f"   位置: ({book['position']['x']}, {book['position']['y']}, {book['position']['z']})")
        print(f"   区域: {book['shelf_zone']}-{book['shelf_level']}层")
        return True
    else:
        print("❌ 未找到ORIGIN_BOOK_001书籍")
        return False

def test_rfid_config_integration():
    """测试RFID配置集成"""
    print("\n🧪 测试RFID配置集成...")

    # 读取RFID配置
    config_path = "/home/lhl/lib_bot_ws/src/libbot_simulation/config/rfid_config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    tags = data.get('rfid_tags', {}).get('predefined_tags', [])

    # 查找ORIGIN_BOOK_001标签
    origin_tag = None
    for tag in tags:
        if tag['id'] == 'ORIGIN_BOOK_001':
            origin_tag = tag
            break

    if origin_tag:
        print(f"✅ 找到RFID标签: {origin_tag['id']}")
        print(f"   位置: {origin_tag['position']}")
        print(f"   功率: {origin_tag['power']}")
        print(f"   描述: {origin_tag['description']}")
        return True
    else:
        print("❌ 未找到ORIGIN_BOOK_001 RFID标签")
        return False

def test_position_consistency():
    """测试位置一致性"""
    print("\n🧪 测试位置一致性...")

    # 读取书籍数据库
    db_path = "/home/lhl/lib_bot_ws/src/libbot_ui/config/book_database.yaml"
    with open(db_path, 'r', encoding='utf-8') as f:
        db_data = yaml.safe_load(f)

    # 读取RFID配置
    config_path = "/home/lhl/lib_bot_ws/src/libbot_simulation/config/rfid_config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        rfid_data = yaml.safe_load(f)

    # 获取书籍位置
    book_pos = db_data['books']['ORIGIN_BOOK_001']['position']
    book_x, book_y = book_pos['x'], book_pos['y']

    # 获取RFID标签位置
    tags = rfid_data['rfid_tags']['predefined_tags']
    rfid_pos = None
    for tag in tags:
        if tag['id'] == 'ORIGIN_BOOK_001':
            rfid_pos = tag['position']
            break

    if rfid_pos:
        rfid_x, rfid_y = rfid_pos[0], rfid_pos[1]

        # 检查位置是否一致（允许小的误差）
        tolerance = 0.001
        if abs(book_x - rfid_x) < tolerance and abs(book_y - rfid_y) < tolerance:
            print(f"✅ 位置一致")
            print(f"   书籍位置: ({book_x}, {book_y})")
            print(f"   RFID位置: ({rfid_x}, {rfid_y})")
            return True
        else:
            print(f"❌ 位置不一致")
            print(f"   书籍位置: ({book_x}, {book_y})")
            print(f"   RFID位置: ({rfid_x}, {rfid_y})")
            return False
    else:
        print("❌ 未找到RFID标签位置")
        return False

def test_world_model():
    """测试世界模型中的RFID标签"""
    print("\n🧪 测试世界模型...")

    world_path = "/home/lhl/lib_bot_ws/src/aws-robomaker-bookstore-world/worlds/bookstore_with_rfid.world"

    with open(world_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'rfid_tag_origin' in content:
        print("✅ 世界模型中存在rfid_tag_origin标签")
        print("   注意: 世界模型中的标签名称仍为rfid_tag_origin")
        print("   这不会影响功能，因为RFID传感器基于配置文件")
        return True
    else:
        print("❌ 世界模型中未找到rfid_tag_origin标签")
        return False

def main():
    """主测试函数"""
    print("🚀 开始RFID标签与书籍映射集成测试")
    print("=" * 50)

    # 运行所有测试
    tests = [
        test_database_integration,
        test_rfid_config_integration,
        test_position_consistency,
        test_world_model
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            results.append(False)

    # 总结结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✅ 全部测试通过 ({passed}/{total})")
        print("\n🎉 RFID标签与书籍映射集成成功！")
        print("\n📋 使用指南:")
        print("1. 启动仿真环境:")
        print("   ros2 launch libbot_simulation library_gazebo_rfid.launch.py")
        print("2. 启动RFID传感器:")
        print("   ros2 run libbot_simulation rfid_sensor_node")
        print("3. 启动UI系统:")
        print("   ros2 launch libbot_ui ui_findbook_demo.launch.py")
        print("4. 在UI中选择'图书馆指南'进行找书测试")
    else:
        print(f"❌ 部分测试失败 ({passed}/{total})")
        print("请检查失败的项目并修复问题")

if __name__ == "__main__":
    main()
