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
        ('share/' + package_name + '/launch', ['launch/library_simulation.launch.py', 'launch/library_with_turtlebot3.launch.py', 'launch/library_headless.launch.py', 'launch/library_navigation.launch.py', 'launch/library_navigation_complete.launch.py', 'launch/library_tb3_simulation.launch.py', 'launch/library_nav2_simulation.launch.py', 'launch/library_nav2_simple.launch.py', 'launch/rfid_simulation.launch.py']),
        ('share/' + package_name + '/config', ['config/turtlebot3_config.yaml', 'config/library_nav2_params.yaml', 'config/rfid_config.yaml']),
        ('share/' + package_name + '/worlds', ['worlds/bookstore.world']),
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
            'test_rfid_simulation=libbot_simulation.test.test_rfid_simulation:main',
        ],
    },
)