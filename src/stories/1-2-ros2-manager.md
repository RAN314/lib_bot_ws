# Story 1-2: Ros2Manager通信封装实现

> **Epic**: #1 人机交互细节
> **Priority**: P0 (Critical)
> **Points**: 5
> **Status**: backlog
> **Platform**: ROS2 / Python / Qt5
> **Dependencies**: Story 1-1 (UI主窗口)

---

## 📋 用户故事 (User Story)

作为图书馆机器人系统的操作员，
我希望UI能够与ROS2机器人节点通信，
这样我可以从UI发送命令（找书、盘点等）并接收实时反馈。

---

## 🎯 验收标准 (Acceptance Criteria)

### 功能性要求
- [ ] 可连接ROS2节点（建立rclpy节点）
- [ ] 可发送FindBook Action Goal
- [ ] 可接收Action实时反馈（progress, status）
- [ ] 可调用GetBookInfo Service
- [ ] 可订阅/system/health Topic获取系统状态
- [ ] 可取消正在执行的Action
- [ ] 支持异步操作（不阻塞UI线程）
- [ ] 错误处理（网络断开、节点不可达）

### 性能要求
- [ ] Service调用响应时间 < 500ms
- [ ] Action Goal发送延迟 < 200ms
- [ ] 反馈更新频率 10Hz（不卡顿）
- [ ] 线程安全：ROS2回调不阻塞UI

### 代码质量
- [ ] 所有异步操作使用Signal/Slot
- [ ] 错误码定义清晰
- [ ] 日志记录完整（发送、接收、错误）
- [ ] 支持重试机制（最多3次）

---

## 🔧 实现细节

### 文件清单
```
src/libbot_ui/libbot_ui/
├── ros2_manager.py          # 新建 - ROS2通信管理器
└── main_window.py           # 修改 - 集成Ros2Manager
```

### Ros2Manager类设计

```python
# ros2_manager.py

from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtCore import QThread
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.executors import MultiThreadedExecutor
import threading

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

    # ========== 初始化 ==========

    def __init__(self, node_name='libbot_ui_manager'):
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

        # 定时器
        self.health_check_timer = None

        # 初始化ROS2
        self._init_ros2()

    def _init_ros2(self):
        """初始化ROS2环境"""
        try:
            # 检查rclpy是否已初始化
            if not rclpy.ok():
                rclpy.init()

            # 创建节点
            self.node = Node(self.node_name)

            # 创建Action客户端
            from libbot_msgs.action import FindBook
            self.find_book_action_client = ActionClient(
                self.node,
                FindBook,
                '/find_book'
            )

            # 创建Service客户端
            from libbot_msgs.srv import GetBookInfo
            self.get_book_info_client = self.node.create_client(
                GetBookInfo,
                '/get_book_info'
            )

            # 等待Service可用
            if not self.get_book_info_client.wait_for_service(timeout_sec=5.0):
                self.node.get_logger().warn(
                    'get_book_info service not available'
                )

            # 启动执行器线程
            self.executor = MultiThreadedExecutor()
            self.executor.add_node(self.node)

            self.executor_thread = threading.Thread(
                target=self._executor_spin,
                daemon=True
            )
            self.executor_thread.start()

            # 启动健康检查定时器
            self._start_health_check()

            self.node.get_logger().info("Ros2Manager initialized successfully")

        except Exception as e:
            self.error_occurred.emit({
                "error_code": "ROS2_INIT_FAILED",
                "message": f"Failed to initialize ROS2: {str(e)}"
            })

    def _executor_spin(self):
        """在后台线程中运行ROS2执行器"""
        while rclpy.ok():
            self.executor.spin_once(timeout_sec=0.1)

    def _start_health_check(self):
        """启动系统健康检查"""
        self.health_check_timer = QTimer()
        self.health_check_timer.timeout.connect(self._check_system_health)
        self.health_check_timer.start(1000)  # 1秒检查一次

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
            # 等待Action服务器可用
            if not self.find_book_action_client.wait_for_server(timeout_sec=5.0):
                self.error_occurred.emit({
                    "error_code": "ACTION_SERVER_UNAVAILABLE",
                    "message": "/find_book Action server not available"
                })
                return False

            # 创建Goal
            from libbot_msgs.action import FindBook
            goal = FindBook.Goal()
            goal.book_id = book_id
            goal.guide_patron = guide_patron

            # 发送Goal（异步）
            future = self.find_book_action_client.send_goal_async(
                goal,
                feedback_callback=self._find_book_feedback_callback
            )

            # 添加完成回调
            future.add_done_callback(self._goal_response_callback)

            self.node.get_logger().info(
                f"FindBook goal sent for book: {book_id}"
            )

            return True

        except Exception as e:
            self.error_occurred.emit({
                "error_code": "SEND_GOAL_FAILED",
                "message": f"Failed to send goal: {str(e)}"
            })
            return False

    def _goal_response_callback(self, future):
        """Goal响应回调"""
        try:
            goal_handle = future.result()

            if not goal_handle.accepted:
                self.error_occurred.emit({
                    "error_code": "GOAL_REJECTED",
                    "message": "Goal was rejected by the action server"
                })
                return

            self.current_goal_handle = goal_handle
            self.node.get_logger().info("Goal accepted")

            # 获取结果
            result_future = goal_handle.get_result_async()
            result_future.add_done_callback(self._goal_result_callback)

        except Exception as e:
            self.error_occurred.emit({
                "error_code": "GOAL_RESPONSE_ERROR",
                "message": f"Error in goal response: {str(e)}"
            })

    def _find_book_feedback_callback(self, feedback):
        """FindBook反馈回调"""
        try:
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
                "detection_direction": feedback.feedback.detection_direction if feedback.feedback.detection_direction else "",
                "estimated_remaining": feedback.feedback.estimated_remaining
            }

            # 发射信号（线程安全）
            self.task_status_updated.emit(feedback_dict)

        except Exception as e:
            self.node.get_logger().error(
                f"Error in feedback callback: {str(e)}"
            )

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
                "scan_attempts": result.scan_attempts
            }

            self.task_status_updated.emit({
                "status": "completed",
                "result": result_dict
            })

            self.current_goal_handle = None

        except Exception as e:
            self.error_occurred.emit({
                "error_code": "RESULT_ERROR",
                "message": f"Error getting result: {str(e)}"
            })

    def cancel_current_goal(self):
        """取消当前正在执行的Goal"""
        try:
            if self.current_goal_handle:
                future = self.current_goal_handle.cancel_goal_async()
                future.add_done_callback(self._cancel_done_callback)
                self.node.get_logger().info("Goal cancellation requested")
                return True
            else:
                self.error_occurred.emit({
                    "error_code": "NO_ACTIVE_GOAL",
                    "message": "No active goal to cancel"
                })
                return False

        except Exception as e:
            self.error_occurred.emit({
                "error_code": "CANCEL_FAILED",
                "message": f"Failed to cancel goal: {str(e)}"
            })
            return False

    def _cancel_done_callback(self, future):
        """取消完成回调"""
        try:
            cancel_response = future.result()
            if cancel_response:
                self.task_status_updated.emit({
                    "status": "cancelled",
                    "message": "Goal cancelled successfully"
                })
            else:
                self.error_occurred.emit({
                    "error_code": "CANCEL_REJECTED",
                    "message": "Goal cancellation rejected"
                })

            self.current_goal_handle = None

        except Exception as e:
            self.error_occurred.emit({
                "error_code": "CANCEL_RESULT_ERROR",
                "message": f"Error in cancel result: {str(e)}"
            })

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
            from libbot_msgs.srv import GetBookInfo

            # 等待Service可用
            if not self.get_book_info_client.wait_for_service(timeout_sec=timeout):
                self.error_occurred.emit({
                    "error_code": "SERVICE_UNAVAILABLE",
                    "message": "get_book_info service not available"
                })
                return False

            # 创建Request
            request = GetBookInfo.Request()
            request.book_id = book_id

            # 异步调用Service
            future = self.get_book_info_client.call_async(request)

            # 添加回调
            future.add_done_callback(
                lambda f: self._book_info_callback(f, callback)
            )

            return True

        except Exception as e:
            self.error_occurred.emit({
                "error_code": "SERVICE_CALL_FAILED",
                "message": f"Failed to call service: {str(e)}"
            })
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
                    }
                }

                # 发射信号
                self.book_info_received.emit(result)

            else:
                self.error_occurred.emit({
                    "error_code": "BOOK_NOT_FOUND",
                    "message": response.message
                })

            # 调用用户回调
            if user_callback:
                user_callback(response)

        except Exception as e:
            self.error_occurred.emit({
                "error_code": "SERVICE_RESPONSE_ERROR",
                "message": f"Error in service response: {str(e)}"
            })

    # ========== 系统健康检查 ==========

    def _check_system_health(self):
        """检查系统健康状态"""
        try:
            # TODO: 订阅/system/health topic
            # 现在使用模拟数据
            health_data = {
                "navigation_health": 0.95,
                "perception_health": 0.90,
                "database_health": 0.98,
                "robot_pose": {"x": 5.2, "y": 3.1, "yaw": 0.0},
                "active_warnings": [],
                "active_errors": []
            }

            self.system_health_updated.emit(health_data)

            # 更新机器人位置
            if "robot_pose" in health_data:
                self.robot_pose_updated.emit(health_data["robot_pose"])

        except Exception as e:
            self.node.get_logger().error(
                f"Error checking system health: {str(e)}"
            )

    # ========== 清理 ==========

    def shutdown(self):
        """关闭Ros2Manager"""
        try:
            if self.health_check_timer:
                self.health_check_timer.stop()

            if self.node:
                self.node.get_logger().info("Shutting down Ros2Manager...")
                # TODO: 清理资源

        except Exception as e:
            print(f"Error during shutdown: {e}")

    def __del__(self):
        """析构函数"""
        self.shutdown()
