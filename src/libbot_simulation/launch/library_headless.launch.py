#!/usr/bin/env python3
# 图书馆机器人无GUI仿真启动文件（推荐用于性能和稳定性）

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # 获取包路径
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_bookstore_world = get_package_share_directory('aws-robomaker-bookstore-world')
    pkg_turtlebot3_gazebo = get_package_share_directory('turtlebot3_gazebo')
    pkg_turtlebot3_description = get_package_share_directory('turtlebot3_description')

    # 声明启动参数
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')

    # TurtleBot3 Waffle Pi URDF文件路径
    urdf_file = os.path.join(pkg_turtlebot3_description, 'urdf', 'turtlebot3_waffle_pi.urdf')

    # 设置TurtleBot3模型环境变量
    set_turtlebot3_model = SetEnvironmentVariable('TURTLEBOT3_MODEL', 'waffle_pi')

    # Gazebo无GUI启动
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'gui': 'false',  # 强制无GUI模式
            'world': os.path.join(pkg_bookstore_world, 'worlds', 'bookstore.world'),
            'use_sim_time': use_sim_time,
            'verbose': 'false'
        }.items()
    )

    # 机器人状态发布器
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': ParameterValue(
                Command('xacro ' + urdf_file),
                value_type=str
            )
        }]
    )

    # 机器人发布到Gazebo
    spawn_turtlebot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_turtlebot3_gazebo, 'launch', 'spawn_turtlebot3.launch.py')
        ),
        launch_arguments={
            'x_pose': x_pose,
            'y_pose': y_pose,
            'robot_name': 'library_robot',
            'urdf_file': urdf_file
        }.items()
    )

    return LaunchDescription([
        # 环境变量
        set_turtlebot3_model,

        # 声明参数
        DeclareLaunchArgument('use_sim_time', default_value='true', description='使用仿真时间'),
        DeclareLaunchArgument('x_pose', default_value='0.0', description='机器人初始X位置'),
        DeclareLaunchArgument('y_pose', default_value='0.0', description='机器人初始Y位置'),

        # 启动Gazebo（无GUI）
        gazebo,

        # 发布机器人状态
        robot_state_publisher,

        # 生成机器人
        spawn_turtlebot,
    ])