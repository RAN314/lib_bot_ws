cmake_minimum_required(VERSION 3.8)
project(libbot_ui)

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

# Install Python executables to lib/<package>/ for launch files
# Create wrapper scripts that call the Python modules
file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/main_window
"#!/bin/sh
python3 -m ${PROJECT_NAME}.main_window
")

install(PROGRAMS
  ${CMAKE_CURRENT_BINARY_DIR}/main_window
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()