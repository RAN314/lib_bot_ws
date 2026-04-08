from setuptools import find_packages, setup

package_name = "test_action_cancel"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="lhl",
    maintainer_email="1412046028@qq.com",
    description="TODO: Package description",
    license="TODO: License declaration",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "test_cancel_server = test_action_cancel.test_cancel_server:main",
            "test_cancel_client = test_action_cancel.test_cancel_client:main",
            "control_publisher = test_action_cancel.control_publisher:main",
        ],
    },
)
