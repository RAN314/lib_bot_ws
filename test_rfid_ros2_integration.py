#!/usr/bin/env python3
"""
RFID ROS2集成测试 - 验证节点和Topic功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'libbot_simulation'))

import rclpy
from rclpy.node import Node
import time

def test_ros2_integration():
    """测试ROS2集成"""
    print("🔧 测试RFID ROS2集成")

    try:
        # 初始化ROS2
        rclpy.init()
        print("  ✅ ROS2初始化成功")

        # 创建测试节点
        test_node = Node('rfid_test_node')
        print("  ✅ 测试节点创建成功")

        # 测试RFID噪声模型导入
        from libbot_simulation.rfid_noise_model import RFIDNoiseSimulator
        simulator = RFIDNoiseSimulator()
        print("  ✅ RFID噪声模型导入成功")

        # 测试检测功能
        tag = {'id': 'test_tag', 'position': (0.3, 0.0, 0.0), 'power': 1.0}
        results = simulator.simulate_detection(
            direction='front',
            tags_in_range=[tag],
            robot_pose=(0.0, 0.0, 0.0),
            robot_orientation=0.0,
            timestamp=time.time()
        )
        print(f"  ✅ 检测功能测试成功，结果数量: {len(results)}")

        # 测试消息导入
        from libbot_msgs.msg import RFIDScan
        msg = RFIDScan()
        msg.antenna_position = 'front'
        msg.detected_book_ids = ['book_001']
        msg.signal_strengths = [0.8]
        print("  ✅ RFIDScan消息创建成功")

        # 清理
        test_node.destroy_node()
        rclpy.shutdown()

        print("  ✅ ROS2集成测试通过")
        return True

    except Exception as e:
        print(f"  ❌ ROS2集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🔬 RFID ROS2集成测试")
    print("=" * 40)

    success = test_ros2_integration()

    if success:
        print("\n🎉 RFID ROS2集成测试通过！")
    else:
        print("\n❌ RFID ROS2集成测试失败！")
        sys.exit(1)