# 📅 Phase 1 详细实施计划（4周）

> 目标：MVP（最小可行产品）- 基础导航 + 单本书检索
> 时间：4周（20个工作日）
> 完成标志：能从任意位置导航到目标书架并检测到RFID标签

---

## 📊 项目概览

### 交付物清单
| 模块 | 核心功能 | 优先级 | 预计工时 |
|------|---------|--------|---------|
| libbot_description | TurtleBot3模型配置 | P0 | 8h |
| libbot_simulation | Gazebo环境搭建 | P0 | 16h |
| libbot_navigation | Nav2配置与调优 | P0 | 24h |
| libbot_perception | 四向RFID扫描仿真 | P0 | 20h |
| libbot_tasks | FindBook Action实现 | P0 | 16h |
| libbot_database | SQLite接口 | P1 | 12h |
| libbot_msgs | 自定义消息定义 | P0 | 4h |
| 集成测试 | E2E流程验证 | P0 | 8h |

**总工时：108小时**（按8小时/天 ≈ 13.5天，预留缓冲时间）

---

## 📅 第1周：基础环境搭建

### 目标
- 完成ROS2工作空间初始化
- 搭建基础Gazebo仿真环境
- 实现TurtleBot3导航基础功能

### Day 1-2：工作空间与基础配置
**负责人：** 主开发
**依赖：** 无

#### 任务 1.1：创建工作空间结构
```bash
# 创建ROS2包结构
mkdir -p ~/lib_bot_ws/src
mkdir -p ~/lib_bot_ws/library_config
mkdir -p ~/lib_bot_ws/scripts

# 初始化git仓库
cd ~/lib_bot_ws
git init

# 创建基础目录结构
cd src
ros2 pkg create libbot_description --build-type ament_python
git add . && git commit -m "Initial workspace setup"
```

**验收标准：**
- [ ] 工作空间可成功编译（colcon build）
- [ ] git仓库初始化完成
- [ ] .gitignore文件包含build/, install/, log/

#### 任务 1.2：安装依赖项
```bash
# 安装核心依赖
sudo apt update
sudo apt install -y \
  ros-humble-turtlebot3 \
  ros-humble-turtlebot3-simulations \
  ros-humble-nav2 \
  ros-humble-nav2-bringup \
  ros-humble- behaviortree-cpp \
  python3-sqlite3 \
  python3-pyqt5

# 创建依赖清单
echo "turtlebot3" >> ~/lib_bot_ws/requirements_ros.txt
echo "nav2" >> ~/lib_bot_ws/requirements_ros.txt
```

**验收标准：**
- [ ] 所有依赖安装成功（无报错）
- [ ] 可运行turtlebot3_gazebo demo

### Day 3-4：机器人模型配置
**负责人：** 主开发
**依赖：** 任务1.1, 1.2

#### 任务 1.3：libbot_description包
创建 `src/libbot_description/` 配置：

```bash
# 目录结构
libbot_description/
├── libbot_description/
│   ├── __init__.py
│   └── config/
│       └── turtlebot3_waffle_libbot.yaml  # 机器人参数
├── launch/
│   └── robot.launch.py                    # 启动机器人
├── rviz/
│   └── libbot_view.rviz                   # RViz配置
└── urdf/
    └── libbot_waffle.urdf.xacro           # 修改后的URDF
```

**关键修改点：**
1. 添加4个RFID读取器link（前、后、左、右）
2. 每个读取器添加Gazebo插件配置
3. 修改footprint为0.3m × 0.3m（狭窄过道优化）

**验收标准：**
- [ ] 可启动机器人模型：`ros2 launch libbot_description robot.launch.py`
- [ ] RViz显示4个RFID读取器位置（彩色标记）
- [ ] 四个读取器TF发布正确

### Day 5：基础导航测试
**负责人：** 主开发
**依赖：** 任务1.3

#### 任务 1.4：Nav2基础配置
创建 `src/libbot_navigation/config/`：

```yaml
# nav2_params.yaml 关键参数
amcl:
  ros__parameters:
    min_particles: 3000
    max_particles: 8000
    laser_likelihood_max_dist: 2.0

dwb_controller:
  ros__parameters:
    max_vel_x: 0.3
    min_vel_x: -0.15
    max_vel_theta: 0.5
```

**测试流程：**
1. 启动Gazebo空环境
2. 启动Nav2
3. 使用RViz设置目标点
4. 验证机器人可导航到任意位置

**验收标准：**
- [ ] 导航成功率 >90%（10次测试）
- [ ] 平均到达时间 <30秒（10米距离）
- [ ] 无碰撞发生

---

## 📅 第2周：仿真环境与RFID感知

### 目标
- 搭建图书馆Gazebo环境
- 实现四向RFID扫描仿真
- 完成基础数据库集成

### Day 6-7：图书馆环境建模
**负责人：** 主开发
**依赖：** 第1周完成

#### 任务 2.1：libbot_simulation包
创建图书馆世界文件：

```bash
libbot_simulation/
├── launch/
│   └── library.launch.py          # 主启动文件
├── worlds/
│   ├── library_basic.sdf          # 基础环境（4排×6书架）
│   └── library_basic_24.sdf       # 24个书架完整版
├── models/
│   └── bookshelf/
│       ├── model.config
│       └── model.sdf              # 参数化书架
└── scripts/
    └── generate_library_world.py  # 世界生成器
```

**环境规格：**
- 房间尺寸：15m × 12m
- 书架：4排 × 6个 = 24个
- 过道宽度：1.2m
- 阅览区：2个（4m × 3m）

**验收标准：**
- [ ] Gazebo可加载library_basic.world
- [ ] 24个书架正确摆放
- [ ] 机器人可在过道中自由移动
- [ ] 地图可通过SLAM工具生成

### Day 8-9：四向RFID仿真实现
**负责人：** 主开发
**依赖：** 任务2.1

#### 任务 2.2：libbot_perception包
```bash
libbot_perception/
├── libbot_perception/
│   ├── __init__.py
│   └── rfid_simulator.py          # RFID仿真核心
├── launch/
│   └── rfid.launch.py
└── scripts/
    └── test_rfid.py               # 测试脚本
```

**实现四向扫描器：**
```python
# rfid_simulator.py 核心逻辑
class RFIDSimulator(Node):
    def __init__(self):
        # 四个发布者
        self.pub_front = self.create_publisher(RFIDScan, '/rfid/scan/front', 10)
        self.pub_back = self.create_publisher(RFIDScan, '/rfid/scan/back', 10)
        self.pub_left = self.create_publisher(RFIDScan, '/rfid/scan/left', 10)
        self.pub_right = self.create_publisher(RFIDScan, '/rfid/scan/right', 10)

        # 定时扫描
        self.create_timer(0.1, self.scan_callback)  # 10Hz

    def scan_callback(self):
        # 检测范围内的图书
        # 计算距离和方向
        # 发布到对应Topic
```

**关键参数（可配置）：**
```yaml
# rfid_params.yaml
detection_range: 0.5        # 检测范围
false_negative_rate: 0.15  # 漏检率
tag_power_threshold: -60  # 信号强度阈值
```

**测试场景：**
```bash
# 测试1：静态检测
ros2 launch libbot_simulation library.launch.py
ros2 launch libbot_perception rfid.launch.py
ros2 topic echo /rfid/scan/front

# 测试2：移动检测
ros2 run libbot_perception test_rfid.py  # 机器人移动并记录检测结果
```

**验收标准：**
- [ ] 四个Topic正常发布（10Hz）
- [ ] 检测范围准确（0.5m ± 0.05m）
- [ ] 方向区分正确（前/后/左/右）
- [ ] 漏检率可配置（0-30%）

### Day 10：数据库集成与测试数据
**负责人：** 主开发
**依赖：** 任务2.2

#### 任务 2.3：libbot_database包
```bash
libbot_database/
├── libbot_database/
│   ├── __init__.py
│   └── db_manager.py          # SQLite接口
├── launch/
│   └── db.launch.py
└── config/
    └── test_books_50.csv      # 50本测试数据
```

**数据库创建脚本：**
```python
# create_test_data.py
import sqlite3
import csv

def create_database():
    conn = sqlite3.connect('library.db')
    # 创建books表
    # 创建inventory_log表
    # 创建task_queue表

def import_books_from_csv(csv_file):
    # 从CSV导入50本书
    # 自动生成位置信息
```

**验收标准：**
- [ ] SQLite数据库创建成功
- [ ] 包含50本测试图书数据
- [ ] 图书均匀分布在24个书架上（每个书架2-3本）
- [ ] 验证SQL查询性能（<100ms）

---

## 📅 第3周：任务管理与集成

### 目标
- 实现FindBook Action
- 集成四向扫描与导航
- 完成端到端基本流程

### Day 11-12：自定义消息与Action定义
**负责人：** 主开发
**依赖：** 第2周完成

#### 任务 3.1：libbot_msgs包
```bash
libbot_msgs/
├── action/
│   ├── FindBook.action
│   └── PerformInventory.action
├── msg/
│   ├── RFIDScan.msg
│   └── BookLocation.msg
└── srv/
    ├── GetBookInfo.srv
    └── UpdateBookLocation.srv
```

**消息定义示例：**
```bash
# FindBook.action
string book_id
bool guide_patron
---
bool success
geometry_msgs/Pose book_pose
float32 search_time
---
string status
float32 progress
float32 distance_to_book
```

```bash
# RFIDScan.msg
std_msgs/Header header
RFIDTag[] detected_tags
```

**验收标准：**
- [ ] 所有消息编译成功（无warning）
- [ ] 使用ros2 interface show可查看消息结构
- [ ] 包含完整的action定义（goal/result/feedback）

### Day 13-14：FindBook Action服务器
**负责人：** 主开发
**依赖：** 任务3.1

#### 任务 3.2：libbot_tasks包 - FindBook实现
```bash
libbot_tasks/
├── libbot_tasks/
│   ├── __init__.py
│   ├── find_book_action.py      # Action服务器
│   └── book_search_fsm.py       # 状态机
├── launch/
│   └── tasks.launch.py
└── behaviors/
    └── scan_for_book.xml        # BT配置
```

**状态机设计（简化）：**
```python
# 伪代码
class FindBookActionServer:
    def execute_callback(self, goal_handle):
        # 1. 查询数据库获取书籍位置
        book_info = self.db.get_book_info(goal_handle.book_id)

        # 2. 导航到目标书架区域
        nav_result = self.navigator.go_to_pose(book_info.shelf_pose)

        # 3. 执行扫描
        scan_result = self.scan_for_book(goal_handle.book_id)

        # 4. 返回结果
        if scan_result.found:
            return SUCCESS
        else:
            return FAILURE
```

**验收标准：**
- [ ] Action服务器可正常启动
- [ ] 可通过命令行测试：`ros2 action send_goal /find_book libbot_msgs/action/FindBook {...}`
- [ ] 支持取消操作
- [ ] 返回详细反馈（progress, distance）

### Day 15：集成测试与调试
**负责人：** 主开发
**依赖：** 任务3.2

#### 任务 3.3：端到端集成测试
**测试场景：**
1. 启动完整系统
   ```bash
   ros2 launch libbot_simulation library.launch.py
   ros2 launch libbot_tasks tasks.launch.py
   ```

2. 执行找书任务
   ```bash
   ros2 action send_goal /find_book libbot_msgs/action/FindBook \
     '{book_id: "978-3-16-1000001"}'
   ```

3. 观察行为：
   - 机器人是否成功导航？
   - RFID是否检测到？
   - Action是否正确返回结果？

**问题排查清单：**
- [ ] TF树完整（无断开）
- [ ] 所有Topic正常发布
- [ ] 导航目标可达（无规划失败）
- [ ] RFID检测范围准确
- [ ] 数据库查询响应正常

**验收标准：**
- [ ] 端到端测试成功率 >80%（5次测试）
- [ ] 平均找书时间 <60秒
- [ ] 日志无critical错误
- [ ] 生成测试报告

---

## 📅 第4周：优化与验收

### 目标
- 性能优化
- 文档完善
- Phase 1验收测试

### Day 16-17：性能优化
**负责人：** 主开发
**依赖：** 第3周完成

#### 任务 4.1：启动时间优化
**现状分析：**
```bash
# 测量当前启动时间
(time ros2 launch libbot_simulation library.launch.py) &> startup_time.log
```

**优化措施：**
1. **减少TF广播频率**
   ```yaml
   # 静态TF改为1Hz发布
   tf_publish_rate: 1.0
   ```

2. **优化Gazebo物理参数**
   ```xml
   <!-- 减少实时因子检查频率 -->
   <physics type="ode">
     <real_time_update_rate>1000</real_time_update_rate>
     <max_step_size>0.001</max_step_size>
   </physics>
   ```

3. **RFID扫描延迟启动**
   ```python
   # 等待机器人完全启动后再开始扫描
   time.sleep(5.0)
   ```

**目标：** 启动时间 <15秒

#### 任务 4.2：导航参数调优
**调优清单：**
- [ ] 测试不同速度组合（0.2/0.3/0.4 m/s）
- [ ] 调整代价地图膨胀参数
- [ ] 优化恢复行为触发条件
- [ ] 测试狭窄过道通过性

**测试矩阵：**
| 参数 | 测试值 | 结果记录 |
|------|--------|---------|
| max_vel_x | 0.2, 0.3 | 记录成功率、时间 |
| inflation_radius | 0.4, 0.5, 0.6 | 记录安全距离 |
| min_particles | 3000, 5000 | 记录定位精度 |

**验收标准：**
- [ ] 最佳参数组合确定
- [ ] 导航成功率 >95%
- [ ] 狭窄过道通过率 100%

### Day 18-19：文档与测试数据
**负责人：** 主开发 + 测试
**依赖：** 任务4.2

#### 任务 4.3：生成完整测试数据集
```bash
# 执行脚本生成数据
python3 scripts/generate_test_data.py --num-books 50 --output library_config/books_50.csv
```

**数据验证：**
- [ ] 每本图书有唯一ID
- [ ] 图书均匀分布（检查每个书架2-3本）
- [ ] 所有RFID tag_id唯一
- [ ] 数据导入数据库成功

#### 任务 4.4：文档完善
更新以下文档：
- [ ] README.md（启动说明）
- [ ] design_brainstorm_detailed.md（更新Phase 1状态）
- [ ] API文档（生成rosdoc2）
- [ ] 调优指南（记录最佳参数）

### Day 20：Phase 1 验收测试
**负责人：** 主开发 + 验收方
**依赖：** 任务4.4

#### 任务 4.5：正式验收测试
**测试场景库：**
```bash
# 场景1：近处找书（3米内）
ros2 launch libbot_simulation library.launch.py initial_pose:="{x: 5.0, y: 5.0}"
ros2 action send_goal /find_book ... book_id: "book_nearby"

# 场景2：远处找书（>10米）
ros2 launch libbot_simulation library.launch.py initial_pose:="{x: 1.0, y: 1.0}"
ros2 action send_goal /find_book ... book_id: "book_far_away"

# 场景3：不同书架区域
for book_id in books_A1 + books_B3 + books_D6:
    ros2 action send_goal /find_book ...
```

**验收标准（必须全部通过）：**
| 测试项 | 目标 | 实际 | 状态 |
|--------|------|------|------|
| 导航成功率 | ≥95% | | |
| 平均找书时间 | ≤60秒 | | |
| RFID检测准确率 | ≥85% | | |
| 系统稳定性 | 连续运行1小时无崩溃 | | |
| 启动时间 | ≤15秒 | | |

**签署标准：**
- [ ] 所有验收测试通过
- [ ] 文档完整
- [ ] 代码提交到git
- [ ] 生成Phase 1交付报告

---

## 📋 风险与应对策略

### 高风险
| 风险项 | 概率 | 影响 | 应对措施 |
|--------|------|------|---------|
| Nav2在重复环境中定位失败 | 中 | 高 | 增加AMCL粒子数，备用恢复行为 |
| Gazebo性能不达标（<30 FPS） | 低 | 高 | 减少模型复杂度，禁用图书碰撞 |
| RFID仿真精度不足 | 中 | 中 | 增加调参时间，预留2天优化 |

### 中低风险
| 风险项 | 概率 | 影响 | 应对措施 |
|--------|------|------|---------|
| SQLite并发性能问题 | 低 | 中 | 使用连接池，异步查询 |
| Action通信延迟过高 | 低 | 中 | 优化回调函数，减少阻塞 |

---

## 📦 交付物清单

### 代码交付物
```
src/
├── libbot_description/      # 机器人模型 ✓
├── libbot_simulation/       # 仿真环境 ✓
├── libbot_navigation/       # 导航配置 ✓
├── libbot_perception/       # RFID感知 ✓
├── libbot_database/         # 数据库接口 ✓
├── libbot_msgs/             # 消息定义 ✓
└── libbot_tasks/            # 任务管理 ✓
```

### 文档交付物
- [ ] README.md（启动指南）
- [ ] API文档（自动生成）
- [ ] 调优指南
- [ ] Phase 1验收报告

### 测试交付物
- [ ] test_results_phase1.md
- [ ] 性能测试数据
- [ ] 代码覆盖率报告（目标≥80%）

### 数据交付物
- [ ] library_config/books_50.csv（50本测试数据）
- [ ] library_config/library.db（SQLite数据库）
- [ ] library_config/bookshelf_templates.yaml

---

## 🔄 与Phase 2的衔接

### Phase 1完成后的状态
```
当前状态：
✅ 可导航到指定书架
✅ 可检测RFID标签
✅ 单本书检索流程完成

Phase 2待实现：
⏳ 人机交互界面（屏幕显示）
⏳ 完整库存盘点功能
⏳ 任务队列管理（多本书）
⏳ 位置指示系统（Visual Marker）
```

### 技术债务
| 项 | 说明 | 计划解决时间 |
|---|------|----------|
| 硬编码参数 | 书架位置在代码中写死 | Phase 2第1周 |
| 无错误恢复 | 导航失败直接返回错误 | Phase 2第2周 |
| 单线程数据库 | 所有操作为同步 | Phase 2第3周 |

---

## 📝 附录

### 每日站会议题
每天15分钟，讨论：
1. 昨天完成了什么？
2. 今天计划做什么？
3. 有什么障碍？

### 周评审会议
每周五下午，讨论：
1. 本周完成度（按计划/延期）
2. 下周计划调整
3. 风险更新

### 关键决策记录
| 日期 | 决策 | 理由 | 影响 |
|------|------|------|------|
| 待定 | RFID检测范围0.5m | 平衡精度与覆盖 | 确定书架间距 |
| 待定 | 四向扫描而非360° | 简化实现，方向明确 | 代码复杂度降低 |

---

**文档维护：** 本文档应在每周评审后更新进度
**最后更新：** 2026-4-7
**下次评审：** 2026-4-14（第1周结束）
