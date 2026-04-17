cmake_minimum_required(VERSION 3.8)
project(libbot_simulation)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

# Install Python package
ament_python_install_package(${PROJECT_NAME})

# Install launch files
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}
)

# Install config files
install(DIRECTORY
  config
  DESTINATION share/${PROJECT_NAME}
)

# Install worlds
install(DIRECTORY
  worlds
  DESTINATION share/${PROJECT_NAME}
)

# Install rviz files
install(DIRECTORY
  rviz
  DESTINATION share/${PROJECT_NAME}
)

# Install models
install(DIRECTORY
  models
  DESTINATION share/${PROJECT_NAME}
)

# Install Python executables to lib/<package>/ for launch files
# Create wrapper scripts that call the Python modules
file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/rfid_sensor_node
"#!/bin/sh
python3 -m ${PROJECT_NAME}.rfid_sensor_node
")
file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/robot_pose_publisher
"#!/bin/sh
python3 -m ${PROJECT_NAME}.robot_pose_publisher
")
file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/rfid_visualizer
"#!/bin/sh
python3 -m ${PROJECT_NAME}.rfid_visualizer
")

install(PROGRAMS
  ${CMAKE_CURRENT_BINARY_DIR}/rfid_sensor_node
  ${CMAKE_CURRENT_BINARY_DIR}/robot_pose_publisher
  ${CMAKE_CURRENT_BINARY_DIR}/rfid_visualizer
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
