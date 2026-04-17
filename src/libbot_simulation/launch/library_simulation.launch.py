#!/usr/bin/env python3
# 图书馆机器人仿真主启动文件
# 基于Amazon RoboMaker书店世界 + TurtleBot3 Waffle Pi

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, ThisLaunchFileDir
from launch_ros.actions import Node

def generate_launch_description():
    # 获取包路径
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_libbot_simulation = get_package_share_directory('libbot_simulation')

    # 声明启动参数
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    gui = LaunchConfiguration('gui', default='true')
    world = LaunchConfiguration('world', default=os.path.join(
        pkg_libbot_simulation, 'worlds', 'bookstore.world'))

    # Gazebo启动
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'gui': gui,
            'world': world,
            'use_sim_time': use_sim_time
        }.items()
    )

    return LaunchDescription([
        # 声明参数
        DeclareLaunchArgument('gui', default_value='true', description='启动Gazebo GUI'),
        DeclareLaunchArgument('use_sim_time', default_value='true', description='使用仿真时间'),
        DeclareLaunchArgument('world', default_value=world, description='世界文件路径'),

        # 启动Gazebo
        gazebo,
    ])