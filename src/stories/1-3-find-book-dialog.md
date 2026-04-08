# Story 1-3: 找书对话框和按钮实现

> **Epic**: #1 人机交互细节
> **Priority**: P0 (Critical)
> **Points**: 3
> **Status**: backlog
> **Platform**: ROS2 / Python / Qt5
> **Dependencies**: Story 1-2 (Ros2Manager通信封装)

---

## 📋 用户故事 (User Story)

作为图书馆机器人操作员，
我希望能够通过UI发起找书任务，
这样我可以输入图书信息并跟踪找书进度。

---

## 🎯 验收标准 (Acceptance Criteria)

### 功能性要求
- [ ] "找书"按钮绑定Ros2Manager.send_find_book_goal()
- [ ] 按下Ctrl+N快捷键弹出找书对话框
- [ ] 对话框包含图书ID输入框
- [ ] 对话框包含"引导读者"复选框
- [ ] 点击"确定"发送Action Goal
- [ ] 点击"取消"关闭对话框
- [ ] 显示找书任务状态（准备中、导航中、扫描中、完成）
- [ ] 显示找书进度百分比（0-100%）
- [ ] 显示剩余时间估计
- [ ] 错误提示（无法连接服务、超时等）

### 界面要求
- [ ] 对话框居中显示，模态窗口
- [ ] 输入框获得焦点，支持回车确认
- [ ] 图书ID输入框支持历史记录（最近5本）
- [ ] 状态变化时右侧面板实时更新
- [ ] 任务卡片显示当前活动任务信息

### 性能要求
- [ ] 对话框打开时间 < 200ms
- [ ] UI响应Action反馈延迟 < 100ms
- [ ] 错误提示显示延迟 < 50ms

---

## 🔧 实现细节

### 文件清单
```
src/libbot_ui/libbot_ui/
├── find_book_dialog.py        # 新建 - 找书对话框
├── left_panel.py              # 修改 - 连接"找书"按钮信号
├── right_panel.py             # 修改 - 显示任务状态
└── main_window.py             # 修改 - 添加快捷键处理
```

### FindBookDialog类设计

```python
# find_book_dialog.py

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QCheckBox, QPushButton, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence


class FindBookDialog(QDialog):
    """找书对话框 - 输入图书信息并发起找书任务"""

    # 信号：用户确认找书
    find_book_confirmed = pyqtSignal(str, bool)  # (book_id, guide_patron)

    def __init__(self, parent=None, ros2_manager=None):
        """初始化找书对话框

        Args:
            parent: 父窗口
            ros2_manager: Ros2Manager实例（用于历史记录）
        """
        super().__init__(parent)
        self.ros2_manager = ros2_manager
        self.setup_ui()
        self.load_history()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("查找图书")
        self.setModal(True)
        self.resize(400, 200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 图书ID输入
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("图书ID:"))

        # 支持输入和历史记录下拉
        self.book_id_combo = QComboBox()
        self.book_id_combo.setEditable(True)
        self.book_id_combo.setMinimumWidth(250)
        self.book_id_combo.setPlaceholderText("输入或选择图书ID...")
        id_layout.addWidget(self.book_id_combo)

        layout.addLayout(id_layout)

        # 引导读者选项
        self.guide_patron_check = QCheckBox("引导读者前往图书位置")
        self.guide_patron_check.setChecked(False)
        layout.addWidget(self.guide_patron_check)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_button = QPushButton("确定")
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.on_ok_clicked)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        # 设置快捷键
        self.ok_button.setShortcut(QKeySequence(Qt.Key_Return))
        self.cancel_button.setShortcut(QKeySequence(Qt.Key_Escape))

    def load_history(self):
        """加载历史记录"""
        # TODO: 从SQLite数据库加载最近5本查找的图书
        # 临时使用示例数据
        sample_books = [
            "9787115426273",
            "9787115426274",
            "9787115426275"
        ]
        self.book_id_combo.addItems(sample_books)

    def on_ok_clicked(self):
        """确定按钮点击处理"""
        book_id = self.book_id_combo.currentText().strip()

        if not book_id:
            # TODO: 显示错误提示
            return

        guide_patron = self.guide_patron_check.isChecked()

        # 发射信号
        self.find_book_confirmed.emit(book_id, guide_patron)

        # 保存到历史记录
        self.save_to_history(book_id)

        self.accept()

    def save_to_history(self, book_id):
        """保存到历史记录"""
        # TODO: 保存到SQLite数据库
        # 更新combobox
        index = self.book_id_combo.findText(book_id)
        if index >= 0:
            self.book_id_combo.removeItem(index)
        self.book_id_combo.insertItem(0, book_id)
        self.book_id_combo.setCurrentIndex(0)

        # 限制历史记录数量
        while self.book_id_combo.count() > 5:
            self.book_id_combo.removeItem(self.book_id_combo.count() - 1)

    def showEvent(self, event):
        """显示事件"""
        super().showEvent(event)
        # 聚焦到输入框
        self.book_id_combo.setFocus()
        self.book_id_combo.lineEdit().selectAll()

```

### LeftPanel修改

在 `left_panel.py` 中连接"找书"按钮：

```python
# left_panel.py 修改

class LeftPanel(QWidget):
    # ... 现有代码 ...

    def connect_signals(self):
        """连接按钮信号"""
        # 找书按钮点击信号
        # 将由MainWindow连接实际处理逻辑
        pass

    def get_find_book_button(self):
        """获取找书按钮（供MainWindow连接）"""
        return self.find_book_btn
```

### MainWindow修改

在 `main_window.py` 中添加对话框和信号处理：

```python
# main_window.py 修改

from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtCore import Qt
from .left_panel import LeftPanel
from .right_panel import RightPanel
from .find_book_dialog import FindBookDialog
from .ros2_manager import Ros2Manager


class MainWindow(QMainWindow):
    """主窗口类 - 800x600控制面板"""

    def __init__(self):
        super().__init__()
        # ... 现有初始化代码 ...

        # 初始化Ros2Manager
        self.ros2_manager = Ros2Manager()

        # 初始化找书对话框
        self.find_book_dialog = FindBookDialog(self, self.ros2_manager)

        # 连接信号
        self.setup_connections()

    def setup_connections(self):
        """设置信号连接"""
        # 连接找书按钮
        self.left_panel.get_find_book_button().clicked.connect(
            self.show_find_book_dialog
        )

        # 连接快捷键
        shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        shortcut.activated.connect(self.show_find_book_dialog)

        # 连接对话框确认信号
        self.find_book_dialog.find_book_confirmed.connect(
            self.on_find_book_confirmed
        )

        # 连接Ros2Manager信号到右侧面板
        self.ros2_manager.task_status_updated.connect(
            self.right_panel.update_task_status
        )
        self.ros2_manager.error_occurred.connect(
            self.right_panel.show_error
        )
        self.ros2_manager.system_health_updated.connect(
            self.right_panel.update_health_status
        )

    def show_find_book_dialog(self):
        """显示找书对话框"""
        self.find_book_dialog.show()

    def on_find_book_confirmed(self, book_id, guide_patron):
        """找书确认处理"""
        # 发送找书任务
        success = self.ros2_manager.send_find_book_goal(
            book_id,
            guide_patron
        )

        if success:
            # 在日志面板显示任务已发送
            self.right_panel.add_log_message(
                f"找书任务已发送: {book_id}",
                "info"
            )
        else:
            # 显示错误
            self.right_panel.add_log_message(
                f"找书任务发送失败: {book_id}",
                "error"
            )

```

### RightPanel修改

在 `right_panel.py` 中添加任务状态显示：

```python
# right_panel.py 修改

class RightPanel(QWidget):
    """右侧面板 - 600px宽，包含任务卡片、统计和日志"""

    # ... 现有代码 ...

    def update_task_status(self, status_dict):
        """更新任务状态

        Args:
            status_dict: 状态字典，格式取决于Ros2Manager的信号
        """
        try:
            # 提取状态信息
            status = status_dict.get("status", "unknown")
            progress = status_dict.get("progress", 0)

            # 更新任务卡片
            self.task_card.update_status(status, progress)

            # 更新状态文本
            status_text = self._get_status_text(status)
            self.status_label.setText(f"状态: {status_text}")

            # 更新进度条
            self.progress_bar.setValue(int(progress))

        except Exception as e:
            print(f"Error updating task status: {e}")

    def _get_status_text(self, status):
        """获取状态文本"""
        status_map = {
            "idle": "待机",
            "navigating": "导航中",
            "scanning": "扫描中",
            "approaching": "接近目标",
            "completed": "完成",
            "cancelled": "已取消",
            "failed": "失败"
        }
        return status_map.get(status, status)

    def show_error(self, error_dict):
        """显示错误

        Args:
            error_dict: 错误字典 {"error_code": "...", "message": "..."}
        """
        error_code = error_dict.get("error_code", "UNKNOWN")
        message = error_dict.get("message", "Unknown error")

        # 添加到日志
        self.add_log_message(f"错误 [{error_code}]: {message}", "error")

    def update_health_status(self, health_dict):
        """更新健康状态"""
        # TODO: 更新健康指标显示
        pass

```

---

## ✅ 完成检查清单

- [ ] FindBookDialog类实现并测试
- [ ] LeftPanel的"找书"按钮连接正确
- [ ] Ctrl+N快捷键工作正常
- [ ] MainWindow集成ros2_manager和对话框
- [ ] RightPanel显示任务状态和进度
- [ ] 错误提示显示正确
- [ ] 日志面板显示找书任务相关信息
- [ ] 所有异步操作不阻塞UI
- [ ] 代码通过Black格式化检查
- [ ] 手动测试找书流程（可发送测试Action Goal）

---

## 🔍 测试场景

### 测试1: 正常找书流程
1. 点击"找书"按钮或Ctrl+N
2. 输入图书ID: "9787115426273"
3. 勾选"引导读者"
4. 点击确定
5. 验证:
   - Ros2Manager.send_find_book_goal()被调用
   - 日志面板显示"找书任务已发送"
   - 右侧面板显示状态"导航中"和进度0%

### 测试2: 错误处理
1. 点击"找书"按钮
2. 不输入任何内容直接点击确定
3. 验证: 显示"请输入图书ID"错误提示

### 测试3: 快捷键
1. 在主窗口任意位置
2. 按下Ctrl+N
3. 验证: 找书对话框弹出

### 测试4: 历史记录
1. 第一次查找: ISBN "9787115426273"
2. 第二次查找: ISBN "9787115426274"
3. 第三次点击"找书"按钮
4. 验证:
   - 下拉框显示最近5条记录
   - 最近的显示在最上面

### 测试5: 取消任务
1. 开始找书任务
2. 点击"暂停"或"取消"按钮
3. 验证:
   - Ros2Manager.cancel_current_goal()被调用
   - 日志面板显示"任务已取消"
   - 状态更新为"已取消"

---

## 📚 相关文档

- [Story 1-1: UI主窗口实现](./1-1-ui-main-window.md) - UI基础结构
- [Story 1-2: Ros2Manager通信封装](./1-2-ros2-manager.md) - ROS2通信层
- [libbot_msgs/FindBook.action](../libbot_msgs/action/FindBook.action) - Action定义
- [libbot_msgs/GetBookInfo.srv](../libbot_msgs/srv/GetBookInfo.srv) - Service定义

---

## 💡 实现提示

1. **信号与槽**: 所有ROS2回调通过pyqtSignal发送到主线程，避免UI阻塞
2. **错误处理**: 使用error_occurred信号统一处理错误，显示在日志面板
3. **状态管理**: 当前活动任务保存在Ros2Manager.current_goal_handle
4. **测试**: 可使用`ros2 action send_goal`命令测试Action服务器
5. **历史记录**: 预留SQLite接口，Story 7-1实现数据库后可完善

---

