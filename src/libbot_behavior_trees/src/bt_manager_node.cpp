#include "libbot_behavior_trees/bt_manager_node.hpp"
#include "libbot_behavior_trees/bt_nodes.hpp"

#include <filesystem>
#include <fstream>
#include <chrono>

namespace libbot_behavior_trees
{

BTManagerNode::BTManagerNode(const rclcpp::NodeOptions & options)
: Node("bt_manager_node", options),
  is_running_(false),
  should_stop_(false),
  tree_status_(BT::NodeStatus::IDLE),
  groot_enabled_(true),
  groot_port_(1666),
  tick_rate_(10.0)
{
    RCLCPP_FATAL(this->get_logger(), "!!! BTManagerNode 构造函数开始执行 !!");
    RCLCPP_INFO(this->get_logger(), "BT Manager节点初始化开始");

    try {
        // 创建ROS2接口
        status_publisher_ = this->create_publisher<std_msgs::msg::String>(
            "/bt/execution_status", 10);
        node_status_publisher_ = this->create_publisher<std_msgs::msg::String>(
            "/bt/node_status", 10);

        // 状态发布定时器
        double status_rate = 2.0;  // 2Hz状态发布
        status_timer_ = this->create_wall_timer(
            std::chrono::duration<double>(1.0 / status_rate),
            std::bind(&BTManagerNode::publishStatus, this));

        // 初始化行为树系统
        initBehaviorTreeSystem();

        RCLCPP_INFO(this->get_logger(), "BT Manager节点初始化完成");
    }
    catch (const std::exception & e) {
        RCLCPP_ERROR(this->get_logger(), "BT Manager初始化失败: %s", e.what());
        throw;
    }
}

BTManagerNode::~BTManagerNode()
{
    stopBehaviorTree();
    should_stop_ = true;
    if (execution_thread_ && execution_thread_->joinable()) {
        execution_thread_->join();
    }
    RCLCPP_INFO(this->get_logger(), "BT Manager节点已关闭");
}

void BTManagerNode::initBehaviorTreeSystem()
{
    RCLCPP_FATAL(this->get_logger(), "!!! initBehaviorTreeSystem() 函数开始执行 !!!");
    try {
        RCLCPP_INFO(this->get_logger(), "初始化行为树系统");

        // 注册自定义节点
        registerCustomNodes();

        // 设置ROS2节点指针供BT节点使用
        ROSConditionNode::setROSNode(this);
        ROSActionNode::setROSNode(this);

        // 初始化Groot可视化
        if (groot_enabled_ && current_tree_ && current_tree_->rootNode()) {
            try {
                groot_publisher_ = std::make_shared<BT::Groot2Publisher>(current_tree_, groot_port_);
                RCLCPP_INFO(this->get_logger(), "Groot可视化已启用，端口: %d", groot_port_);
            }
            catch (const std::exception & e) {
                RCLCPP_WARN(this->get_logger(), "Groot初始化失败: %s", e.what());
            }
        }

        // 启动执行线程
        is_running_ = true;
        execution_thread_ = std::make_unique<std::thread>(
            &BTManagerNode::executionLoop, this);

        // 加载默认行为树
        loadDefaultTrees();

        RCLCPP_INFO(this->get_logger(), "行为树系统初始化完成");
    }
    catch (const std::exception & e) {
        RCLCPP_ERROR(this->get_logger(), "行为树系统初始化失败: %s", e.what());
        throw;
    }
}

void BTManagerNode::registerCustomNodes()
{
    RCLCPP_INFO(this->get_logger(), "注册自定义BT节点");

    // 注册条件节点
    factory_.registerNodeType<IsBookAvailable>("IsBookAvailable");
    factory_.registerNodeType<IsNavigationStuck>("IsNavigationStuck");
    factory_.registerNodeType<IsLocalizationLost>("IsLocalizationLost");
    factory_.registerNodeType<HasActiveErrors>("HasActiveErrors");
    factory_.registerNodeType<CanUseL1Recovery>("CanUseL1Recovery");
    factory_.registerNodeType<CanUseL2Recovery>("CanUseL2Recovery");
    factory_.registerNodeType<HasPendingTasks>("HasPendingTasks");

    // 注册动作节点
    factory_.registerNodeType<NavigateToBookshelf>("NavigateToBookshelf");
    factory_.registerNodeType<ScanForBook>("ScanForBook");
    factory_.registerNodeType<UpdateDatabase>("UpdateDatabase");
    factory_.registerNodeType<PerformSystemCheck>("PerformSystemCheck");
    factory_.registerNodeType<EnterIdleState>("EnterIdleState");
    factory_.registerNodeType<RequestHumanIntervention>("RequestHumanIntervention");

    // 注册恢复节点
    factory_.registerNodeType<L1RecoveryNode>("L1RecoveryNode");
    factory_.registerNodeType<L2RecoveryNode>("L2RecoveryNode");
    factory_.registerNodeType<ErrorDetectionNode>("ErrorDetectionNode");

    RCLCPP_INFO(this->get_logger(), "自定义BT节点注册完成");
}

void BTManagerNode::loadDefaultTrees()
{
    RCLCPP_FATAL(this->get_logger(), "!!! loadDefaultTrees() 函数开始执行 !!!");
    try {
        RCLCPP_ERROR(this->get_logger(), "=== 开始从XML文件加载默认行为树 ===");

        // 从XML文件加载行为树
        std::string package_path = "/home/lhl/lib_bot_ws/install/libbot_behavior_trees/share/libbot_behavior_trees";

        // 加载主行为树
        std::string main_tree_path = package_path + "/behaviors/main_bt.xml";
        RCLCPP_INFO(this->get_logger(), "正在加载主行为树: %s", main_tree_path.c_str());
        if (!loadBehaviorTree("main_tree", main_tree_path)) {
            throw std::runtime_error("Failed to load main_tree from XML: " + main_tree_path);
        }

        // 加载恢复行为树
        if (!loadBehaviorTree("recovery_tree", package_path + "/behaviors/recovery_bt.xml")) {
            throw std::runtime_error("Failed to load recovery_tree from XML");
        }

        // 加载找书行为树
        if (!loadBehaviorTree("findbook_tree", package_path + "/behaviors/findbook_bt.xml")) {
            throw std::runtime_error("Failed to load findbook_tree from XML");
        }

        // 默认启动main_tree
        if (!loaded_trees_["main_tree"] || !loaded_trees_["main_tree"]->rootNode()) {
            throw std::runtime_error("Failed to create main tree");
        }

        current_tree_.reset(new BT::Tree(*(loaded_trees_["main_tree"])));
        active_tree_name_ = "main_tree";

        // 调试：输出当前树的根节点名称
        RCLCPP_ERROR(this->get_logger(), "当前活跃树: %s, 根节点: %s",
                    active_tree_name_.c_str(),
                    current_tree_->rootNode()->name().c_str());

        RCLCPP_ERROR(this->get_logger(), "=== 成功从XML文件加载了 %zu 个默认行为树 ===", loaded_trees_.size());
    }
    catch (const std::exception & e) {
        RCLCPP_ERROR(this->get_logger(), "加载默认行为树失败: %s", e.what());
        throw;
    }
}

bool BTManagerNode::loadBehaviorTree(const std::string & tree_name, const std::string & xml_path)
{
    try {
        std::lock_guard<std::mutex> lock(tree_mutex_);

        RCLCPP_INFO(this->get_logger(), "尝试加载行为树 '%s' 从文件: %s", tree_name.c_str(), xml_path.c_str());

        if (!std::filesystem::exists(xml_path)) {
            RCLCPP_ERROR(this->get_logger(), "行为树文件不存在: %s", xml_path.c_str());
            return false;
        }

        // 读取XML文件
        std::ifstream file(xml_path);
        std::string xml_content((std::istreambuf_iterator<char>(file)),
                               std::istreambuf_iterator<char>());

        RCLCPP_INFO(this->get_logger(), "XML文件内容长度: %zu 字符", xml_content.length());

        // 创建行为树
        auto tree = std::make_unique<BT::Tree>(factory_.createTreeFromText(xml_content));
        loaded_trees_[tree_name] = std::move(tree);

        RCLCPP_INFO(this->get_logger(), "成功从XML文件加载行为树: %s", tree_name.c_str());
        return true;
    }
    catch (const std::exception & e) {
        RCLCPP_ERROR(this->get_logger(), "加载行为树 %s 失败: %s",
                    tree_name.c_str(), e.what());
        return false;
    }
}

bool BTManagerNode::startBehaviorTree(const std::string & tree_name)
{
    try {
        std::lock_guard<std::mutex> lock(tree_mutex_);

        auto it = loaded_trees_.find(tree_name);
        if (it == loaded_trees_.end() || !it->second) {
            RCLCPP_ERROR(this->get_logger(), "找不到行为树: %s", tree_name.c_str());
            return false;
        }

        // 停止当前运行的树
        if (current_tree_ && current_tree_->rootNode()) {
            current_tree_->haltTree();
        }

        // 切换到新树
        current_tree_.reset(new BT::Tree(*(it->second)));
        active_tree_name_ = tree_name;
        tree_status_ = BT::NodeStatus::IDLE;

        RCLCPP_INFO(this->get_logger(), "启动行为树: %s", tree_name.c_str());
        return true;
    }
    catch (const std::exception & e) {
        RCLCPP_ERROR(this->get_logger(), "启动行为树 %s 失败: %s",
                    tree_name.c_str(), e.what());
        return false;
    }
}

bool BTManagerNode::stopBehaviorTree()
{
    try {
        std::lock_guard<std::mutex> lock(tree_mutex_);

        if (current_tree_.rootNode()) {
            current_tree_.haltTree();
            tree_status_ = BT::NodeStatus::IDLE;
            active_tree_name_.clear();

            RCLCPP_INFO(this->get_logger(), "行为树已停止");
            return true;
        }

        return false;
    }
    catch (const std::exception & e) {
        RCLCPP_ERROR(this->get_logger(), "停止行为树失败: %s", e.what());
        return false;
    }
}

bool BTManagerNode::reloadBehaviorTree(const std::string & tree_name)
{
    try {
        // 从XML文件重新加载指定树
        std::string package_path = "/home/lhl/lib_bot_ws/install/libbot_behavior_trees/share/libbot_behavior_trees";
        std::string xml_path;

        if (tree_name == "main_tree") {
            xml_path = package_path + "/behaviors/main_bt.xml";
        }
        else if (tree_name == "recovery_tree") {
            xml_path = package_path + "/behaviors/recovery_bt.xml";
        }
        else if (tree_name == "findbook_tree") {
            xml_path = package_path + "/behaviors/findbook_bt.xml";
        }
        else {
            RCLCPP_ERROR(this->get_logger(), "未知行为树类型: %s", tree_name.c_str());
            return false;
        }

        // 使用现有的loadBehaviorTree方法重新加载
        return loadBehaviorTree(tree_name, xml_path);

        // 如果当前活跃的是这个树，重新切换到它
        if (active_tree_name_ == tree_name) {
            startBehaviorTree(tree_name);
        }

        RCLCPP_INFO(this->get_logger(), "成功重载行为树: %s", tree_name.c_str());
        return true;
    }
    catch (const std::exception & e) {
        RCLCPP_ERROR(this->get_logger(), "重载行为树 %s 失败: %s",
                    tree_name.c_str(), e.what());
        return false;
    }
}

void BTManagerNode::executionLoop()
{
    auto tick_interval = std::chrono::duration<double>(1.0 / tick_rate_);

    while (rclcpp::ok() && !should_stop_) {
        try {
            auto start_time = std::chrono::steady_clock::now();

            // 执行行为树tick
            std::lock_guard<std::mutex> lock(tree_mutex_);
            if (current_tree_.rootNode()) {
                tree_status_ = current_tree_->tickOnce();
            }

            // 计算执行时间
            auto execution_time = std::chrono::steady_clock::now() - start_time;
            auto execution_duration = std::chrono::duration_cast<std::chrono::milliseconds>(execution_time);

            if (execution_duration.count() > 100) {  // 超过100ms
                RCLCPP_WARN(this->get_logger(), "行为树执行超时: %ldms", execution_duration.count());
            }

            // 等待下一个tick
            std::this_thread::sleep_for(tick_interval);

        }
        catch (const std::exception & e) {
            RCLCPP_ERROR(this->get_logger(), "行为树执行循环错误: %s", e.what());
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    }
}

void BTManagerNode::publishStatus()
{
    try {
        std_msgs::msg::String status_msg;
        std_msgs::msg::String node_msg;

        std::lock_guard<std::mutex> lock(tree_mutex_);

        // 发布执行状态
        if (!active_tree_name_.empty() && current_tree_ && current_tree_->rootNode()) {
            std::string status_text = "Active: " + active_tree_name_ +
                                    ", Status: " + BT::toStr(tree_status_);
            status_msg.data = status_text;
        }
        else {
            status_msg.data = "No active behavior tree";
        }

        status_publisher_->publish(status_msg);

        // 发布节点状态
        if (current_tree_ && current_tree_->rootNode()) {
            std::string node_text = "Node: " + current_tree_->rootNode()->name() +
                                  ", Status: " + BT::toStr(current_tree_->rootNode()->status());
            node_msg.data = node_text;
            node_status_publisher_->publish(node_msg);
        }
    }
    catch (const std::exception & e) {
        RCLCPP_ERROR(this->get_logger(), "发布行为树状态错误: %s", e.what());
    }
}


}  // namespace libbot_behavior_trees