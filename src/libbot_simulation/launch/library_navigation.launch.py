#!/usr/bin/env python3
# 图书馆机器人导航仿真启动文件
# 基于现有的仿真环境添加Nav2寻路功能

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, FindExecutable
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # 获取包路径
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_bookstore_world = get_package_share_directory('aws_robomaker_bookstore_world')
    pkg_turtlebot3_gazebo = get_package_share_directory('turtlebot3_gazebo')
    pkg_turtlebot3_description = get_package_share_directory('turtlebot3_description')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')
    pkg_libbot_simulation = get_package_share_directory('libbot_simulation')

    # 声明启动参数
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    gui = LaunchConfiguration('gui', default='true')
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')
    map_yaml_file = LaunchConfiguration('map_yaml_file', default=os.path.join(pkg_bookstore_world, 'maps', 'turtlebot3_waffle_pi', 'map.yaml'))
    params_file = LaunchConfiguration('params_file', default=os.path.join(pkg_libbot_simulation, 'config', 'library_nav2_params.yaml'))
    autostart = LaunchConfiguration('autostart', default='true')
    rviz_config_file = LaunchConfiguration('rviz_config_file', default=os.path.join(pkg_nav2_bringup, 'rviz', 'nav2_default_view.rviz'))

    # TurtleBot3 Waffle Pi URDF文件路径
    urdf_file = os.path.join(pkg_turtlebot3_description, 'urdf', 'turtlebot3_waffle_pi.urdf')

    # 设置TurtleBot3模型环境变量
    set_turtlebot3_model = SetEnvironmentVariable('TURTLEBOT3_MODEL', 'waffle_pi')

    # Gazebo启动
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'gui': gui,
            'world': os.path.join(pkg_bookstore_world, 'worlds', 'bookstore.world'),
            'use_sim_time': use_sim_time
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

    # Nav2导航启动
    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': map_yaml_file,
            'params_file': params_file,
            'use_sim_time': use_sim_time,
            'autostart': autostart,
            'rviz_config_file': rviz_config_file
        }.items()
    )

    return LaunchDescription([
        # 环境变量
        set_turtlebot3_model,

        # 声明参数
        DeclareLaunchArgument('gui', default_value='true', description='启动Gazebo GUI'),
        DeclareLaunchArgument('use_sim_time', default_value='true', description='使用仿真时间'),
        DeclareLaunchArgument('x_pose', default_value='0.0', description='机器人初始X位置'),
        DeclareLaunchArgument('y_pose', default_value='0.0', description='机器人初始Y位置'),
        DeclareLaunchArgument('map_yaml_file', default_value=os.path.join(pkg_bookstore_world, 'maps', 'turtlebot3_waffle_pi', 'map.yaml'), description='地图yaml文件路径'),
        DeclareLaunchArgument('params_file', default_value=os.path.join(pkg_bookstore_world, 'param', 'waffle_pi.yaml'), description='Nav2参数文件路径'),
        DeclareLaunchArgument('autostart', default_value='true', description='自动启动nav2 lifecycle节点'),
        DeclareLaunchArgument('rviz_config_file', default_value=os.path.join(pkg_nav2_bringup, 'rviz', 'nav2_default_view.rviz'), description='RVIZ配置文件路径'),

        # 启动Gazebo
        gazebo,

        # 发布机器人状态
        robot_state_publisher,

        # 生成机器人
        spawn_turtlebot,

        # 启动Nav2导航
        nav2_bringup,
    ])