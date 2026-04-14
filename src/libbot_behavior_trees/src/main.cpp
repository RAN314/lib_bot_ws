#include <chrono>
#include <memory>
#include <string>
#include <thread>

// Groot2 & BT.CPP
#include "behaviortree_cpp/bt_factory.h"
#include "behaviortree_cpp/loggers/bt_cout_logger.h"
#include "behaviortree_cpp/loggers/groot2_publisher.h"

// ROS 2
#include <ament_index_cpp/get_package_share_directory.hpp>

#include "rclcpp/rclcpp.hpp"

// 自定义节点
#include "libbot_behavior_trees/bt_nodes.hpp"

int main(int argc, char* argv[]) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<rclcpp::Node>("libbot_bt_manager");

  // 获取包路径
  std::string package_share_directory =
      ament_index_cpp::get_package_share_directory("libbot_behavior_trees");

  // --- 参数获取与初始化 ---
  std::string tree_file = "";
  bool groot_logger = true;
  int groot_client_port = 1666;
  int server_timeout = 10000;
  int bt_loop_duration = 100;
  int wait_for_service_timeout = 5000;

  if (tree_file.empty()) {
    // 默认加载主行为树
    tree_file = "main_bt.xml";
  }

  // 拼接完整的绝对路径
  std::string tree_path = package_share_directory + "/behaviors/" + tree_file;
  RCLCPP_INFO(node->get_logger(), "Loading Behavior Tree from: %s",
              tree_path.c_str());

  // --- 注册节点类型 ---
  BT::BehaviorTreeFactory factory;
  try {
    // 注册所有自定义节点
    factory.registerNodeType<libbot_behavior_trees::IsBookAvailable>("IsBookAvailable");
    factory.registerNodeType<libbot_behavior_trees::IsNavigationStuck>("IsNavigationStuck");
    factory.registerNodeType<libbot_behavior_trees::IsLocalizationLost>("IsLocalizationLost");
    factory.registerNodeType<libbot_behavior_trees::HasActiveErrors>("HasActiveErrors");
    factory.registerNodeType<libbot_behavior_trees::HasPendingTasks>("HasPendingTasks");
    factory.registerNodeType<libbot_behavior_trees::ShouldMonitorSystem>("ShouldMonitorSystem");
    factory.registerNodeType<libbot_behavior_trees::CanUseL1Recovery>("CanUseL1Recovery");
    factory.registerNodeType<libbot_behavior_trees::CanUseL2Recovery>("CanUseL2Recovery");

    factory.registerNodeType<libbot_behavior_trees::NavigateToBookshelf>("NavigateToBookshelf");
    factory.registerNodeType<libbot_behavior_trees::ScanForBook>("ScanForBook");
    factory.registerNodeType<libbot_behavior_trees::UpdateDatabase>("UpdateDatabase");
    factory.registerNodeType<libbot_behavior_trees::PerformSystemCheck>("PerformSystemCheck");
    factory.registerNodeType<libbot_behavior_trees::EnterIdleState>("EnterIdleState");
    factory.registerNodeType<libbot_behavior_trees::RequestHumanIntervention>("RequestHumanIntervention");

    factory.registerNodeType<libbot_behavior_trees::L1RecoveryNode>("L1RecoveryNode");
    factory.registerNodeType<libbot_behavior_trees::L2RecoveryNode>("L2RecoveryNode");
    factory.registerNodeType<libbot_behavior_trees::ErrorDetectionNode>("ErrorDetectionNode");

    // 从XML文件注册行为树
    factory.registerBehaviorTreeFromFile(tree_path);
  } catch (const std::exception& ex) {
    RCLCPP_FATAL(node->get_logger(), "Node registration failed: %s", ex.what());
    rclcpp::shutdown();
    return 1;
  }

  // --- 配置 Blackboard ---
  auto blackboard = BT::Blackboard::create();
  blackboard->set<rclcpp::Node::SharedPtr>("node", node);
  blackboard->set<std::chrono::milliseconds>(
      "server_timeout", std::chrono::milliseconds(server_timeout));
  blackboard->set<std::chrono::milliseconds>(
      "bt_loop_duration", std::chrono::milliseconds(bt_loop_duration));
  blackboard->set<std::chrono::milliseconds>(
      "wait_for_service_timeout",
      std::chrono::milliseconds(wait_for_service_timeout));

  // --- 实例化行为树 ---
  BT::Tree tree;
  try {
    tree = factory.createTree("MainBehaviorTree", blackboard);
  } catch (const std::exception& ex) {
    RCLCPP_FATAL(node->get_logger(), "Failed to create BT: %s", ex.what());
    rclcpp::shutdown();
    return 1;
  }

  // --- 配置 Loggers ---
  BT::StdCoutLogger logger_cout(tree);
  std::shared_ptr<BT::Groot2Publisher> groot_pub = nullptr;

  if (groot_logger) {
    try {
      groot_pub =
          std::make_shared<BT::Groot2Publisher>(tree, groot_client_port);
      RCLCPP_INFO(node->get_logger(), "Groot2 publisher started on port %d",
                  groot_client_port);
    } catch (const std::exception& ex) {
      RCLCPP_WARN(node->get_logger(), "Failed to start Groot2: %s", ex.what());
    }
  }

  // --- 主执行循环 ---
  rclcpp::WallRate loop_rate{std::chrono::milliseconds(bt_loop_duration)};
  int tick_count = 0;
  RCLCPP_INFO(node->get_logger(),
              "Bobo Behavior Tree is continuously running...");

  while (rclcpp::ok()) {
    rclcpp::spin_some(node);
    tick_count++;

    try {
      auto status = tree.tickExactlyOnce();

      // 每10次tick打印一次状态
      if (tick_count % 10 == 0) {
        RCLCPP_INFO_THROTTLE(node->get_logger(), *node->get_clock(), 2000,
                             "Tick #%d - Status: %s", tick_count,
                             BT::toStr(status).c_str());
      }
    } catch (const std::exception& ex) {
      RCLCPP_ERROR(node->get_logger(), "Exception during tree tick: %s",
                   ex.what());
    }

    loop_rate.sleep();
  }

  // --- 优雅退出 ---
  rclcpp::shutdown();
  return 0;
}