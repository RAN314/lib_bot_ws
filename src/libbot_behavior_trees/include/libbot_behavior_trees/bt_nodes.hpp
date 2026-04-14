#ifndef LIBBOT_BEHAVIOR_TREES_BT_NODES_HPP
#define LIBBOT_BEHAVIOR_TREES_BT_NODES_HPP

#include <memory>
#include <string>
#include <chrono>

#include <rclcpp/rclcpp.hpp>
#include <behaviortree_cpp/action_node.h>
#include <behaviortree_cpp/condition_node.h>

namespace libbot_behavior_trees
{

// 条件节点基类
class ROSConditionNode : public BT::ConditionNode
{
public:
    ROSConditionNode(const std::string & name, const BT::NodeConfiguration & config)
    : BT::ConditionNode(name, config) {}

    // 子类必须实现tick()方法
    virtual BT::NodeStatus tick() override = 0;

public:
    // ROS2节点指针，子类可以通过这个访问ROS2功能
    static rclcpp::Node* getROSNode() { return ros_node_; }
    static void setROSNode(rclcpp::Node* node) { ros_node_ = node; }

private:
    static rclcpp::Node* ros_node_;
};

// 动作节点基类
class ROSActionNode : public BT::SyncActionNode
{
public:
    ROSActionNode(const std::string & name, const BT::NodeConfiguration & config)
    : BT::SyncActionNode(name, config) {}

    // 子类必须实现tick()方法
    virtual BT::NodeStatus tick() override = 0;

public:
    // ROS2节点指针，子类可以通过这个访问ROS2功能
    static rclcpp::Node* getROSNode() { return ros_node_; }
    static void setROSNode(rclcpp::Node* node) { ros_node_ = node; }

private:
    static rclcpp::Node* ros_node_;
};

// 具体的条件节点实现
class IsBookAvailable : public ROSConditionNode
{
public:
    IsBookAvailable(const std::string & name, const BT::NodeConfiguration & config)
    : ROSConditionNode(name, config) {}

    BT::NodeStatus tick() override;
    static BT::PortsList providedPorts() { return {}; }
};

class IsNavigationStuck : public ROSConditionNode
{
public:
    IsNavigationStuck(const std::string & name, const BT::NodeConfiguration & config)
    : ROSConditionNode(name, config) {}

    BT::NodeStatus tick() override;
    static BT::PortsList providedPorts() { return {}; }
};

class IsLocalizationLost : public ROSConditionNode
{
public:
    IsLocalizationLost(const std::string & name, const BT::NodeConfiguration & config)
    : ROSConditionNode(name, config) {}

    BT::NodeStatus tick() override;
    static BT::PortsList providedPorts() { return {}; }
};

class HasActiveErrors : public ROSConditionNode
{
public:
    HasActiveErrors(const std::string & name, const BT::NodeConfiguration & config)
    : ROSConditionNode(name, config) {}

    BT::NodeStatus tick() override;
    static BT::PortsList providedPorts() { return {}; }
};

class CanUseL1Recovery : public ROSConditionNode
{
public:
    CanUseL1Recovery(const std::string & name, const BT::NodeConfiguration & config)
    : ROSConditionNode(name, config) {}

    BT::NodeStatus tick() override;
    static BT::PortsList providedPorts() { return {}; }
};

class CanUseL2Recovery : public ROSConditionNode
{
public:
    CanUseL2Recovery(const std::string & name, const BT::NodeConfiguration & config)
    : ROSConditionNode(name, config) {}

    BT::NodeStatus tick() override;
    static BT::PortsList providedPorts() { return {}; }
};

class HasPendingTasks : public ROSConditionNode
{
public:
    HasPendingTasks(const std::string & name, const BT::NodeConfiguration & config)
    : ROSConditionNode(name, config) {}

    BT::NodeStatus tick() override;
    static BT::PortsList providedPorts() { return {}; }
};

class ShouldMonitorSystem : public ROSConditionNode
{
public:
    ShouldMonitorSystem(const std::string & name, const BT::NodeConfiguration & config)
    : ROSConditionNode(name, config) {}

    BT::NodeStatus tick() override;
    static BT::PortsList providedPorts() { return {}; }
};

// 具体的动作节点实现
class NavigateToBookshelf : public ROSActionNode
{
public:
    NavigateToBookshelf(const std::string & name, const BT::NodeConfiguration & config)
    : ROSActionNode(name, config) {}

    BT::NodeStatus tick() override;
    static BT::PortsList providedPorts() { return {}; }
};

class ScanForBook : public ROSActionNode
{
public:
    ScanForBook(const std::string & name, const BT::NodeConfiguration & config)
    : ROSActionNode(name, config) {}

    BT::NodeStatus tick() override;
    static BT::PortsList providedPorts() { return {}; }
};

class UpdateDatabase : public ROSActionNode
{
public:
    UpdateDatabase(const std::string & name, const BT::NodeConfiguration & config)
    : ROSActionNode(name, config) {}

    BT::NodeStatus tick() override;
    static BT::PortsList providedPorts() { return {}; }
};

class PerformSystemCheck : public ROSActionNode
{
public:
    PerformSystemCheck(const std::string & name, const BT::NodeConfiguration & config)
    : ROSActionNode(name, config) {}

    BT::NodeStatus tick() override;
    static BT::PortsList providedPorts() { return {}; }
};

class EnterIdleState : public ROSActionNode
{
public:
    EnterIdleState(const std::string & name, const BT::NodeConfiguration & config)
    : ROSActionNode(name, config) {}

    BT::NodeStatus tick() override;
    static BT::PortsList providedPorts() { return {}; }
};

class RequestHumanIntervention : public ROSActionNode
{
public:
    RequestHumanIntervention(const std::string & name, const BT::NodeConfiguration & config)
    : ROSActionNode(name, config) {}

    BT::NodeStatus tick() override;
    static BT::PortsList providedPorts() { return {}; }
};

// 恢复节点
class L1RecoveryNode : public ROSActionNode
{
public:
    L1RecoveryNode(const std::string & name, const BT::NodeConfiguration & config)
    : ROSActionNode(name, config) {}

    BT::NodeStatus tick() override;
    static BT::PortsList providedPorts() { return {}; }
};

class L2RecoveryNode : public ROSActionNode
{
public:
    L2RecoveryNode(const std::string & name, const BT::NodeConfiguration & config)
    : ROSActionNode(name, config) {}

    BT::NodeStatus tick() override;
    static BT::PortsList providedPorts() { return {}; }
};

class ErrorDetectionNode : public ROSActionNode
{
public:
    ErrorDetectionNode(const std::string & name, const BT::NodeConfiguration & config)
    : ROSActionNode(name, config) {}

    BT::NodeStatus tick() override;
    static BT::PortsList providedPorts() { return {}; }
};

}  // namespace libbot_behavior_trees

#endif  // LIBBOT_BEHAVIOR_TREES_BT_NODES_HPP