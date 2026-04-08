#!/bin/bash

echo "╔════════════════════════════════════════════╗"
echo "║        1-2story 完整测试启动脚本          ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# 确保在工作空间根目录
if [ ! -f "install/setup.bash" ]; then
    echo "❌ 错误：请从工作空间根目录运行此脚本"
    echo "   当前目录: $(pwd)"
    echo "   期望目录: ~/lib_bot_ws"
    exit 1
fi

# Source环境变量
echo "📦 配置ROS2环境..."
source install/setup.bash

echo "✅ 环境配置完成"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "请选择测试步骤："
echo "1. 启动测试UI（用于显示ROS2消息）"
echo "2. 启动Action服务器（找书任务模拟）"
echo "3. 启动Service服务器（图书信息模拟）"
echo "4. 查看测试命令示例"
echo "5. 开始完整测试（新终端）"
echo ""
read -p "输入选项 [1-5]: " choice

cd src

case $choice in
    1)
        echo "🎮 启动测试UI..."
        python3 test_ui_display.py
        ;;
    2)
        echo "🎮 启动Action服务器..."
        python3 test_action_server.py
        ;;
    3)
        echo "🎮 启动Service服务器..."
        python3 test_service_server.py
        ;;
    4)
        echo "📝 测试命令示例："
        echo ""
        echo "发送找书任务："
        echo "ros2 action send_goal /find_book libbot_msgs/action/FindBook '{\"book_id\": \"9787115426273\", \"guide_patron\": true}'"
        echo ""
        echo "查询图书："
        echo "ros2 service call /get_book_info libbot_msgs/srv/GetBookInfo '{\"book_id\": \"9787115426273\"}'"
        ;;
    5)
        echo "🚀 准备启动完整测试..."
        echo ""
        echo "请手动在4个新终端中运行："
        echo ""
        echo "终端1: ros2 run rmw_zenoh_cpp rmw_zenohd"
        echo "终端2: cd src && python3 test_action_server.py"
        echo "终端3: cd src && python3 test_service_server.py"
        echo "终端4: cd src && python3 test_ui_display.py"
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac
