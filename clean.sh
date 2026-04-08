#!/bin/bash

# ROS2 工作空间清理脚本
# 用于删除编译产物：build, install, log 目录

# 获取脚本所在目录（工作空间根目录）
WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "  ROS2 工作空间清理脚本"
echo "=========================================="
echo "工作空间路径: $WORKSPACE_DIR"
echo ""

# 要删除的目录列表
DIRS_TO_REMOVE=("build" "install" "log")

# 检查要删除的目录
echo "检查编译产物目录..."
FOUND_DIRS=()
for dir in "${DIRS_TO_REMOVE[@]}"; do
    if [ -d "$WORKSPACE_DIR/$dir" ]; then
        FOUND_DIRS+=("$dir")
        echo "  ✓ 发现: $dir/"
    fi
done

# 如果没有找到任何目录
if [ ${#FOUND_DIRS[@]} -eq 0 ]; then
    echo ""
    echo "✓ 工作空间已经是干净的，没有需要删除的编译产物。"
    exit 0
fi

# 询问用户确认
echo ""
echo "将要删除以下目录:"
for dir in "${FOUND_DIRS[@]}"; do
    echo "  - $dir/"
done
echo ""
read -p "确认删除? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消操作。"
    exit 0
fi

# 删除目录
echo ""
echo "开始清理..."
for dir in "${FOUND_DIRS[@]}"; do
    echo "  删除 $dir/ ..."
    rm -rf "$WORKSPACE_DIR/$dir"
    if [ $? -eq 0 ]; then
        echo "  ✓ 已删除 $dir/"
    else
        echo "  ✗ 删除 $dir/ 失败"
    fi
done

echo ""
echo "=========================================="
echo "✓ 清理完成！"
echo "=========================================="
echo "现在可以重新编译工作空间:"
echo "  colcon build"
echo ""
