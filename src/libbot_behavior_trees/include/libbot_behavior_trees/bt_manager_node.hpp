#ifndef LIBBOT_BEHAVIOR_TREES_BT_MANAGER_NODE_HPP
#define LIBBOT_BEHAVIOR_TREES_BT_MANAGER_NODE_HPP

#include <memory>
#include <string>
#include <vector>
#include <map>
#include <thread>
#include <mutex>
#include <atomic>

#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>

#include <behaviortree_cpp/bt_factory.h>
#include <behaviortree_cpp/loggers/bt_cout_logger.h>
#include <behaviortree_cpp/loggers/groot2_publisher.h>

namespace libbot_behavior_trees
{

class BTManagerNode : public rclcpp::Node
{
public:
    explicit BTManagerNode(const rclcpp::NodeOptions & options = rclcpp::NodeOptions());
    virtual ~BTManagerNode();

    // 行为树管理接口
    bool loadBehaviorTree(const std::string & tree_name, const std::string & xml_path);
    bool startBehaviorTree(const std::string & tree_name);
    bool stopBehaviorTree();
    bool reloadBehaviorTree(const std::string & tree_name);

    // 状态查询接口
    std::string getActiveTreeName() const { return active_tree_name_; }
    BT::NodeStatus getTreeStatus() const { return tree_status_; }
    bool isRunning() const { return is_running_; }

protected:
    // 行为树系统初始化
    void initBehaviorTreeSystem();

    // 注册自定义节点
    void registerCustomNodes();

    // 加载默认行为树
    void loadDefaultTrees();

    // 执行循环
    void executionLoop();

    // 发布状态
    void publishStatus();


private:
    // ROS2接口
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr status_publisher_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr node_status_publisher_;
    rclcpp::TimerBase::SharedPtr status_timer_;

    // 行为树相关
    BT::BehaviorTreeFactory factory_;
    BT::Tree current_tree_;
    std::map<std::string, std::unique_ptr<BT::Tree>> loaded_trees_;

    // Groot可视化
    std::shared_ptr<BT::Groot2Publisher> groot_publisher_;
    bool groot_enabled_;
    int groot_port_;

    // 执行状态
    std::atomic<bool> is_running_;
    std::atomic<bool> should_stop_;
    std::string active_tree_name_;
    BT::NodeStatus tree_status_;

    // 线程和同步
    std::unique_ptr<std::thread> execution_thread_;
    mutable std::mutex tree_mutex_;

    // 配置参数
    double tick_rate_;
    std::map<std::string, std::string> tree_configs_;
};

}  // namespace libbot_behavior_trees

#endif  // LIBBOT_BEHAVIOR_TREES_BT_MANAGER_NODE_HPP