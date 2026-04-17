#!/usr/bin/env python3
# 图书馆机器人RFID + Nav2导航仿真启动文件 - 修复版
# 基于library_nav2_simple.launch.py，添加RFID功能

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, AppendEnvironmentVariable, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # 获取包目录
    bringup_dir = get_package_share_directory('nav2_bringup')
    launch_dir = os.path.join(bringup_dir, 'launch')
    pkg_bookstore_world = get_package_share_directory('aws_robomaker_bookstore_world')
    pkg_turtlebot3_gazebo = get_package_share_directory('turtlebot3_gazebo')
    pkg_libbot_simulation = get_package_share_directory('libbot_simulation')

    # 启动配置 - 与原始文件完全一致
    slam = LaunchConfiguration('slam')
    namespace = LaunchConfiguration('namespace')
    use_namespace = LaunchConfiguration('use_namespace')
    map_yaml_file = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')
    autostart = LaunchConfiguration('autostart')
    use_composition = LaunchConfiguration('use_composition')
    use_respawn = LaunchConfiguration('use_respawn')
    rviz_config_file = LaunchConfiguration('rviz_config_file')
    use_simulator = LaunchConfiguration('use_simulator')
    use_robot_state_pub = LaunchConfiguration('use_robot_state_pub')
    use_rviz = LaunchConfiguration('use_rviz')
    headless = LaunchConfiguration('headless')
    world = LaunchConfiguration('world')
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')
    z_pose = LaunchConfiguration('z_pose', default='0.01')
    roll = LaunchConfiguration('roll', default='0.00')
    pitch = LaunchConfiguration('pitch', default='0.00')
    yaw = LaunchConfiguration('yaw', default='0.00')

    remappings = [('/tf', 'tf'), ('/tf_static', 'tf_static')]

    # 声明参数 - 与原始文件完全一致
    declare_namespace = DeclareLaunchArgument('namespace', default_value='', description='Top-level namespace')
    declare_use_namespace = DeclareLaunchArgument('use_namespace', default_value='false')
    declare_slam = DeclareLaunchArgument('slam', default_value='False')
    declare_map = DeclareLaunchArgument('map', default_value=os.path.join(pkg_bookstore_world, 'maps', 'turtlebot3_waffle_pi', 'map.yaml'))
    declare_use_sim_time = DeclareLaunchArgument('use_sim_time', default_value='true')
    declare_params_file = DeclareLaunchArgument('params_file', default_value=os.path.join(bringup_dir, 'params', 'nav2_params.yaml'))
    declare_autostart = DeclareLaunchArgument('autostart', default_value='true')
    declare_use_composition = DeclareLaunchArgument('use_composition', default_value='True')
    declare_use_respawn = DeclareLaunchArgument('use_respawn', default_value='False')
    declare_rviz_config = DeclareLaunchArgument('rviz_config_file', default_value=os.path.join(bringup_dir, 'rviz', 'nav2_default_view.rviz'))
    declare_use_simulator = DeclareLaunchArgument('use_simulator', default_value='True')
    declare_use_robot_state_pub = DeclareLaunchArgument('use_robot_state_pub', default_value='True')
    declare_use_rviz = DeclareLaunchArgument('use_rviz', default_value='True')
    declare_headless = DeclareLaunchArgument('headless', default_value='False')
    declare_world = DeclareLaunchArgument('world', default_value=os.path.join(pkg_bookstore_world, 'worlds', 'bookstore.world'))

    # 环境变量 - 只添加必要的路径
    append_model_path1 = AppendEnvironmentVariable('GAZEBO_MODEL_PATH', os.path.join(pkg_bookstore_world, 'models'))
    append_model_path2 = AppendEnvironmentVariable('GAZEBO_MODEL_PATH', os.path.join(pkg_turtlebot3_gazebo, 'models'))
    append_resource_path = AppendEnvironmentVariable('GAZEBO_RESOURCE_PATH', pkg_bookstore_world)

    # Gazebo 服务器 - 与原始文件完全一致
    start_gazebo_server = ExecuteProcess(
        condition=IfCondition(use_simulator),
        cmd=['gzserver', '-s', 'libgazebo_ros_init.so', '-s', 'libgazebo_ros_factory.so', world],
        cwd=[launch_dir], output='screen')

    # Gazebo 客户端 - 与原始文件完全一致
    start_gazebo_client = ExecuteProcess(
        condition=IfCondition(PythonExpression([use_simulator, ' and not ', headless])),
        cmd=['gzclient'], cwd=[launch_dir], output='screen')

    # 机器人状态发布器 - 与原始文件完全一致
    urdf_path = os.path.join(pkg_turtlebot3_gazebo, 'urdf', 'turtlebot3_waffle_pi.urdf')
    robot_state_publisher = Node(
        condition=IfCondition(use_robot_state_pub),
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        namespace=namespace,
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': ParameterValue(Command(['xacro ', urdf_path]), value_type=str)
        }],
        remappings=remappings)

    # 生成机器人 - 与原始文件完全一致
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        output='screen',
        arguments=[
            '-entity', 'turtlebot3_waffle_pi',
            '-file', os.path.join(pkg_turtlebot3_gazebo, 'models', 'turtlebot3_waffle_pi', 'model.sdf'),
            '-x', x_pose, '-y', y_pose, '-z', z_pose,
            '-R', roll, '-P', pitch, '-Y', yaw])

    spawn_robot_delayed = TimerAction(period=3.0, actions=[spawn_robot])

    # =====================================
    # 添加的RFID功能
    # =====================================

    # 鲁棒位姿发布器 - 替换原有的robot_pose_publisher
    robust_pose_publisher = Node(
        package='libbot_simulation',
        executable='robust_pose_publisher',
        name='robust_pose_publisher',
        output='screen')

    # 延迟启动，确保Gazebo和机器人已经启动
    robust_pose_delayed = TimerAction(period=8.0, actions=[robust_pose_publisher])

    # RFID传感器节点
    rfid_sensor_node = Node(
        package='libbot_simulation',
        executable='rfid_sensor_node',
        name='rfid_sensor_node',
        output='screen',
        parameters=[
            os.path.join(pkg_libbot_simulation, 'config', 'rfid_config.yaml')
        ])

    rfid_sensor_delayed = TimerAction(period=10.0, actions=[rfid_sensor_node])

    # RFID可视化节点
    rfid_visualizer = Node(
        package='libbot_simulation',
        executable='rfid_visualizer',
        name='rfid_visualizer',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}])

    rfid_visualizer_delayed = TimerAction(period=12.0, actions=[rfid_visualizer])

    # =====================================
    # 原始Nav2功能
    # =====================================

    # RVIZ - 与原始文件完全一致
    rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(launch_dir, 'rviz_launch.py')),
        condition=IfCondition(use_rviz),
        launch_arguments={'namespace': namespace, 'use_namespace': use_namespace, 'rviz_config': rviz_config_file}.items())

    # Nav2 Bringup - 与原始文件完全一致
    bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(launch_dir, 'bringup_launch.py')),
        launch_arguments={
            'namespace': namespace, 'use_namespace': use_namespace, 'slam': slam,
            'map': map_yaml_file, 'use_sim_time': use_sim_time, 'params_file': params_file,
            'autostart': autostart, 'use_composition': use_composition, 'use_respawn': use_respawn}.items())

    # 组装启动描述 - 保持原始顺序，只添加RFID功能
    ld = LaunchDescription()

    # 环境设置 - 与原始文件完全一致
    ld.add_action(append_model_path1)
    ld.add_action(append_model_path2)
    ld.add_action(append_resource_path)

    # 参数声明 - 与原始文件完全一致
    ld.add_action(declare_namespace)
    ld.add_action(declare_use_namespace)
    ld.add_action(declare_slam)
    ld.add_action(declare_map)
    ld.add_action(declare_use_sim_time)
    ld.add_action(declare_params_file)
    ld.add_action(declare_autostart)
    ld.add_action(declare_use_composition)
    ld.add_action(declare_use_respawn)
    ld.add_action(declare_rviz_config)
    ld.add_action(declare_use_simulator)
    ld.add_action(declare_use_robot_state_pub)
    ld.add_action(declare_use_rviz)
    ld.add_action(declare_headless)
    ld.add_action(declare_world)

    # Gazebo仿真 - 与原始文件完全一致
    ld.add_action(start_gazebo_server)
    ld.add_action(start_gazebo_client)

    # 机器人基础 - 与原始文件完全一致
    ld.add_action(robot_state_publisher)
    ld.add_action(spawn_robot_delayed)

    # 添加的RFID功能
    ld.add_action(robust_pose_delayed)     # 8秒后启动位姿发布器
    ld.add_action(rfid_sensor_delayed)     # 10秒后启动RFID传感器
    ld.add_action(rfid_visualizer_delayed) # 12秒后启动可视化

    # Nav2导航系统 - 与原始文件完全一致
    ld.add_action(rviz)
    ld.add_action(bringup)

    return ld