#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导航错误检测器 - 检测导航和路径规划相关问题
实现机器人卡住、路径规划失败等检测
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from nav2_msgs.srv import GetCostmap
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Path, Odometry
import time
import threading


class NavigationErrorDetector:
    """导航错误检测器 - 检测导航和路径规划相关问题"""

    def __init__(self, node: Node):
        """初始化导航错误检测器"""
        self.node = node
        self.stuck_timeout = 30.0          # 卡住超时(秒)
        self.planning_timeout = 10.0       # 规划超时(秒)
        self.collision_distance_threshold = 0.3  # 碰撞距离阈值(m)
        self.goal_unreachable_timeout = 60.0     # 目标不可达超时(秒)

        # 状态跟踪
        self.last_odom_time = None
        self.last_position = None
        self.last_movement_time = None
        self.current_goal = None
        self.goal_start_time = None
        self.planning_start_time = None
        self.is_planning = False

        # 从参数服务器加载配置
        self._load_parameters()

        # 订阅相关Topic
        self.odom_sub = node.create_subscription(
            Odometry,
            '/odom',
            self._odom_callback,
            10
        )

        self.path_sub = node.create_subscription(
            Path,
            '/plan',
            self._path_callback,
            10
        )

        self.cmd_vel_sub = node.create_subscription(
            Twist,
            '/cmd_vel',
            self._cmd_vel_callback,
            10
        )

        # 创建导航Action客户端
        self.nav_client = ActionClient(
            node, NavigateToPose, '/navigate_to_pose'
        )

        # 创建代价地图服务客户端
        self.costmap_client = node.create_client(GetCostmap, '/global_costmap/get_costmap')

    def _load_parameters(self):
        """加载检测参数"""
        try:
            self.stuck_timeout = self.node.declare_parameter(
                'detection.navigation.stuck_timeout', 30.0
            ).value
            self.planning_timeout = self.node.declare_parameter(
                'detection.navigation.planning_timeout', 10.0
            ).value
            self.collision_distance_threshold = self.node.declare_parameter(
                'detection.navigation.collision_distance_threshold', 0.3
            ).value
            self.goal_unreachable_timeout = self.node.declare_parameter(
                'detection.navigation.goal_unreachable_timeout', 60.0
            ).value

            self.node.get_logger().info("导航检测器参数加载完成")
        except Exception as e:
            self.node.get_logger().warn(f"导航检测器参数加载失败: {str(e)}")

    def detect(self) -> list:
        """执行导航错误检测

        Returns:
            检测到的错误列表
        """
        errors = []

        # 检测机器人是否卡住
        errors.extend(self._check_robot_stuck())

        # 检测路径规划失败
        errors.extend(self._check_planning_failure())

        # 检测目标不可达
        errors.extend(self._check_goal_unreachable())

        # 检测碰撞风险
        errors.extend(self._check_collision_risk())

        return errors

    def _odom_callback(self, msg: Odometry):
        """里程计消息回调"""
        current_time = time.time()
        current_position = msg.pose.pose.position

        # 更新位置和时间
        if self.last_position:
            # 计算移动距离
            dx = current_position.x - self.last_position.x
            dy = current_position.y - self.last_position.y
            distance = (dx*dx + dy*dy)**0.5

            # 如果移动了显著距离，更新最后移动时间
            if distance > 0.01:  # 1cm阈值
                self.last_movement_time = current_time

        self.last_position = current_position
        self.last_odom_time = current_time

    def _path_callback(self, msg: Path):
        """路径消息回调"""
        # 路径规划开始
        if not self.is_planning:
            self.is_planning = True
            self.planning_start_time = time.time()

        # 检查路径规划是否超时
        if self.planning_start_time:
            planning_duration = time.time() - self.planning_start_time
            if planning_duration > self.planning_timeout:
                # 规划超时，但这里不立即报错，等待detect()方法统一处理
                pass

    def _cmd_vel_callback(self, msg: Twist):
        """速度命令回调"""
        # 检查是否有速度命令
        linear_velocity = (msg.linear.x**2 + msg.linear.y**2 + msg.linear.z**2)**0.5
        angular_velocity = (msg.angular.x**2 + msg.angular.y**2 + msg.angular.z**2)**0.5

        # 如果有显著的速度命令，重置规划状态
        if linear_velocity > 0.01 or angular_velocity > 0.01:
            self.is_planning = False
            self.planning_start_time = None

    def _check_robot_stuck(self) -> list:
        """检查机器人是否卡住"""
        errors = []

        if not self.last_movement_time or not self.last_odom_time:
            return errors

        # 计算机器人停止移动的时间
        current_time = time.time()
        time_since_movement = current_time - self.last_movement_time

        if time_since_movement > self.stuck_timeout:
            errors.append({
                'error_type': 'navigation_stuck',
                'message': f'机器人卡住: {time_since_movement:.1f} 秒无移动',
                'time_stuck': time_since_movement,
                'last_position': {
                    'x': self.last_position.x,
                    'y': self.last_position.y
                }
            })

        return errors

    def _check_planning_failure(self) -> list:
        """检查路径规划失败"""
        errors = []

        if self.is_planning and self.planning_start_time:
            planning_duration = time.time() - self.planning_start_time

            if planning_duration > self.planning_timeout:
                errors.append({
                    'error_type': 'path_planning_failed',
                    'message': f'路径规划超时: {planning_duration:.1f} 秒',
                    'planning_duration': planning_duration,
                    'timeout_threshold': self.planning_timeout
                })

        return errors

    def _check_goal_unreachable(self) -> list:
        """检查目标不可达"""
        errors = []

        # 这里需要跟踪当前的导航目标
        # 在实际实现中，可以通过监听导航Action的状态来获取
        if self.goal_start_time:
            goal_duration = time.time() - self.goal_start_time

            if goal_duration > self.goal_unreachable_timeout:
                errors.append({
                    'error_type': 'goal_unreachable',
                    'message': f'目标可能不可达: {goal_duration:.1f} 秒未完成',
                    'goal_duration': goal_duration,
                    'timeout_threshold': self.goal_unreachable_timeout
                })

        return errors

    def _check_collision_risk(self) -> list:
        """检查碰撞风险"""
        errors = []

        try:
            # 尝试获取代价地图
            if not self.costmap_client.wait_for_service(timeout_sec=1.0):
                return errors  # 服务不可用，不报错

            request = GetCostmap.Request()
            future = self.costmap_client.call_async(request)

            # 等待服务响应
            if future.wait_for_result(timeout_sec=2.0):
                result = future.result()
                if result:
                    # 分析代价地图检测碰撞风险
                    # 这里简化实现，实际应该分析机器人周围的代价
                    collision_risk = self._analyze_costmap_for_collision(result)
                    if collision_risk > 0.8:  # 80%碰撞风险
                        errors.append({
                            'error_type': 'collision_imminent',
                            'message': f'检测到碰撞风险: {collision_risk:.2f}',
                            'collision_risk': collision_risk
                        })

        except Exception as e:
            # 获取代价地图失败，但不认为是错误
            pass

        return errors

    def _analyze_costmap_for_collision(self, costmap) -> float:
        """分析代价地图检测碰撞风险"""
        # 简化的碰撞风险分析
        # 实际实现应该考虑机器人形状和周围的障碍物
        try:
            # 获取代价地图数据
            width = costmap.metadata.size_x
            height = costmap.metadata.size_y
            data = costmap.data

            # 检查机器人周围的区域（简化为中心区域）
            center_x = width // 2
            center_y = height // 2
            check_radius = 5  # 检查半径

            high_cost_count = 0
            total_checked = 0

            for dx in range(-check_radius, check_radius + 1):
                for dy in range(-check_radius, check_radius + 1):
                    x = center_x + dx
                    y = center_y + dy

                    if 0 <= x < width and 0 <= y < height:
                        index = y * width + x
                        if index < len(data):
                            cost = data[index]
                            if cost > 80:  # 高代价表示障碍物
                                high_cost_count += 1
                            total_checked += 1

            if total_checked > 0:
                return high_cost_count / total_checked
            else:
                return 0.0

        except Exception:
            return 0.0

    def register_navigation_goal(self, goal_pose):
        """注册新的导航目标（用于跟踪）"""
        self.current_goal = goal_pose
        self.goal_start_time = time.time()

    def clear_navigation_goal(self):
        """清除当前导航目标"""
        self.current_goal = None
        self.goal_start_time = None

    def get_status(self) -> dict:
        """获取检测器状态"""
        status = {
            'last_odom_time': self.last_odom_time,
            'last_movement_time': self.last_movement_time,
            'current_goal': self.current_goal,
            'goal_start_time': self.goal_start_time,
            'is_planning': self.is_planning,
            'planning_start_time': self.planning_start_time,
            'stuck_timeout': self.stuck_timeout,
            'planning_timeout': self.planning_timeout,
            'goal_timeout': self.goal_unreachable_timeout
        }
        return status

    def reset(self):
        """重置检测器"""
        self.last_odom_time = None
        self.last_position = None
        self.last_movement_time = None
        self.current_goal = None
        self.goal_start_time = None
        self.planning_start_time = None
        self.is_planning = False
        self.node.get_logger().info("导航错误检测器已重置")


def main():
    """测试函数"""
    import rclpy

    rclpy.init()

    # 创建测试节点
    test_node = Node("navigation_detector_test")

    # 创建导航检测器实例
    detector = NavigationErrorDetector(test_node)

    try:
        print("🧪 导航错误检测器测试")
        print("等待导航数据...")

        # 运行测试10秒
        start_time = time.time()
        while time.time() - start_time < 10.0:
            rclpy.spin_once(test_node, timeout_sec=0.1)

            # 模拟检测
            errors = detector.detect()
            if errors:
                for error in errors:
                    print(f"检测到错误: {error}")

    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
    finally:
        # 清理
        test_node.destroy_node()
        rclpy.shutdown()

    print("✅ 导航错误检测器测试完成")


if __name__ == "__main__":
    main()