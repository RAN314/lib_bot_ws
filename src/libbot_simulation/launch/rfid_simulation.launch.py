#!/usr/bin/env python3
# 图书馆机器人RFID仿真启动文件
# 集成RFID传感器、噪声模型和完整仿真环境

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
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
    pkg_libbot_simulation = get_package_share_directory('libbot_simulation')

    # 声明启动参数
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    gui = LaunchConfiguration('gui', default='true')
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')
    rfid_enabled = LaunchConfiguration('rfid_enabled', default='true')
    noise_model_enabled = LaunchConfiguration('noise_model_enabled', default='true')

    # TurtleBot3 Waffle Pi URDF文件路径
    urdf_file = os.path.join(pkg_turtlebot3_description, 'urdf', 'turtlebot3_waffle_pi.urdf')

    # 设置TurtleBot3模型环境变量
    set_turtlebot3_model = SetEnvironmentVariable('TURTLEBOT3_MODEL', 'waffle_pi')

    # Gazebo启动 - 使用书店世界
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

    # RFID传感器节点
    rfid_sensor_node = Node(
        package='libbot_simulation',
        executable='rfid_sensor_node',
        name='rfid_sensor_node',
        output='screen',
        parameters=[
            os.path.join(pkg_libbot_simulation, 'config', 'rfid_config.yaml')
        ],
        remappings=[
            ('/robot_pose', '/amcl_pose')  # 使用AMCL定位结果
        ]
    )

    # 延迟启动RFID节点，等待Gazebo完全启动
    delayed_rfid_node = TimerAction(
        period=10.0,
        actions=[rfid_sensor_node]
    )

    # 可选：添加RVIZ可视化
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.join(pkg_libbot_simulation, 'config', 'rfid_rviz.rviz')],
        condition=lambda context: context.launch_configurations.get('gui', 'true') == 'true'
    )

    return LaunchDescription([
        # 环境变量
        set_turtlebot3_model,

        # 声明参数
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='使用仿真时间'
        ),
        DeclareLaunchArgument(
            'gui',
            default_value='true',
            description='启动Gazebo GUI'
        ),
        DeclareLaunchArgument(
            'x_pose',
            default_value='0.0',
            description='机器人初始X位置'
        ),
        DeclareLaunchArgument(
            'y_pose',
            default_value='0.0',
            description='机器人初始Y位置'
        ),
        DeclareLaunchArgument(
            'rfid_enabled',
            default_value='true',
            description='启用RFID传感器'
        ),
        DeclareLaunchArgument(
            'noise_model_enabled',
            default_value='true',
            description='启用RFID噪声模型'
        ),

        # 启动Gazebo仿真环境
        gazebo,

        # 发布机器人状态
        robot_state_publisher,

        # 生成机器人
        spawn_turtlebot,

        # 延迟启动RFID传感器节点
        delayed_rfid_node,

        # 可选RVIZ可视化
        rviz_node,
    ])

# ============================================
# 专用RFID测试启动文件
# ============================================

def generate_rfid_test_launch_description():
    """生成RFID专用测试启动描述"""
    pkg_libbot_simulation = get_package_share_directory('libbot_simulation')

    return LaunchDescription([
        # RFID传感器节点（测试模式）
        Node(
            package='libbot_simulation',
            executable='rfid_sensor_node',
            name='rfid_test_node',
            output='screen',
            parameters=[
                os.path.join(pkg_libbot_simulation, 'config', 'rfid_config.yaml'),
                {'rfid_sensor.scan_frequency': 5.0}  # 测试时降低频率
            ],
            remappings=[
                ('/robot_pose', '/test_robot_pose')
            ]
        ),

        # RFID测试节点
        Node(
            package='libbot_simulation',
            executable='test_rfid_simulation',
            name='rfid_simulation_test',
            output='screen'
        ),
    ])