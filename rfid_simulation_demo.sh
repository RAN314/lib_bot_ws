#!/bin/bash

# RFID仿真演示脚本
# 展示完整的RFID传感器集成到Gazebo仿真环境

echo "🤖 Waffle机器人RFID传感器仿真演示"
echo "======================================"

# 检查ROS环境
if [ -z "$ROS_DISTRO" ]; then
    echo "❌ ROS环境未设置，请先source ROS setup文件"
    exit 1
fi

echo "✅ ROS $ROS_DISTRO 环境已就绪"

# 设置环境变量
export TURTLEBOT3_MODEL=waffle_pi
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/opt/ros/$ROS_DISTRO/share/turtlebot3_gazebo/models:/opt/ros/$ROS_DISTRO/share/aws_robomaker_bookstore_world/models

# 方法1：使用新的RFID专用启动文件
echo ""
echo "📋 方法1：启动RFID专用仿真环境"
echo "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-"
echo "命令：ros2 launch libbot_simulation library_rfid_demo.launch.py"
echo ""
echo "这将启动："
echo "  ✅ Gazebo仿真环境（书店世界）"
echo "  ✅ Waffle Pi机器人"
echo "  ✅ RFID传感器节点"
echo "  ✅ 机器人位姿发布器"
echo "  ✅ RFID可视化节点"
echo "  ✅ RVIZ可视化界面"
echo ""

# 方法2：使用现有仿真+RFID集成
echo "📋 方法2：现有仿真+RFID集成"
echo "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-"
echo "命令：ros2 launch libbot_simulation rfid_simulation.launch.py"
echo ""
echo "这将启动："
echo "  ✅ 基础Gazebo仿真"
echo "  ✅ RFID传感器节点"
echo "  ✅ 基础RVIZ配置"
echo ""

# 方法3：测试脚本
echo "📋 方法3：运行集成测试"
echo "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-"
echo "命令：python3 test_rfid_gazebo_integration.py"
echo ""
echo "这将测试："
echo "  ✅ RFID传感器功能"
echo "  ✅ 标签检测能力"
echo "  ✅ 噪声模型效果"
echo ""

# 使用方法说明
echo "📋 使用步骤："
echo "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-"
echo "1. 在终端1启动仿真："
echo "   ros2 launch libbot_simulation library_rfid_demo.launch.py"
echo ""
echo "2. 在终端2查看RFID检测结果："
echo "   ros2 topic echo /rfid/scan/front"
echo "   ros2 topic echo /rfid/scan/back"
echo "   ros2 topic echo /rfid/scan/left"
echo "   ros2 topic echo /rfid/scan/right"
echo ""
echo "3. 在终端3控制机器人移动："
echo "   ros2 run teleop_twist_keyboard teleop_twist_keyboard"
echo ""
echo "4. 在Gazebo中观察机器人移动和RFID检测"
echo ""
echo "5. 在RVIZ中查看RFID可视化效果"
echo ""

# 验证安装
echo "📋 验证安装："
echo "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-" "-"
if [ -f "/home/lhl/lib_bot_ws/install/libbot_simulation/lib/rfid_sensor_node" ]; then
    echo "✅ RFID传感器节点已安装"
else
    echo "❌ RFID传感器节点未找到，请先构建：colcon build --packages-select libbot_simulation"
fi

if [ -f "/home/lhl/lib_bot_ws/install/libbot_simulation/lib/robot_pose_publisher" ]; then
    echo "✅ 机器人位姿发布器已安装"
else
    echo "❌ 机器人位姿发布器未找到"
fi

if [ -f "/home/lhl/lib_bot_ws/install/libbot_simulation/lib/rfid_visualizer" ]; then
    echo "✅ RFID可视化节点已安装"
else
    echo "❌ RFID可视化节点未找到"
fi

echo ""
echo "🎯 RFID传感器已成功集成到Waffle机器人仿真系统！"
echo "现在可以在Gazebo仿真环境中测试RFID检测功能了。"

# 提供快速启动选项
read -p "是否要立即启动RFID仿真演示？(y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 启动RFID仿真演示..."
    cd /home/lhl/lib_bot_ws
    ros2 launch libbot_simulation library_rfid_demo.launch.py
else
    echo "💡 提示：您可以随时使用上述命令启动仿真"
fi