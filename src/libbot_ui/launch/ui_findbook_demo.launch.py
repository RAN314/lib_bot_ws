#!/usr/bin/env python3
#
# UI控制面板启动文件
# 仅启动UI节点，与仿真环境分离

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # 启动参数
    use_sim = LaunchConfiguration('use_sim', default='true')

    return LaunchDescription([
        # 启动参数声明
        DeclareLaunchArgument(
            'use_sim',
            default_value='true',
            description='使用仿真时间'),

        # 仅启动UI控制面板
        Node(
            package='libbot_ui',
            executable='main_window',
            name='libbot_ui',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim,
                'book_database_file': PathJoinSubstitution([
                    FindPackageShare('libbot_ui'),
                    'config', 'book_database.yaml'
                ])
            }]
        )
    ])
