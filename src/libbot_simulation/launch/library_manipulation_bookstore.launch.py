#!/usr/bin/env python3
#
# 图书馆机器人带机械臂的AWS书店仿真启动文件
# 基于 turtlebot3_manipulation_gazebo/launch/gazebo.launch.py 模板
# 使用 AWS RoboMaker Bookstore 世界
#

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.actions import AppendEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch.substitutions import ThisLaunchFileDir

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def is_valid_to_launch():
    # Path includes model name of Raspberry Pi series
    path = '/sys/firmware/devicetree/base/model'
    if os.path.exists(path):
        return False
    else:
        return True


def generate_launch_description():
    if not is_valid_to_launch():
        print('Can not launch fake robot in Raspberry Pi')
        return LaunchDescription([])

    # 参数配置
    start_rviz = LaunchConfiguration('start_rviz')
    prefix = LaunchConfiguration('prefix')
    use_sim = LaunchConfiguration('use_sim')

    # AWS Bookstore 世界配置
    pkg_bookstore_world = get_package_share_directory('aws_robomaker_bookstore_world')

    # 世界文件路径
    world = LaunchConfiguration(
        'world',
        default=PathJoinSubstitution([
            FindPackageShare('aws_robomaker_bookstore_world'),
            'worlds',
            'bookstore.world'
        ])
    )

    # 机器人初始位置（书店内合适位置）
    pose = {
        'x': LaunchConfiguration('x_pose', default='0.0'),
        'y': LaunchConfiguration('y_pose', default='0.0'),
        'z': LaunchConfiguration('z_pose', default='0.01'),
        'R': LaunchConfiguration('roll', default='0.00'),
        'P': LaunchConfiguration('pitch', default='0.00'),
        'Y': LaunchConfiguration('yaw', default='0.00')
    }

    # 添加环境变量 - AWS Bookstore 模型路径
    append_model_path = AppendEnvironmentVariable(
        'GAZEBO_MODEL_PATH',
        os.path.join(pkg_bookstore_world, 'models')
    )
    append_resource_path = AppendEnvironmentVariable(
        'GAZEBO_RESOURCE_PATH',
        pkg_bookstore_world
    )

    return LaunchDescription([
        # 声明参数
        DeclareLaunchArgument(
            'start_rviz',
            default_value='false',
            description='Whether execute rviz2'),

        DeclareLaunchArgument(
            'prefix',
            default_value='""',
            description='Prefix of the joint and link names'),

        DeclareLaunchArgument(
            'use_sim',
            default_value='true',
            description='Start robot in Gazebo simulation.'),

        DeclareLaunchArgument(
            'world',
            default_value=world,
            description='Directory of gazebo world file'),

        DeclareLaunchArgument(
            'x_pose',
            default_value=pose['x'],
            description='position of turtlebot3'),

        DeclareLaunchArgument(
            'y_pose',
            default_value=pose['y'],
            description='position of turtlebot3'),

        DeclareLaunchArgument(
            'z_pose',
            default_value=pose['z'],
            description='position of turtlebot3'),

        DeclareLaunchArgument(
            'roll',
            default_value=pose['R'],
            description='orientation of turtlebot3'),

        DeclareLaunchArgument(
            'pitch',
            default_value=pose['P'],
            description='orientation of turtlebot3'),

        DeclareLaunchArgument(
            'yaw',
            default_value=pose['Y'],
            description='orientation of turtlebot3'),

        # 环境变量
        append_model_path,
        append_resource_path,

        # 1. 启动 base.launch.py - 机器人状态发布和控制器
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                ThisLaunchFileDir(),
                '/library_manipulation_base.launch.py'
            ]),
            launch_arguments={
                'start_rviz': start_rviz,
                'prefix': prefix,
                'use_sim': use_sim,
            }.items(),
        ),

        # 2. 启动 Gazebo - 使用 AWS Bookstore 世界
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare('gazebo_ros'),
                    'launch',
                    'gazebo.launch.py'
                ])
            ]),
            launch_arguments={
                'verbose': 'false',
                'world': world,
            }.items(),
        ),

        # 3. 生成机器人 - 从 robot_description 话题
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-topic', 'robot_description',
                '-entity', 'turtlebot3_manipulation_system',
                '-x', pose['x'], '-y', pose['y'], '-z', pose['z'],
                '-R', pose['R'], '-P', pose['P'], '-Y', pose['Y'],
            ],
            output='screen',
        ),
    ])
