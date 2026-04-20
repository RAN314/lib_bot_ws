from setuptools import setup

package_name = 'libbot_simulation'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/library_simulation.launch.py', 
                                               'launch/library_with_turtlebot3.launch.py', 
                                               'launch/library_headless.launch.py', 
                                               'launch/library_navigation.launch.py', 
                                               'launch/library_navigation_complete.launch.py', 
                                               'launch/library_tb3_simulation.launch.py', 
                                               'launch/library_nav2_simulation.launch.py', 
                                               'launch/library_nav2_simple.launch.py', 
                                               'launch/rfid_simulation.launch.py', 
                                               'launch/library_rfid_demo.launch.py', 
                                               'launch/simple_rfid_demo.launch.py',
                                               'launch/library_nav2_use_sim_time.launch.py', 
                                               'launch/library_manipulation_bookstore.launch.py', 
                                               'launch/library_manipulation_base.launch.py', 
                                               'launch/library_gazebo.launch.py']),
        ('share/' + package_name + '/config', ['config/turtlebot3_config.yaml', 'config/library_nav2_params.yaml', 'config/rfid_config.yaml']),
        ('share/' + package_name + '/worlds', ['worlds/bookstore.world', 'worlds/bookstore_with_rfid.world']),
        ('share/' + package_name + '/models/rfid_tag', ['models/rfid_tag/model.sdf', 'models/rfid_tag/model.config']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='lihaolan',
    maintainer_email='lihaolan@example.com',
    description='Library Robot Simulation Package - RFID noise model and sensor simulation',
    license='Apache 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'rfid_sensor_node=libbot_simulation.rfid_sensor_node:main',
            'robot_pose_publisher=libbot_simulation.robot_pose_publisher:main',
            'robust_pose_publisher=libbot_simulation.robust_pose_publisher:main',
            'rfid_visualizer=libbot_simulation.rfid_visualizer:main',
            'amcl_pose_converter=libbot_simulation.amcl_pose_converter:main',
            'test_rfid_simulation=libbot_simulation.test.test_rfid_simulation:main',
        ],
    },
)