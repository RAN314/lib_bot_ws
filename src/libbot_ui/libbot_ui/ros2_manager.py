#!/usr/bin/env python3

from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread, QMetaObject, Qt
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
import threading
import weakref

# 导入L1和L2恢复集成
from .l1_recovery_integration import L1RecoveryIntegration
from .l2_recovery_integration import L2RecoveryIntegration


class Ros2Manager(QObject):
    """ROS2通信管理器 - 封装所有ROS2通信逻辑"""

    # ========== Signals (Qt信号，用于线程安全通信) ==========

    # 任务状态更新
    # 发送: {"task_id": "task_42", "status": "navigating", "progress": 75}
    task_status_updated = pyqtSignal(dict)

    # 机器人位置更新
    # 发送: {"x": 5.2, "y": 3.1, "yaw": 0.5}
    robot_pose_updated = pyqtSignal(dict)

    # 图书检测到
    # 发送: {"book_id": "978316...", "signal_strength": 0.85}
    book_detected = pyqtSignal(dict)

    # 系统健康状态
    # 发送: {"navigation_health": 0.95, "perception_health": 0.90}
    system_health_updated = pyqtSignal(dict)

    # 错误发生
    # 发送: {"error_code": "ACTION_TIMEOUT", "message": "..."}
    error_occurred = pyqtSignal(dict)

    # 图书信息收到
    # 发送: 图书信息字典
    book_info_received = pyqtSignal(dict)

    # ========== 初始化 ==========

    def __init__(self, node_name="libbot_ui_manager"):
        """初始化ROS2管理器

        Args:
            node_name: ROS2节点名称
        """
        super().__init__()

        self.node_name = node_name
        self.node = None
        self.executor = None
        self.executor_thread = None

        # Action客户端
        self.find_book_action_client = None
        self.current_goal_handle = None

        # Service客户端
        self.get_book_info_client = None

        # L1恢复集成
        self.l1_recovery_integration = None

        # L2恢复集成
        self.l2_recovery_integration = None

        # 定时器
        self.health_check_timer = None

        # 初始化ROS2
        self._init_ros2()

    def _init_ros2(self):
        """初始化ROS2环境"""
        try:
            # 初始化rclpy（如果尚未初始化）
            try:
                if not rclpy.ok():
                    rclpy.init()
            except:
                # 如果已经初始化，忽略错误
                pass

            # 创建节点
            self.node = Node(self.node_name)

            # 创建Action客户端
            try:
                from libbot_msgs.action import FindBook

                self.find_book_action_client = ActionClient(
                    self.node, FindBook, "/find_book",
                    callback_group=ReentrantCallbackGroup()
                )

                # 检查Action服务器是否可用（非阻塞）
                if not self.find_book_action_client.wait_for_server(timeout_sec=1.0):
                    self.node.get_logger().warn(
                        "/find_book Action server not available, running in simulation mode"
                    )
                    # 保持客户端，但将在send_find_book_goal中处理不可用情况
                else:
                    self.node.get_logger().info("/find_book Action server connected")

            except ImportError as e:
                self.node.get_logger().warn(
                    f"libbot_msgs not found or import error: {e}, running in simulation mode"
                )
                self.find_book_action_client = None

            # 创建Service客户端
            try:
                from libbot_msgs.srv import GetBookInfo

                self.get_book_info_client = self.node.create_client(
                    GetBookInfo, "/get_book_info"
                )

                # 等待Service可用
                if not self.get_book_info_client.wait_for_service(timeout_sec=1.0):
                    self.node.get_logger().warn("get_book_info service not available")
            except ImportError:
                self.node.get_logger().warn(
                    "libbot_msgs not found, running in simulation mode"
                )

            # 启动执行器线程
            self.executor = MultiThreadedExecutor()
            self.executor.add_node(self.node)

            # 使用QTimer在主线程中处理ROS2事件，避免线程安全问题
            self.ros2_timer = QTimer()
            self.ros2_timer.timeout.connect(self._process_ros2_events)
            self.ros2_timer.start(10)  # 每10ms处理一次ROS2事件

            # 启动健康检查定时器
            self._start_health_check()

            # 初始化L1恢复集成
            self._init_l1_recovery_integration()

            # 初始化L2恢复集成
            self._init_l2_recovery_integration()

            self.node.get_logger().info("Ros2Manager initialized successfully")

        except Exception as e:
            self.error_occurred.emit(
                {
                    "error_code": "ROS2_INIT_FAILED",
                    "message": f"Failed to initialize ROS2: {str(e)}",
                }
            )

    def _executor_spin(self):
        """在后台线程中运行ROS2执行器"""
        while rclpy.ok() and self.node is not None:
            self.executor.spin_once(timeout_sec=0.1)

    def _start_health_check(self):
        """启动系统健康检查"""
        self.health_check_timer = QTimer()
        self.health_check_timer.timeout.connect(self._check_system_health)
        self.health_check_timer.start(1000)  # 1秒检查一次

    def _process_ros2_events(self):
        """在主线程中处理ROS2事件"""
        if self.node is not None and rclpy.ok():
            self.executor.spin_once(timeout_sec=0.001)  # 非阻塞处理

    def _start_action_client_check(self):
        """启动Action客户端状态检查"""
        self.action_check_timer = QTimer()
        self.action_check_timer.timeout.connect(self._check_action_client_status)
        self.action_check_timer.start(2000)  # 2秒检查一次


    def _start_simulation(self, book_id, guide_patron):
        """启动模拟任务（在没有真实ROS2 Action服务器时使用）"""
        # 创建模拟任务定时器
        self.simulation_timer = QTimer()
        self.simulation_progress = 0
        self.simulation_book_id = book_id
        self.simulation_guide_patron = guide_patron

        # 立即发送初始状态
        self._send_simulation_update()

        # 设置定时器，每100ms更新一次状态（10Hz）
        self.simulation_timer.timeout.connect(self._send_simulation_update)
        self.simulation_timer.start(100)

    def _send_simulation_update(self):
        """发送模拟状态更新"""
        import time

        # 模拟进度增长
        self.simulation_progress += 2  # 每次增加2%

        if self.simulation_progress <= 100:
            # 根据进度确定状态
            if self.simulation_progress < 30:
                status = "navigating"
            elif self.simulation_progress < 70:
                status = "scanning"
            elif self.simulation_progress < 95:
                status = "approaching"
            else:
                status = "completed"

            # 模拟位置变化
            progress_ratio = self.simulation_progress / 100.0
            x = 0.0 + (5.0 * progress_ratio)  # 从0到5
            y = 0.0 + (3.0 * progress_ratio)  # 从0到3

            # 模拟图书检测
            books_detected = []
            signal_strength = 0.0
            if self.simulation_progress > 50:
                books_detected = [self.simulation_book_id]
                signal_strength = 0.5 + (0.4 * (self.simulation_progress - 50) / 50)  # 0.5到0.9

            # 计算剩余时间
            remaining = max(0, 30.0 - (30.0 * progress_ratio))

            # 发送状态更新
            status_data = {
                "status": status,
                "progress": float(self.simulation_progress),
                "distance_to_goal": 10.0 * (1.0 - progress_ratio),
                "current_pose": {"x": x, "y": y},
                "books_detected": books_detected,
                "signal_strength": signal_strength,
                "detection_direction": "front" if signal_strength > 0.7 else "",
                "estimated_remaining": remaining,
            }

            self.task_status_updated.emit(status_data)

        else:
            # 任务完成
            self.simulation_timer.stop()
            self.simulation_timer = None

            # 发送完成状态
            self.task_status_updated.emit({
                "status": "completed",
                "progress": 100.0,
                "distance_to_goal": 0.0,
                "current_pose": {"x": 5.0, "y": 3.0},
                "books_detected": [self.simulation_book_id],
                "signal_strength": 0.95,
                "detection_direction": "front",
                "estimated_remaining": 0.0,
                "result": {
                    "success": True,
                    "message": "Book found successfully",
                    "search_time": 30.0,
                    "navigation_attempts": 1,
                    "scan_attempts": 3,
                }
            })

    # ========== Action通信 ==========

    def send_find_book_goal(self, book_id, guide_patron=False):
        """发送找书任务

        Args:
            book_id: 图书ID
            guide_patron: 是否引导读者

        Returns:
            bool: 是否成功发送
        """
        try:
            # 检查是否有活跃的任务，如果有则先重置
            if self.current_goal_handle is not None:
                self.node.get_logger().warn(
                    "Found active goal handle, resetting before sending new goal"
                )
                self.current_goal_handle = None

            if self.find_book_action_client is None:
                self.node.get_logger().info(
                    f"Simulating FindBook goal sent for book: {book_id}"
                )
                # 启动模拟任务
                self._start_simulation(book_id, guide_patron)
                return True

            # 等待Action服务器可用
            if not self.find_book_action_client.wait_for_server(timeout_sec=5.0):
                self.error_occurred.emit(
                    {
                        "error_code": "ACTION_SERVER_UNAVAILABLE",
                        "message": "/find_book Action server not available",
                    }
                )
                return False

            # 创建Goal
            from libbot_msgs.action import FindBook

            goal = FindBook.Goal()
            goal.book_id = book_id
            goal.guide_patron = guide_patron

            # 发送Goal（异步）
            future = self.find_book_action_client.send_goal_async(
                goal, feedback_callback=self._find_book_feedback_callback
            )

            # 添加完成回调
            future.add_done_callback(self._goal_response_callback)

            self.node.get_logger().info(f"FindBook goal sent for book: {book_id}")

            return True

        except Exception as e:
            self.error_occurred.emit(
                {
                    "error_code": "SEND_GOAL_FAILED",
                    "message": f"Failed to send goal: {str(e)}",
                }
            )
            return False

    def _goal_response_callback(self, future):
        """Goal响应回调"""
        try:
            goal_handle = future.result()

            if not goal_handle.accepted:
                self.error_occurred.emit(
                    {
                        "error_code": "GOAL_REJECTED",
                        "message": "Goal was rejected by the action server",
                    }
                )
                # 重置goal handle
                self.current_goal_handle = None
                return

            self.current_goal_handle = goal_handle
            self.node.get_logger().info("Goal accepted")

            # 获取结果
            result_future = goal_handle.get_result_async()
            result_future.add_done_callback(self._goal_result_callback)

        except Exception as e:
            self.error_occurred.emit(
                {
                    "error_code": "GOAL_RESPONSE_ERROR",
                    "message": f"Error in goal response: {str(e)}",
                }
            )
            # 重置goal handle
            self.current_goal_handle = None

    def _find_book_feedback_callback(self, feedback):
        """FindBook反馈回调"""
        try:
            # 调试：打印收到的反馈
            fb = feedback.feedback
            self.node.get_logger().info(f"收到反馈: 状态={fb.status}, 进度={fb.progress}%")

            # 将ROS2反馈转换为dict
            feedback_dict = {
                "status": feedback.feedback.status,
                "progress": feedback.feedback.progress,
                "distance_to_goal": feedback.feedback.distance_to_goal,
                "current_pose": {
                    "x": feedback.feedback.current_pose.position.x,
                    "y": feedback.feedback.current_pose.position.y,
                },
                "books_detected": feedback.feedback.books_detected,
                "signal_strength": feedback.feedback.signal_strength,
                "detection_direction": feedback.feedback.detection_direction
                if hasattr(feedback.feedback, "detection_direction")
                else "",
                "estimated_remaining": feedback.feedback.estimated_remaining,
            }

            # 使用queued connection确保线程安全
            self.task_status_updated.emit(feedback_dict)


        except Exception as e:
            self.node.get_logger().error(f"Error in feedback callback: {str(e)}")

    def _goal_result_callback(self, future):
        """Goal结果回调"""
        try:
            result = future.result().result

            # 发送完成信号
            result_dict = {
                "success": result.success,
                "message": result.message,
                "search_time": result.search_time,
                "navigation_attempts": result.navigation_attempts,
                "scan_attempts": result.scan_attempts,
            }

            self.task_status_updated.emit(
                {"status": "completed", "result": result_dict}
            )

            self.current_goal_handle = None

        except Exception as e:
            self.error_occurred.emit(
                {
                    "error_code": "RESULT_ERROR",
                    "message": f"Error getting result: {str(e)}",
                }
            )

    def cancel_current_goal(self):
        """取消当前正在执行的Goal"""
        try:
            # 检查模拟任务
            if hasattr(self, 'simulation_timer') and self.simulation_timer is not None:
                self.simulation_timer.stop()
                self.simulation_timer = None

                self.task_status_updated.emit({
                    "status": "cancelled",
                    "message": "Goal cancelled successfully",
                    "progress": float(self.simulation_progress) if hasattr(self, 'simulation_progress') else 0.0
                })

                self.node.get_logger().info("Simulation goal cancelled")
                return True

            # 检查真实ROS2任务
            if self.current_goal_handle:
                future = self.current_goal_handle.cancel_goal_async()
                future.add_done_callback(self._cancel_done_callback)
                self.node.get_logger().info("Goal cancellation requested")
                return True
            else:
                # 检查是否有模拟任务正在运行
                if hasattr(self, 'simulation_timer') and self.simulation_timer is not None:
                    return self.cancel_current_goal()  # 递归调用处理模拟任务

                self.error_occurred.emit(
                    {
                        "error_code": "NO_ACTIVE_GOAL",
                        "message": "No active goal to cancel",
                    }
                )
                return False

        except Exception as e:
            self.error_occurred.emit(
                {
                    "error_code": "CANCEL_FAILED",
                    "message": f"Failed to cancel goal: {str(e)}",
                }
            )
            return False

    def _cancel_done_callback(self, future):
        """取消完成回调"""
        try:
            cancel_response = future.result()
            if cancel_response and hasattr(cancel_response, 'goals_canceling'):
                if cancel_response.goals_canceling:
                    self.task_status_updated.emit(
                        {"status": "cancelled", "message": "Goal cancelled successfully"}
                    )
                else:
                    self.error_occurred.emit(
                        {
                            "error_code": "CANCEL_REJECTED",
                            "message": "Goal cancellation rejected",
                        }
                    )
            else:
                # 兼容旧版本ROS2
                self.task_status_updated.emit(
                    {"status": "cancelled", "message": "Goal cancelled (legacy format)"}
                )

            # 关键：确保重置goal handle
            self.current_goal_handle = None

        except Exception as e:
            self.error_occurred.emit(
                {
                    "error_code": "CANCEL_RESULT_ERROR",
                    "message": f"Error in cancel result: {str(e)}",
                }
            )
            # 确保重置goal handle
            self.current_goal_handle = None

    # ========== Service通信 ==========

    def get_book_info(self, book_id, callback=None, timeout=5.0):
        """查询图书信息

        Args:
            book_id: 图书ID
            callback: 结果回调函数(result_dict)
            timeout: 超时时间（秒）

        Returns:
            bool: 是否成功发送请求
        """
        try:
            if self.get_book_info_client is None:
                self.node.get_logger().info(
                    f"Simulating GetBookInfo for book: {book_id}"
                )
                # 模拟响应
                result = {
                    "success": True,
                    "id": book_id,
                    "isbn": "978-3-16-148410-0",
                    "title": "Sample Book Title",
                    "author": "Sample Author",
                    "category": "Fiction",
                    "shelf_zone": "A",
                    "shelf_level": 2,
                    "shelf_position": 5,
                    "status": "available",
                    "pose": {"x": 2.5, "y": 3.1, "z": 1.2},
                }
                self.book_info_received.emit(result)
                if callback:
                    callback(result)
                return True

            # 等待Service可用
            if not self.get_book_info_client.wait_for_service(timeout_sec=timeout):
                self.error_occurred.emit(
                    {
                        "error_code": "SERVICE_UNAVAILABLE",
                        "message": "get_book_info service not available",
                    }
                )
                return False

            # 创建Request
            from libbot_msgs.srv import GetBookInfo

            request = GetBookInfo.Request()
            request.book_id = book_id

            # 异步调用Service
            future = self.get_book_info_client.call_async(request)

            # 添加回调
            future.add_done_callback(lambda f: self._book_info_callback(f, callback))

            return True

        except Exception as e:
            self.error_occurred.emit(
                {
                    "error_code": "SERVICE_CALL_FAILED",
                    "message": f"Failed to call service: {str(e)}",
                }
            )
            return False

    def _book_info_callback(self, future, user_callback):
        """图书信息响应回调"""
        try:
            response = future.result()

            if response.success:
                # 构建结果字典
                result = {
                    "success": True,
                    "id": response.id,
                    "isbn": response.isbn,
                    "title": response.title,
                    "author": response.author,
                    "category": response.category,
                    "shelf_zone": response.shelf_zone,
                    "shelf_level": response.shelf_level,
                    "shelf_position": response.shelf_position,
                    "status": response.status,
                    "pose": {
                        "x": response.pose.position.x,
                        "y": response.pose.position.y,
                        "z": response.pose.position.z,
                    },
                }

                # 发射信号
                self.book_info_received.emit(result)

            else:
                self.error_occurred.emit(
                    {"error_code": "BOOK_NOT_FOUND", "message": response.message}
                )

            # 调用用户回调
            if user_callback:
                user_callback(response)

        except Exception as e:
            self.error_occurred.emit(
                {
                    "error_code": "SERVICE_RESPONSE_ERROR",
                    "message": f"Error in service response: {str(e)}",
                }
            )

    # ========== 系统健康检查 ==========

    def _check_system_health(self):
        """检查系统健康状态"""
        try:
            # 使用模拟数据，避免复杂的订阅逻辑
            self._use_mock_health_data()
        except Exception as e:
            if self.node:
                self.node.get_logger().error(f"Error checking system health: {str(e)}")
            # 出错时也使用模拟数据
            self._use_mock_health_data()

    def _use_mock_health_data(self):
        """使用模拟健康数据"""
        health_data = {
            "navigation_health": 0.95,
            "perception_health": 0.90,
            "database_health": 0.98,
            "battery_level": 0.85,
            "robot_pose": {"x": 5.2, "y": 3.1, "z": 0.0, "yaw": 0.0},
            "active_warnings": [],
            "active_errors": [],
            "active_tasks": 0
        }

        self.system_health_updated.emit(health_data)

        # 更新机器人位置
        if "robot_pose" in health_data:
            self.robot_pose_updated.emit(health_data["robot_pose"])

    # ========== 清理 ==========

    def shutdown(self):
        """关闭Ros2Manager"""
        try:
            if self.health_check_timer:
                self.health_check_timer.stop()

            if hasattr(self, 'ros2_timer') and self.ros2_timer:
                self.ros2_timer.stop()

            # 清理L2恢复集成
            if self.l2_recovery_integration:
                self.l2_recovery_integration.cleanup()

            if self.node:
                self.node.get_logger().info("Shutting down Ros2Manager...")
                self.executor.remove_node(self.node)
                self.node.destroy_node()
                rclpy.shutdown()

        except Exception as e:
            print(f"Error during shutdown: {e}")

    def _init_l1_recovery_integration(self):
        """初始化L1恢复集成"""
        try:
            self.l1_recovery_integration = L1RecoveryIntegration(self.node)

            # 连接L1恢复信号到UI信号
            self.l1_recovery_integration.recovery_status_updated.connect(
                self._on_l1_recovery_status_update
            )
            self.l1_recovery_integration.recovery_error_occurred.connect(
                self._on_l1_recovery_error
            )
            self.l1_recovery_integration.recovery_completed.connect(
                self._on_l1_recovery_completed
            )

            self.node.get_logger().info("L1恢复集成初始化成功")

        except Exception as e:
            self.node.get_logger().error(f"L1恢复集成初始化失败: {e}")
            self.l1_recovery_integration = None

    def _init_l2_recovery_integration(self):
        """初始化L2恢复集成"""
        try:
            self.l2_recovery_integration = L2RecoveryIntegration(
                self.node, self.l1_recovery_integration
            )

            # 连接L2恢复信号到UI信号
            self.l2_recovery_integration.recovery_status_updated.connect(
                self._on_l2_recovery_status_update
            )
            self.l2_recovery_integration.recovery_error_occurred.connect(
                self._on_l2_recovery_error
            )
            self.l2_recovery_integration.recovery_completed.connect(
                self._on_l2_recovery_completed
            )
            self.l2_recovery_integration.recovery_escalated.connect(
                self._on_l2_recovery_escalated
            )

            self.node.get_logger().info("L2恢复集成初始化成功")

        except Exception as e:
            self.node.get_logger().error(f"L2恢复集成初始化失败: {e}")
            self.l2_recovery_integration = None

    def _on_l1_recovery_status_update(self, status_info):
        """处理L1恢复状态更新"""
        # 将L1恢复状态转换为任务状态更新
        recovery_status = {
            "task_id": f"l1_recovery_{status_info['type']}",
            "status": f"l1_{status_info['status']}",
            "progress": 50.0 if status_info['status'] == 'in_progress' else
                       0.0 if status_info['status'] == 'started' else 100.0,
            "recovery_type": status_info['type'],
            "recovery_status": status_info['status']
        }

        self.task_status_updated.emit(recovery_status)

    def _on_l1_recovery_error(self, error_info):
        """处理L1恢复错误"""
        # 将L1恢复错误转换为UI错误
        ui_error = {
            "error_code": f"L1_RECOVERY_{error_info['type'].upper()}",
            "message": f"L1恢复失败: {error_info['message']}",
            "recovery_type": error_info['type']
        }

        self.error_occurred.emit(ui_error)

    def _on_l1_recovery_completed(self, completion_info):
        """处理L1恢复完成"""
        # 发送恢复完成状态
        completion_status = {
            "task_id": f"l1_recovery_{completion_info['type']}",
            "status": "l1_recovery_completed",
            "success": completion_info['success'],
            "recovery_type": completion_info['type'],
            "progress": 100.0
        }

        self.task_status_updated.emit(completion_status)

        # 如果恢复成功，发送系统健康度更新
        if completion_info['success']:
            health_update = {
                "recovery_health": 1.0,
                "system_health": 0.95,
                "last_recovery": completion_info['type']
            }
            self.system_health_updated.emit(health_update)

    def _on_l2_recovery_status_update(self, status_info):
        """处理L2恢复状态更新（线程安全）"""
        # 将L2恢复状态转换为任务状态更新
        recovery_status = {
            "task_id": f"l2_recovery_{status_info['type']}",
            "status": f"l2_{status_info['status']}",
            "progress": 50.0 if status_info['status'] == 'in_progress' else
                       0.0 if status_info['status'] == 'started' else 100.0,
            "recovery_type": status_info['type'],
            "recovery_status": status_info['status'],
            "recovery_level": "L2",
            "elapsed_time": status_info.get('elapsed_time', 0.0)
        }

        # 线程安全地发射信号
        if threading.current_thread() is threading.main_thread():
            self.task_status_updated.emit(recovery_status)
        else:
            # 在非主线程中使用invokeMethod确保在主线程执行
            QMetaObject.invokeMethod(
                self,
                lambda: self.task_status_updated.emit(recovery_status),
                Qt.QueuedConnection
            )

    def _on_l2_recovery_error(self, error_info):
        """处理L2恢复错误（线程安全）"""
        # 将L2恢复错误转换为UI错误
        ui_error = {
            "error_code": f"L2_RECOVERY_{error_info['type'].upper()}",
            "message": f"L2恢复失败: {error_info['message']}",
            "recovery_type": error_info['type'],
            "recovery_level": "L2"
        }

        # 线程安全地发射信号
        if threading.current_thread() is threading.main_thread():
            self.error_occurred.emit(ui_error)
        else:
            QMetaObject.invokeMethod(
                self,
                lambda: self.error_occurred.emit(ui_error),
                Qt.QueuedConnection
            )

    def _on_l2_recovery_completed(self, completion_info):
        """处理L2恢复完成"""
        # 发送恢复完成状态
        completion_status = {
            "task_id": f"l2_recovery_{completion_info['type']}",
            "status": "l2_recovery_completed",
            "success": completion_info['success'],
            "recovery_type": completion_info['type'],
            "recovery_level": "L2",
            "progress": 100.0,
            "duration": completion_info.get('duration', 0.0)
        }

        self.task_status_updated.emit(completion_status)

        # 如果恢复成功，发送系统健康度更新
        if completion_info['success']:
            health_update = {
                "recovery_health": 1.0,
                "system_health": 0.98,  # L2恢复后系统更健康
                "last_recovery": completion_info['type'],
                "recovery_level": "L2"
            }
            self.system_health_updated.emit(health_update)

    def _on_l2_recovery_escalated(self, escalation_info):
        """处理L2恢复到L3的升级"""
        # 发送升级状态
        escalation_status = {
            "task_id": "recovery_escalation",
            "status": "escalated_to_l3",
            "from_level": "L2",
            "to_level": "L3",
            "reason": escalation_info['reason'],
            "failed_recovery": escalation_info.get('failed_recovery'),
            "error": escalation_info.get('error')
        }

        self.task_status_updated.emit(escalation_status)

        # 发送错误通知
        escalation_error = {
            "error_code": "RECOVERY_ESCALATION_L2_TO_L3",
            "message": f"L2恢复失败，已升级到L3: {escalation_info['reason']}",
            "escalation_info": escalation_info
        }

        self.error_occurred.emit(escalation_error)

    def trigger_l1_rfid_recovery(self, book_id, position):
        """触发L1 RFID恢复"""
        if self.l1_recovery_integration:
            self.l1_recovery_integration.trigger_rfid_recovery(book_id, position)
        else:
            self.error_occurred.emit({
                "error_code": "L1_INTEGRATION_ERROR",
                "message": "L1恢复集成未初始化"
            })

    def trigger_l1_localization_recovery(self):
        """触发L1定位恢复"""
        if self.l1_recovery_integration:
            self.l1_recovery_integration.trigger_localization_recovery()
        else:
            self.error_occurred.emit({
                "error_code": "L1_INTEGRATION_ERROR",
                "message": "L1恢复集成未初始化"
            })

    def trigger_l1_target_redefinition(self, original_goal):
        """触发L1目标重定义"""
        if self.l1_recovery_integration:
            self.l1_recovery_integration.trigger_target_redefinition(original_goal)
        else:
            self.error_occurred.emit({
                "error_code": "L1_INTEGRATION_ERROR",
                "message": "L1恢复集成未初始化"
            })

    # L2恢复触发方法
    def trigger_l2_costmap_recovery(self, goal_pose):
        """触发L2代价地图恢复"""
        if self.l2_recovery_integration:
            self.l2_recovery_integration.trigger_costmap_recovery(goal_pose)
        else:
            self.error_occurred.emit({
                "error_code": "L2_INTEGRATION_ERROR",
                "message": "L2恢复集成未初始化"
            })

    def trigger_l2_task_reset_recovery(self, task_info):
        """触发L2任务重置恢复"""
        if self.l2_recovery_integration:
            self.l2_recovery_integration.trigger_task_reset_recovery(task_info)
        else:
            self.error_occurred.emit({
                "error_code": "L2_INTEGRATION_ERROR",
                "message": "L2恢复集成未初始化"
            })

    def trigger_l2_component_restart_recovery(self, components=None):
        """触发L2组件重启恢复"""
        if self.l2_recovery_integration:
            self.l2_recovery_integration.trigger_component_restart_recovery(components)
        else:
            self.error_occurred.emit({
                "error_code": "L2_INTEGRATION_ERROR",
                "message": "L2恢复集成未初始化"
            })

    def trigger_l2_home_reset_recovery(self):
        """触发L2返回Home重置恢复"""
        if self.l2_recovery_integration:
            self.l2_recovery_integration.trigger_home_reset_recovery()
        else:
            self.error_occurred.emit({
                "error_code": "L2_INTEGRATION_ERROR",
                "message": "L2恢复集成未初始化"
            })

    def __del__(self):
        """析构函数"""
        self.shutdown()
