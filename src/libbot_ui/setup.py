from setuptools import find_packages, setup

package_name = 'libbot_ui'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='开发者',
    maintainer_email='dev@libbot.com',
    description='图书馆机器人控制面板UI - 基于Qt5的ROS2人机交互界面',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'control_panel = libbot_ui.main_window:main',
        ],
    },
)
