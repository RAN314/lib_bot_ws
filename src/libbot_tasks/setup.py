from setuptools import find_packages, setup

package_name = 'libbot_tasks'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='开发者',
    maintainer_email='developer@example.com',
    description='图书馆机器人任务包 - L1恢复行为实现',
    license='Apache License 2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'l1_recovery_node = libbot_tasks.l1_recovery_node:main',
        ],
    },
)
