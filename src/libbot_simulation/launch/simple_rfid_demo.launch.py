#!/usr/bin/env python3
# 简单RFID传感器仿真演示
# 最小化依赖，专注于RFID功能演示

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, AppendEnvironmentVariable, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # 获取包目录
    pkg_bookstore_world = get_package_share_directory('aws_robomaker_bookstore_world')
    pkg_turtlebot3_gazebo = get_package_share_directory('turtlebot3_gazebo')
    pkg_libbot_simulation = get_package_share_directory('libbot_simulation')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    # 启动配置
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    use_rviz = LaunchConfiguration('use_rviz', default='true')
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')
    yaw = LaunchConfiguration('yaw', default='0.00')

    # 声明参数
    declare_use_sim_time = DeclareLaunchArgument('use_sim_time', default_value='true')
    declare_use_rviz = DeclareLaunchArgument('use_rviz', default_value='true')

    # 环境变量
    append_model_path1 = AppendEnvironmentVariable('GAZEBO_MODEL_PATH', os.path.join(pkg_bookstore_world, 'models'))
    append_model_path2 = AppendEnvironmentVariable('GAZEBO_MODEL_PATH', os.path.join(pkg_turtlebot3_gazebo, 'models'))
    append_model_path3 = AppendEnvironmentVariable('GAZEBO_MODEL_PATH', os.path.join(pkg_libbot_simulation, 'models'))
    append_resource_path = AppendEnvironmentVariable('GAZEBO_RESOURCE_PATH', pkg_bookstore_world)

    # Gazebo启动
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'world': os.path.join(pkg_bookstore_world, 'worlds', 'bookstore.world'),
            'use_sim_time': use_sim_time
        }.items()
    )

    # 机器人状态发布器
    urdf_path = os.path.join(pkg_turtlebot3_gazebo, 'urdf', 'turtlebot3_waffle_pi.urdf')
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': ParameterValue(Command(['xacro ', urdf_path]), value_type=str)
        }]
    )

    # 生成机器人
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        output='screen',
        arguments=[
            '-entity', 'turtlebot3_waffle_pi',
            '-file', os.path.join(pkg_turtlebot3_gazebo, 'models', 'turtlebot3_waffle_pi', 'model.sdf'),
            '-x', x_pose, '-y', y_pose, '-z', '0.01',
            '-Y', yaw])

    spawn_robot_delayed = TimerAction(period=3.0, actions=[spawn_robot])

    # RFID传感器节点
    rfid_sensor_node = Node(
        package='libbot_simulation',
        executable='rfid_sensor_node',
        name='rfid_sensor_node',
        output='screen',
        parameters=[os.path.join(pkg_libbot_simulation, 'config', 'rfid_config.yaml')])

    rfid_sensor_delayed = TimerAction(period=8.0, actions=[rfid_sensor_node])

    # 机器人位姿发布器
    robot_pose_publisher = Node(
        package='libbot_simulation',
        executable='robot_pose_publisher',
        name='robot_pose_publisher',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}])

    robot_pose_delayed = TimerAction(period=10.0, actions=[robot_pose_publisher])

    # RFID可视化节点
    rfid_visualizer = Node(
        package='libbot_simulation',
        executable='rfid_visualizer',
        name='rfid_visualizer',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}])

    rfid_visualizer_delayed = TimerAction(period=12.0, actions=[rfid_visualizer])

    # RVIZ
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        condition=IfCondition(use_rviz),
        output='screen',
        arguments=['-d', os.path.join(pkg_libbot_simulation, 'rviz', 'rfid_demo.rviz')],
        parameters=[{'use_sim_time': use_sim_time}])

    rviz_delayed = TimerAction(period=15.0, actions=[rviz])

    return LaunchDescription([
        # 环境设置
        append_model_path1,
        append_model_path2,
        append_model_path3,
        append_resource_path,

        # 声明参数
        declare_use_sim_time,
        declare_use_rviz,

        # Gazebo仿真
        gazebo,

        # 机器人
        robot_state_publisher,
        spawn_robot_delayed,

        # RFID系统
        rfid_sensor_delayed,
        robot_pose_delayed,
        rfid_visualizer_delayed,

        # 可视化
        rviz_delayed,
    ])
