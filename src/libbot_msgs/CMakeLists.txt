cmake_minimum_required(VERSION 3.8)
project(libbot_msgs)

# 检查CMake版本
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 查找依赖
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

# 定义消息文件
set(msg_files
  "msg/RFIDScan.msg"
  "msg/SystemHealth.msg"
)

# 定义服务文件
set(srv_files
  "srv/GetBookInfo.srv"
  "srv/UpdateBookLocation.srv"
  "srv/CheckRobotStatus.srv"
)

# 定义Action文件
set(action_files
  "action/FindBook.action"
  "action/PerformInventory.action"
)

# 生成消息、服务和Action
rosidl_generate_interfaces(${PROJECT_NAME}
  ${msg_files}
  ${srv_files}
  ${action_files}
  DEPENDENCIES
    std_msgs
    geometry_msgs
  ADD_LINTER_TESTS
)

# 导出依赖
ament_export_dependencies(rosidl_default_runtime)

# 添加测试
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
