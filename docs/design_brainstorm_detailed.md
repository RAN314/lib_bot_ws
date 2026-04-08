# 📚 图书馆机器人ROS2仿真 - 详细设计文档

> 生成日期：2026-4-7
> 项目阶段：头脑风暴完成，进入设计阶段
> 文档状态：已完成初稿

---

## 📋 目录
1. [项目概述](#项目概述)
2. [已确认的技术决策](#已确认的技术决策)
3. [系统架构](#系统架构)
4. [详细设计方案](#详细设计方案)
5. [待解决问题清单](#待解决问题清单)
6. [演进路线](#演进路线)

---

## 项目概述

### 项目目标
构建一个图书馆机器人的ROS2仿真工作空间，实现以下核心功能：
- ✅ 自主导航与避障
- ✅ 图书检索并映射到地图位置
- ✅ 图书出入库管理
- ⭕ 可能的扩展：图书抓取（暂不实现）

### 核心约束
- **场景范围**：单层图书馆（不考虑多层、电梯）
- **机器人形态**：服务型机器人（仅导航和指示，不执行抓取）
- **开发重点**：仿真环境功能验证，不考虑Sim2Real迁移

---

## 已确认的技术决策

### 1. 仿真环境选择
| 决策项 | 选择 | 理由 |
|--------|------|------|
| **仿真平台** | Gazebo Classic | ROS2集成成熟、资源丰富、社区支持好 |
| **机器人底盘** | TurtleBot3 Waffle Pi | 平台大、承重好、稳定性高、计算能力强 |
| **图书识别方式** | RFID仿真（方案B） | 实现简单、性能开销小、可模拟真实RFID特性 |
| **扫描方式** | **四向扫描** | 前、后、左、右四个90°扇形，平衡覆盖与方向精度 |

### 4. 性能与优化决策（新增）
| 决策项 | 选择 | 关键参数 |
|--------|------|----------|
| **默认图书数量** | 50-100本 | 启动时间~15秒，平衡开发效率与测试完整性 |
| **最大图书数量** | 500本 | 压力测试上限，避免仿真卡顿 |
| **书架数量** | 24个（4排×6个） | 默认配置，可扩展至60个用于压力测试 |
| **动态障碍物** | 3-4个 | 1移动读者 + 1静止读者 + 1-2移动椅子 |
| **图书碰撞检测** | **禁用** | 图书仅视觉显示，不参与物理碰撞计算 |
| **加载策略** | **参数化实例化** | 1个图书模板 + 多实例配置，减少内存占用 |
| **性能目标** | 启动<15秒，运行>30 FPS | 内存占用<2GB |
| **书架模型** | **参数化模板** | 1个SDF模板，参数生成24个实例 |

### 2. 核心架构决策
| 决策项 | 选择 | 关键参数 |
|--------|------|----------|
| **数据存储** | SQLite数据库 | 支持查询和事务、轻量级、无需独立服务器 |
| **人机交互** | 方案A：屏幕显示 + 视觉标记 | 屏幕显示图书信息和位置描述，Visual marker指示精确位置 |
| **任务队列** | FIFO队列 | 先到先服务，Phase 2可考虑优先级扩展 |
| **感知系统** | 激光雷达 + RGB相机 + IMU | 完整环境感知能力 |

### 3. 范围界定
- ✅ **包含**：单层图书馆、导航避障、图书检索、库存管理
- ❌ **不包含**：Sim2Real迁移、多楼层导航、图书抓取、多机器人协作

---

## 系统架构

### ROS 2节点通信拓扑

```
┌─────────────────────────────────────────────────────────┐
│ 客户端层 (Web/语音/CLI)                                  │
└─────────────────────────────────────────────────────────┘
                           │ Service/Action调用
                           ↓
┌─────────────────────────────────────────────────────────┐
│ 任务管理层 (libbot_tasks)                                │
├─────────────────────────────────────────────────────────┤
│ BookManager (Action: FindBook, Service: GetBookInfo)   │
│ InventoryManager (库存盘点)                              │
│ TaskQueueManager (FIFO任务队列)                         │
└─────────────────────────────────────────────────────────┘
         │                         │                   │
         ↓                         ↓                   ↓
┌──────────────┐         ┌──────────────┐      ┌──────────────┐
│ 导航层        │         │ 感知层        │      │ 数据层        │
│ (Nav2)       │         │ (四向RFID)   │      │ (SQLite)     │
├──────────────┤         ├──────────────┤      ├──────────────┤
│ - Planner    │◄────────┤ - Front      │      │ - Books      │
│ - Controller │         │ - Back       │      │ - Inventory  │
│ - BT Navigator│        │ - Left       │      │ - Task Log   │
│              │         │ - Right      │      │              │
└──────────────┘         └──────────────┘      └──────────────┘
         ▲                         │
         │                         ▼
┌──────────────┐         ┌──────────────┐
│ 传感器数据    │         │ 视觉识别      │
│ (激光/IMU)   │         │ (AprilTag)   │
└──────────────┘         └──────────────┘
```

### 关键ROS 2接口

#### Topic通信
```yaml
/rfid/scan/front:          # 前向RFID扫描结果（10Hz）
/rfid/scan/back:           # 后向RFID扫描结果
/rfid/scan/left:           # 左向RFID扫描结果
/rfid/scan/right:          # 右向RFID扫描结果

/books/locations:          # 所有图书位置（1Hz，用于RViz可视化）
/tf:                       # 坐标变换（实时）
/tf_static:                # 静态坐标变换
```

#### Service通信
```yaml
/get_book_info:            # 查询图书信息
  - 输入: book_id (string)
  - 输出: title, author, location, status

/update_book_location:     # 更新图书位置
  - 输入: book_id, new_location
  - 输出: success, message

/check_robot_status:       # 检查机器人状态
```

#### Action通信
```yaml
/find_book (FindBook Action):
  - Goal: book_id, guide_patron
  - Result: success, book_pose, search_time
  - Feedback: status, progress, distance_to_book

/perform_inventory (库存盘点 Action):
  - Goal: zone, scan_mode
  - Result: books_found, books_missing, misplaced_books
  - Feedback: progress, current_location
```

---

## 详细设计方案

### 一、四向RFID扫描系统

#### 设计决策
使用**四向扫描**（前、后、左、右四个90°扇形），而非360°全向扫描。

**理由：**
- 方向信息明确，无需复杂的角度推算
- 每个方向独立处理，降低复杂度
- 更适合精确找书和人机交互
- 同时保持较好的环境覆盖能力

#### 硬件配置
在机器人上安装4个独立的RFID读取器（SDF模型）：

```
        前向 (0°)
          ↑
          |
左向(90°) ←─┼─→ 右向(-90°)
          |
          ↓
        后向 (180°)
```

**位置：**
- 高度：距离地面30cm（适配书架层高度）
- 距离机器人中心：15cm
- 朝向：每个读取器指向其对应方向

#### ROS 2接口
发布四个独立的Topic：
- `/rfid/scan/front` - 前向扫描（机器人前进方向）
- `/rfid/scan/back` - 后向扫描
- `/rfid/scan/left` - 左向扫描
- `/rfid/scan/right` - 右向扫描

每个Topic发布 `RFIDScan.msg` 消息，包含检测到的标签列表。

#### 关键参数
```yaml
detection_range: 0.5        # 检测范围 0.5米
detection_angle: 90.0      # 每个方向90°扇形
scan_rate: 10.0            # 扫描频率 10Hz

# 噪声参数
enable_realistic_noise: true
false_negative_rate: 0.15  # 15%漏检率（模拟真实RFID环境）
```

#### 使用场景

**场景1：库存盘点**
```
优势：无需旋转机器人
机器人沿过道行走，四向读取器同时工作
左侧扫描书架A，右侧扫描书架B
前方预警障碍物，后方记录已扫描区域

效率提升：节省20-30秒的旋转时间
```

**场景2：精确找书**
```
优势：方向信息明确
当book_X在左侧被检测到 → 明确知道向左转
当前方检测到 → 继续前进
当多个方向同时检测到 → 机器人处于目标区域中心
```

### 二、导航与避障系统

#### 基于Nav2的导航系统

**本地规划器：** DWB（Dynamic Window Approach）
- **最大速度：** 0.3 m/s（图书馆环境需要安静、谨慎）
- **角速度：** 0.5 rad/s
- **路径对齐权重：** 32.0（重视全局路径）
- **障碍物距离权重：** 0.02（保持安全距离）

**全局规划器：** SmacPlannerLattice
- **最小转弯半径：** 0.2米（适应狭窄过道）
- **路径平滑：** 支持连续角度，避免锯齿路径
- **规划时间限制：** 5.0秒

#### 代价地图配置（Costmap）

多层代价地图设计：

```yaml
# 静态层（书架、墙壁）
static_layer:
  - 来自SLAM地图
  - 永不改变

# 膨胀层（安全边界）
# 书架：0.5米膨胀
# 墙壁：0.3米膨胀
inflation_layer:
  inflation_radius: 0.5
  cost_scaling_factor: 3.0

# 动态障碍物层（行人、椅子）
obstacle_layer:
  - 基于实时激光雷达
  - 观测到障碍物：代价升高
  - 障碍物消失后：代价指数衰减（5秒后清除）
  - 参数：observation_persistence: 5.0

# 社会代价层（可选）
social_layer:
  # 阅读区增加额外代价
  # 机器人优先选择主通道
```

#### 狭窄过道处理

**挑战：** 标准过道宽度1.2米，TurtleBot3 Waffle宽度0.281米

**解决方案：**
1. 缩小的footprint（0.3m × 0.3m，留安全余量）
2. 降低最大速度至0.3 m/s
3. 禁止穿越阅览区（代价地图禁区）
4. 在过道中降低速度（0.15 m/s）

#### 定位挑战与应对

**图书馆环境特点：**
- 高度重复的环境（书架外观相似）
- 对称布局
- 动态障碍物多

**AMCL参数调优：**
```yaml
min_particles: 3000      # 增加至3000（默认500）
max_particles: 8000      # 增加至8000
laser_likelihood_max_dist: 2.0  # 激光最大距离
```

**恢复行为：**
1. 原地旋转360°（寻找匹配特征）
2. 清除代价地图（排除动态障碍物干扰）
3. 后退0.5米重试
4. 语音提示（可选项）

### 三、数据管理系统（SQLite）

#### 数据库Schema设计

**books表（图书信息）**
```sql
CREATE TABLE books (
    id TEXT PRIMARY KEY,              -- 图书唯一ID
    isbn TEXT UNIQUE,                 -- ISBN号
    title TEXT NOT NULL,              -- 书名
    author TEXT,                      -- 作者
    category TEXT,                    -- 分类
    keywords TEXT,                    -- 关键词（JSON格式）

    -- 位置信息
    shelf_zone TEXT NOT NULL,         -- 区域（如 "A1", "B3"）
    shelf_level INTEGER NOT NULL,     -- 层数（0=最底层，4=顶层）
    shelf_position INTEGER NOT NULL,  -- 该层位置（0-14，从左到右）

    -- 精确坐标（用于导航）
    pose_x REAL,                      -- X坐标
    pose_y REAL,                      -- Y坐标
    pose_z REAL,                      -- Z坐标（高度）

    -- 物理属性
    thickness REAL,                   -- 厚度（米）
    width REAL,                       -- 宽度（米）
    height REAL,                      -- 高度（米）
    spine_color TEXT,                 -- 书脊颜色
    tag_id INTEGER,                   -- RFID标签ID

    -- 状态管理
    status TEXT DEFAULT 'on_shelf',   -- on_shelf | borrowed | misplaced | reserved
    borrow_count INTEGER DEFAULT 0,   -- 借阅次数
    last_updated TIMESTAMP,           -- 最后更新时间

    -- 扩展信息
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_books_zone ON books(shelf_zone);
CREATE INDEX idx_books_status ON books(status);
CREATE INDEX idx_books_tag ON books(tag_id);
```

**inventory_log表（库存盘点日志）**
```sql
CREATE TABLE inventory_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id TEXT NOT NULL,
    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    robot_id TEXT,                    -- 执行扫描的机器人

    -- 预期状态
    expected_zone TEXT,
    expected_level INTEGER,
    expected_position INTEGER,

    -- 实际检测
    detected_zone TEXT,
    detected_level INTEGER,
    detected_position INTEGER,
    detected_pose_x REAL,
    detected_pose_y REAL,

    -- 异常标记
    is_misplaced BOOLEAN,
    is_missing BOOLEAN,
    notes TEXT,                       -- 备注

    FOREIGN KEY (book_id) REFERENCES books(id)
);

CREATE INDEX idx_inventory_book ON inventory_log(book_id);
CREATE INDEX idx_inventory_time ON inventory_log(scan_time);
```

**task_queue表（任务队列）**
```sql
CREATE TABLE task_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type TEXT NOT NULL,          -- 'find_book' | 'inventory'
    task_data TEXT,                   -- JSON格式的任务参数

    status TEXT DEFAULT 'pending',    -- pending | in_progress | completed | failed
    priority INTEGER DEFAULT 0,       -- 优先级（预留）

    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_time TIMESTAMP,
    completed_time TIMESTAMP,

    result TEXT,                      -- 任务结果（JSON）
    error_message TEXT                -- 错误信息
);

CREATE INDEX idx_task_status ON task_queue(status);
CREATE INDEX idx_task_priority ON task_queue(priority);
```

#### 批量数据操作

**批量生成图书数据（Python示例）：**
```python
import csv
import random

# 生成N本图书
for i in range(100):
    book = {
        'book_id': f'978-3-16-{1000000 + i}',
        'isbn': f'978-3-16-{1000000 + i}',
        'title': f'Book Title {i}',
        'author': f'Author {i}',
        'category': random.choice(['Robotics', 'Programming', 'AI/ML']),
        'shelf_zone': f'{random.choice("ABCDEF")}{random.randint(1, 10)}',
        'shelf_level': random.randint(0, 4),
        'shelf_position': random.randint(0, 14),
        'thickness': round(random.uniform(0.015, 0.035), 3),
        'width': round(random.uniform(0.13, 0.17), 3),
        'height': round(random.uniform(0.18, 0.26), 3),
        'spine_color': random.choice(['red', 'blue', 'green']),
        'tag_id': 100 + i
    }
    # 写入CSV或SQLite
```

### 四、图书模型生成系统（含性能优化）

#### 高层设计原则
1. **按需生成，分层加载**
2. **参数化实例化（Instancing）**：1个模板 + 多配置
3. **简化碰撞检测**：图书禁用碰撞（仅视觉）

#### 图书数量分层策略
```yaml
测试级别:
  Level 1 (开发测试): 10-20本
    - 启动时间 <5秒
    - 用途：快速功能验证

  Level 2 (功能测试): 50-100本（默认配置）
    - 启动时间 ~15秒
    - 用途：完整功能测试

  Level 3 (场景测试): 200-300本
    - 用途：复杂场景验证

  Level 4 (压力测试): 500本（上限）
    - 用途：性能基准测试
```

#### 文件结构
```
~/lib_bot_ws/
├── library_config/
│   ├── books.csv              # 图书元数据（默认50-100本）
│   ├── books_large.csv        # 500本（压力测试备用）
│   ├── book_template.yaml     # 1个通用模板
│   ├── bookshelf_templates.yaml  # 书架模板
│   └── library.db            # SQLite数据库
├──
```

#### 性能优化实现（高层）
```yaml
# 图书模型生成策略
模型生成方式:
  - 不生成: 1000个独立SDF文件
  - 采用: 1个SDF模板 + CSV配置

碰撞检测:
  - 禁用: 图书物理碰撞计算（设置为视觉only）
  - 理由: 图书不会阻挡机器人路径，减少90%物理计算

加载时机:
  - 不支持: 运行时动态加载/卸载（Phase 1）
  - Future: 可支持区域加载（Phase 3）

内存占用预估:
  - 50本书: ~500MB
  - 100本书: ~800MB
  - 500本书: ~1.8GB（达到压力测试上限）
```

#### 生成器功能

**generate_books.py脚本功能：**
1. 从CSV读取图书数据
2. 为每本书生成Gazebo SDF模型
3. 生成AprilTag等视觉标记
4. 创建SQLite数据库并导入数据
5. 生成RViz可视化配置文件

**批量生成1000本书的流程：**
```bash
# 1. 生成元数据
cd ~/lib_bot_ws/library_config
python3 generate_book_metadata.py --num-books 1000 --output books.csv

# 2. 生成Gazebo模型和数据库
python3 generate_books.py --config-dir ./ --num-books 1000

# 输出：
# - library_config/books/ (1000个SDF模型文件)
# - library_config/library.db (SQLite数据库)
# - library_config/book_markers.yaml (RViz配置)
```

### 五、书架模型系统（含性能优化）

#### 书架数量策略
```yaml
默认配置: 24个书架（4排 × 6个）
  - 排: A, B, C, D
  - 每排: 1-6号
  - 总容量: 24书架 × 5层 × 15本 = 1800本书位（实际50-100本）

压力测试: 可扩展至60个书架（6排 × 10个）
  - 仅在需要时手动启用
```

#### 模型优化方案（高层）
```yaml
模型策略:
  - 不使用: 60个独立SDF文件
  - 采用: 1个参数化模板 + 运行时实例化

参数化设计:
  - 1个 bookshelf_template.sdf
  - 参数: width, depth, height, shelf_levels, books_per_level
  - 脚本生成24个配置实例

性能优势:
  - Gazebo只加载1个模型定义（减少内存）
  - 启动时通过参数化实例化24个书架
  - 渲染效率提升

碰撞优化:
  - 书架框架: 完整碰撞计算
  - 书架层板: 简化碰撞盒或仅用框架碰撞
```

### 六、动态障碍物系统

#### Gazebo Actor插件

**行人模拟：**
```xml
<actor name="reader1">
  <skin><filename>model://person/meshes/sitting.dae</filename></skin>
  <animation><filename>model://person/walk.dae</filename></animation>

  <script>
    <loop>true</loop>
    <trajectory id="reader1_path">
      <waypoint><time>0</time><pose>5 5 0 0 0 0</pose></waypoint>
      <waypoint><time>5</time><pose>8 8 0 0 0 0</pose></waypoint>
      <waypoint><time>10</time><pose>12 13 0 0 0 1.57</pose></waypoint>
      <waypoint><time>80</time><pose>12 13 0 0 0 1.57</pose></waypoint> <!-- 阅读75秒 -->
      <waypoint><time>85</time><pose>8 8 0 0 0 3.14</pose></waypoint>
    </trajectory>
  </script>
</actor>
```

**椅子动态移动：**
```xml
<model name="chair_movable" static="false">
  <link name="chair_link">
    <collision><geometry><box><size>0.5 0.5 1.0</size></box></geometry></collision>
    <visual><geometry><mesh><uri>model://chair</uri></mesh></geometry></visual>
  </link>

  <!-- 插件：随机小范围移动 -->
  <plugin name="random_movement" filename="libgazebo_random_movement.so">
    <update_rate>0.1</update_rate>  <!-- 每10秒随机移动一次 -->
    <max_translation>0.5</max_translation>
    <max_rotation>0.5</max_rotation>
  </plugin>
</model>
```

---

## 待解决问题清单

### 高优先级
1. **图书位置初始化**：如何从CSV自动生成精确的Gazebo位置（需要地图配置）
2. **四向扫描数据融合**：当多个方向同时检测到同一本书时，如何融合数据
3. **导航路径优化**：在狭窄过道中，如何生成最合适的路径

### 中优先级
4. **任务超时处理**：如果5分钟找不到书，应该放弃还是继续
5. **数据库同步机制**：Gazebo模型位置修改后，如何同步到SQLite
6. **错误恢复逻辑**：机器人卡住或定位丢失的恢复流程

### 低优先级
7. **性能优化**：1000本书时，Gazebo加载和仿真性能
8. **多语言支持**：书名、作者如何处理多语言字符
9. **可视化优化**：RViz中大量图书标记的显示效率

---

## 演进路线

### Phase 1：MVP（最小可行产品）- 4周
**目标：** 基础导航 + 单本书检索

1. 搭建基础Gazebo环境
   - TurtleBot3 Waffle + 空房间
   - 激光雷达 + 里程计 + AMCL

2. 实现基础导航
   - Nav2配置和调优
   - 能够导航到目标点

3. 集成四向RFID仿真
   - 四个方向的扫描器
   - 发布检测Topic

4. 实现FindBook Action
   - 查询数据库
   - 导航到目标书架
   - 发布检测结果

**完成标志：**
- 能从任意位置导航到目标书架
- 能够"找到"目标图书（检测到RFID标签）

### Phase 2：功能完善 - 4周
**目标：** 完整借还书流程 + 库存管理

1. SQLite数据库集成
   - 生成100本测试数据
   - 实现查询和更新接口

2. 人机交互界面
   - 屏幕显示（Marker显示）
   - 位置指示（激光/箭头）

3. 多任务队列
   - FIFO任务管理
   - 任务日志记录

4. 库存盘点功能
   - 沿过道自动扫描
   - 比对数据库
   - 生成报告

**完成标志：**
- 能执行完整的借还书流程（人机协作版本）
- 能完成指定区域的库存盘点

### Phase 3：仿真真实性提升 - 4周
**目标：** 增加噪声、动态障碍物，接近真实环境

1. RFID噪声模型
   - 距离-概率曲线
   - 漏检和误检模拟

2. 动态障碍物仿真
   - 行人移动（Gazebo Actors）
   - 可移动椅子

3. 代价地图优化
   - 社交导航层
   - 动态区域代价

4. 场景测试
   - 1000本书压力测试
   - 复杂环境测试

**完成标志：**
- 在仿真环境中的行为接近真实机器人
- 能处理动态障碍物和复杂场景

### Phase 4：进阶功能（可选）- 4周
**目标：** 多机器人、数字孪生等高级功能

1. 多机器人协作
   - 任务分配
   - 路径协调

2. Web界面
   - 远程控制
   - 实时监控

3. 数字孪生
   - 仿真与真实同步
   - 预测性维护

4. 性能优化
   - Gazebo性能调优
   - 数据库优化

**完成标志：**
- 可作为产品原型演示
- 具备生产级特性

---

## 附录

### A. 相关文件路径

```
~/lib_bot_ws/
├── src/
│   ├── libbot_description/        # 机器人模型
│   ├── libbot_simulation/         # 仿真环境
│   ├── libbot_navigation/         # 导航配置
│   ├── libbot_perception/         # 感知（四向RFID）
│   ├── libbot_tasks/              # 任务管理
│   ├── libbot_msgs/               # 自定义消息
│   └── libbot_database/           # 数据库接口
│
├── library_config/               # 配置文件
│   ├── books.csv                  # 图书元数据
│   ├── bookshelf_templates.yaml   # 书架模板
│   ├── library.db                 # SQLite数据库
│   └── book_markers.yaml          # RViz配置
│
├── docs/
│   ├── design_brainstorm_detailed.md    # ← 本文档
│   └── design_brainstorm_highlevel.md   # 高层设计文档
│
└── scripts/
    ├── generate_books.py          # 批量生成图书
    ├── generate_bookshelves.py    # 批量生成书架
    └── test_scenarios/            # 测试场景
```

### B. 参考资料

- ROS 2 Navigation官方文档
- Gazebo Classic教程
- TurtleBot3文档
- Nav2配置指南

---

## 附录D：Phase 1功能细节设计（补充）

> 该章节补充了前5项功能的详细设计
> 生成日期：2026-4-7

---

## D1. 人机交互细节设计

### D1.1 UI响应时间要求

```yaml
用户操作 → UI响应:
├─ 按钮点击 → 视觉反馈: ≤50ms
├─ 表单提交 → 开始执行: ≤100ms
├─ 状态更新（进度）: ≤200ms
├─ 错误提示弹出: ≤100ms
└─ 日志实时显示: ≤50ms

ROS数据 → UI更新:
├─ 机器人位置更新: ≤100ms
├─ 任务状态变更: ≤150ms
├─ 扫描结果更新: ≤200ms
└─ 导航进度更新: ≤150ms
```

### D1.2 UI与ROS2通信架构

**线程模型：**
```
主线程 (UI)          ROS2线程          回调线程
   │                    │                 │
   │  1. 用户点击按钮     │                 │
   │─────────────────►│                 │
   │  2. 调用send_goal() │                 │
   │────────────────────┼────────────────►│
   │                    │    3. ROS2回调    │
   │                    │◄─────────────────│
   │    4. 发射Signal    │                 │
   │◄────────────────── │                 │
   │  5. Slot响应更新UI  │                 │
   │                    │                 │
```

**核心通信接口：**
```python
# Ros2Manager类（简化版）
class Ros2Manager(QObject):
    # Signal定义（线程安全）
    task_status_updated = Signal(dict)
    robot_pose_updated = Signal(Pose)
    book_detected = Signal(dict)
    error_occurred = Signal(str)

    def send_find_book_goal(self, book_id):
        # 发送Action Goal
        pass

    def cancel_task(self):
        # 取消当前任务
        pass
```

### D1.3 错误信息显示策略

**四级错误显示策略：**

**Level 1: 关键错误（Critical）**
```yaml
示例: 数据库连接失败、ROS2主节点断开

UI表现: 弹出模态对话框
- 红色图标 + 错误代码
- 自动暂停所有任务
- 需要用户确认后关闭

对话框内容:
┌────────────────────────────────────┐
│ ❌ 关键错误                        │
│                                    │
│ 错误代码: DB_CONN_001              │
│                                    │
│ 数据库连接失败：                   │
│ 无法连接到 /library.db             │
│                                    │
│ 建议操作：                         │
│ 1. 检查数据库文件是否存在          │
│ 2. 检查文件权限                    │
│ 3. 查看详细日志                    │
│                                    │
│         [查看日志] [确认]          │
└────────────────────────────────────┘
```

**Level 2: 任务错误（Task Error）**
```yaml
示例: 找不到指定图书、导航失败

UI表现: 右侧面板顶部红色横幅，15秒后自动消失

横幅样式:
┌────────────────────────────────────┐
│ ⚠️  任务 #42 失败                  │
│ 原因：未找到图书 (ID: 978316...)  │
│ [查看详情] [重新查找]              │
└────────────────────────────────────┘
```

**Level 3: 警告（Warning）**
```yaml
示例: 路径被临时阻挡、RFID信号弱

UI表现: 右侧面板黄色通知，5秒后自动消失

样式:
🟡 路径被阻挡，正在重新规划...
```

**Level 4: 信息（Info）**
```yaml
示例: 任务开始、检测到图书、导航完成

UI表现: 仅在日志区域显示
```

### D1.4 UI状态管理

**状态机设计：**
```python
class UIState(Enum):
    IDLE = "idle"                    # 空闲，无任务
    QUERYING_DB = "querying_db"      # 查询数据库
    NAVIGATING = "navigating"        # 导航中
    SCANNING = "scanning"            # 扫描中
    COMPLETED = "completed"          # 完成
    PAUSED = "paused"                # 暂停
    CANCELLED = "cancelled"          # 已取消
    ERROR = "error"                  # 出错
```

**状态转换：**
```
IDLE → QUERYING_DB → NAVIGATING → SCANNING → COMPLETED
  ↑       ↓              ↓            ↓          ↓
  └────── PAUSED ←───────┴────────────┴────→ CANCELLED
                            ↓
                          ERROR
```

**UI元素状态规则：**

| UI元素 | IDLE | QUERYING | NAVIGATING | SCANNING | COMPLETED | PAUSED | ERROR |
|--------|------|----------|------------|----------|-----------|--------|-------|
| 找书按钮 | 启用 | 禁用 | 禁用 | 禁用 | 启用 | 禁用 | 禁用 |
| 暂停按钮 | 禁用 | 禁用 | 启用 | 启用 | 禁用 | 启用 | 禁用 |
| 取消按钮 | 禁用 | 启用 | 启用 | 启用 | 禁用 | 启用 | 启用 |
| 进度条 | 隐藏 | 显示 | 显示 | 显示 | 显示 | 显示 | 隐藏 |
| 实时数据 | 隐藏 | 部分 | 显示 | 显示 | 显示 | 显示 | 隐藏 |

---

## D2. 错误处理与恢复机制

### D2.1 错误分类体系

**基于来源的分类：**
```yaml
感知层错误:
├── RFID检测失败
│   ├── 漏检（未检测到存在的图书）
│   ├── 误检（检测到不存在的图书）
│   └── 检测超时（长时间检测不到）
└── 传感器错误
    ├── 激光雷达数据异常
    └── IMU数据漂移

导航层错误:
├── 定位错误
│   ├── AMCL定位丢失（粒子发散）
│   └── 定位精度不足
├── 路径规划失败
│   └── 无可行路径
└── 运动控制错误
    ├── 机器人卡住（局部最小值）
    └── 速度指令执行失败

系统层错误:
├── 数据库错误
│   ├── 连接失败
│   ├── 查询超时
│   └── 数据一致性错误
├── ROS2通信错误
│   └── 节点断开连接
└── 业务逻辑错误
    └── 找不到指定图书
```

**基于严重程度的分类：**
```yaml
致命错误 (Fatal) - 需要人工干预
├── 数据库完全不可用
├── ROS2主节点崩溃
└── Gazebo仿真崩溃

严重错误 (Critical) - 自动尝试恢复，失败则人工干预
├── AMCL完全丢失定位（90%概率）
├── 导航持续失败（5分钟无法到达）
└── 碰撞传感器触发

一般错误 (Error) - 自动恢复，记录日志
├── 单次RFID漏检
├── 路径重规划（<3次）
└── 数据库查询超时（<3次）

警告 (Warning) - 无需恢复，提示用户
├── RFID信号弱
├── 路径被临时阻挡
└── 速度受限
```

### D2.2 三层恢复机制

**L1 - 快速恢复（0-5秒，任务内部）**
```yaml
恢复行为1：重新扫描（RFID专用）
触发条件:
  - 到达目标位置后，10秒内未检测到图书
  - 检测信号强度 < 0.5

恢复动作:
  - 保持位置不变
  - 提高RFID灵敏度（降低阈值）
  - 延长扫描时间（从10秒到20秒）

恢复时间: 5-10秒
失败策略: 升级到L2恢复

恢复行为2：路径微调
触发条件:
  - RFID检测到图书，但距离 > 0.8米
  - 检测方向不明确（多个方向都检测到）

恢复动作:
  - 沿检测方向前进30cm
  - 重新扫描

恢复时间: 3-5秒
失败策略: 如果前进后距离增加，退回并升级到L2
```

**L2 - 状态重置（5-30秒，任务层面）**
```yaml
恢复行为3：重新定位
触发条件:
  - L1恢复失败
  - 机器人仍然找不到图书
  - 定位误差 > 1米

恢复动作:
  1. 返回上一个已知良好位置（过道入口）
  2. 原地旋转360°（帮助AMCL重新定位）
  3. 重新规划路径到书架
  4. 再次执行L1恢复行为

恢复时间: 30-40秒
失败策略: 重试2次后升级到L3

恢复行为4：目标重定义
触发条件:
  - 数据库显示图书在A3，但在A3找不到
  - 附近书架(A2, A4)检测到该图书

恢复动作:
  1. 搜索相邻书架（±1书架）
  2. 如果找到，更新数据库位置
  3. 重新导航到正确位置
  4. 执行L1恢复行为

恢复时间: 20-30秒
应用场景: 处理"错架"情况（读者归还时放错位置）
```

**L3 - 系统重置（30秒-2分钟，系统层面）**
```yaml
恢复行为5：返回Home重置
触发条件:
  - 多次L2恢复失败
  - 严重错误（定位完全丢失）
  - 未知错误（意外异常）

恢复动作:
  1. 取消当前任务
  2. 导航到Home位置（充电站）
  3. 重置所有内部状态
  4. 重新初始化：
     - 清空临时缓存
     - 重连数据库
     - 重置AMCL粒子
  5. 等待用户确认
  6. 接受新任务

恢复时间: 60-120秒
注意: 必须有用户确认才继续

恢复行为6：人工接管
触发条件:
  - L3恢复失败
  - 数据库损坏
  - Gazebo崩溃
  - 连续3次任务失败（系统不稳定）

恢复动作:
  1. 立即停止所有电机
  2. 标记所有节点状态为ERROR
  3. 显示详细错误信息
  4. 生成错误报告
  5. 等待人工干预
```

### D2.3 错误检测机制

**导航错误检测：**
```yaml
定位误差监控:
  监控频率: 10Hz
  判断条件: |robot_pose - amcl_pose| > 1.0米
  确认时间: 3秒（避免瞬时差）
  处理: 触发L2恢复

规划失败检测:
  监控: /path_planning_error Topic
  错误类型: 无有效路径、规划超时>5秒、路径无效
  处理策略:
    - 第一次: 扩大膨胀层，重规划
    - 第二次: 触发L2恢复（切换入口点）
    - 第三次: 标记目标不可达

机器人卡住检测:
  监控: cmd_vel vs actual_vel
  判断: 指令速度>0.1且连续2秒实际速度<0.05
  处理: 停止→转向30°→前进→失败则触发L2
```

**RFID检测错误检测：**
```yaml
漏检检测:
  判断: 检测率<80%（实际/预期）
  处理: 提高灵敏度 + 延长扫描时间

误检检测:
  判断: 检测到图书散布范围>2米
  处理: 降低灵敏度，聚焦最近图书

检测超时:
  判断: 到达位置后扫描>30秒
  处理: 触发L2恢复（重新定位）
```

### D2.4 与Behavior Tree集成

**错误处理作为Recovery Node：**
```
主行为树（FindBook）:
├── Sequence: 查找并找到图书
│   ├── RecoveryNode（数据库查询）
│   │   ├── 执行查询
│   │   └── 重试（最多3次）
│   ├──
│   ├── RecoveryNode（导航）
│   │   ├── 执行导航
│   │   └── L2恢复（重定位）
│   └── RecoveryNode（扫描）
│       ├── 执行扫描（10秒）
│       └── L1恢复（提高灵敏度，再扫10秒）
└── 返回结果

RecoveryNode逻辑:
- 先执行主节点
- 如果返回FAILURE
- 执行恢复子树
- 如果恢复成功，重新执行主节点
- 如果恢复失败，返回FAILURE
```

---

## D3. 日志与监控系统

### D3.1 日志方案决策

**混合日志方案：**
```yaml
ROS2 rclpy.logging:
  用途: 节点内部调试、错误追踪
  级别: INFO, WARN, ERROR
  示例: self.get_logger().error(f"Book {book_id} not found")

SQLite业务日志:
  用途: 业务操作记录、库存日志、任务历史
  存储表: inventory_log, task_queue
  示例: 每次扫描、位置更新、任务状态变更
```

### D3.2 日志分类

**系统日志（ROS2）：**
```yaml
├── 导航日志: 路径规划、定位更新、避障事件
├── 感知日志: RFID扫描结果、检测率统计、噪声参数
├── 数据库日志: 查询执行、更新操作、连接状态
└── BT执行日志: 节点进入/退出、状态变化、恢复触发
```

**业务日志（SQLite）：**
```yaml
├── 任务日志: 创建、状态流转、完成、失败
├── 图书日志: 借出、归还、错架、位置更新
└── 库存日志: 盘点开始/结束、检测详情、报告
```

### D3.3 监控指标

**系统健康指标：**
```yaml
导航健康度:
  - AMCL频率: 10Hz（最低5Hz）
  - 规划成功率: >95%
  - 重规划次数: <5次/任务

感知健康度:
  - RFID扫描频率: 10Hz ± 10%
  - 检测成功率: >85%
  - 漏检率: <20%

系统资源:
  - CPU使用率: <70%
  - 内存占用: <2GB
  - Topic延迟: <100ms
```

**业务指标：**
```yaml
任务执行:
  - 完成率: 成功/总数
  - 平均执行时间
  - 取消率、错误率

图书管理:
  - 错架率: 错架/总数
  - 缺失率、盘点覆盖率
```

### D3.4 UI日志面板设计

**日志显示区域：**
```yaml
位置: 右侧面板底部
可见条数: 10-15条
总缓冲区: 100条
自动滚动: 始终显示最新
级别过滤: [✓]INFO [✓]WARN [✓]ERROR

颜色编码:
  INFO:  蓝色 (#2196F3)
  WARN:  橙色 (#FF9800)
  ERROR: 红色 (#F44336)

日志格式:
  [14:23:15] [INFO] Task #42 started
  [14:23:18] [WARN] RFID signal weak (0.3)
  [14:24:10] [ERROR] Book not found
```

---

## D4. 配置管理系统

### D4.1 配置策略决策

**动态参数 → ROS2 Parameter：**
```yaml
- 导航速度（max_vel_x: 0.1-0.5 m/s）
- RFID灵敏度（detection_threshold: 0.5-1.0）
- 扫描时间（scan_duration: 5-30秒）
- 恢复行为参数（retry_count: 1-5次）
```

**静态参数 → YAML配置文件：**
```yaml
- 图书馆布局（书架位置、区域）
- 数据库配置（DB路径、表结构）
- 机器人硬件参数（TF、footprint）
- 性能参数（图书数量、最大速度）
```

### D4.2 配置文件结构

**主配置文件（library_config.yaml）：**
```yaml
global:
  mode: "simulation"      # simulation | production
  log_level: "INFO"       # DEBUG | INFO | WARN | ERROR
  performance_level: 2    # 1:低(50本), 2:中(100本), 3:高(500本)

library:
  room_width: 15.0
  room_height: 12.0
  bookshelves:
    rows: ['A', 'B', 'C', 'D']
    columns: 6
    shelf_width: 0.8
    shelf_depth: 0.4
    shelf_height: 1.5
    levels: 5
    books_per_level: 15

robot:
  model: "turtlebot3_waffle"
  max_vel_x: 0.3
  min_vel_x: -0.15
  max_vel_theta: 0.5
  footprint: [0.3, 0.3]
  rfid_readers:
    count: 4
    height: 0.3
    range: 0.5
    false_negative_rate: 0.15

navigation:
  amcl:
    min_particles: 3000
    max_particles: 8000
  costmap:
    inflation_radius: 0.5
    cost_scaling_factor: 3.0
  planner:
    min_turn_radius: 0.2
    planning_time_limit: 5.0
  recovery:
    stuck_timeout: 2.0

database:
  db_path: "~/lib_bot_ws/library_config/library.db"
  max_connections: 5
  timeout: 30.0

ui:
  window:
    width: 800
    height: 600
    theme: "light"
  refresh_rate:
    robot_pose: 10
    task_status: 5
    rfid_signal: 5
  logs:
    max_entries: 100
    level_filter: ["INFO", "WARN", "ERROR"]

simulation:
  gazebo:
    real_time_factor: 1.0
  dynamic_obstacles:
    enabled: true
    count: 3
```

### D4.3 环境配置文件

```yaml
config_dev.yaml:
  global:
    mode: "simulation"
    log_level: "DEBUG"
    performance_level: 1
  book_count: 20  # 快速启动

config_test.yaml:
  global:
    mode: "simulation"
    log_level: "INFO"
    performance_level: 2
  book_count: 100

config_demo.yaml:
  global:
    mode: "simulation"
    log_level: "INFO"
    performance_level: 2
  book_count: 100
  ui:
    logs:
      level_filter: ["INFO", "WARN"]  # 隐藏ERROR

config_prod.yaml:
  global:
    mode: "production"
    log_level: "WARN"
  # Phase 1预留，暂不实现
```

### D4.4 动态参数更新流程

```yaml
1. 用户在UI拖动"导航速度"滑块（0.25 → 0.35）

2. UI调用Ros2Manager API:
   ros2_manager.update_param("max_vel_x", 0.35)

3. Ros2Manager发送参数更新:
   ros2 param set /bt_navigator max_vel_x 0.35

4. nav2节点收到参数变更:
   - 验证新值（范围检查）
   - 更新内部变量
   - 发布ParameterEvent通知

5. UI收到更新确认:
   - 显示"参数已更新"
   - 如果失败，显示错误原因

异常处理:
  - 参数验证失败（超出范围）→ UI显示错误
  - 节点未响应（超时5秒）→ 标记节点异常
  - 参数更新部分成功 → 显示哪些成功/失败
```

### D4.5 参数验证

```yaml
验证时机: 参数加载时 + 运行时动态更新时

验证规则示例:

max_vel_x:
  类型: double
  范围: [0.1, 0.5]
  默认值: 0.3
  验证: if value < 0.1 or value > 0.5: raise ValueError

book_count:
  类型: int
  枚举值: [10, 20, 50, 100, 200, 500]
  验证: 必须是预设值之一

mode:
  类型: string
  枚举值: ["simulation", "production"]
  验证: value in ["simulation", "production"]
```

---

## D5. API设计细节

### D5.1 API设计原则

```yaml
原则1：清晰的命名规范
  Topic: 使用自然语言，小写下划线
    ✅ /rfid/scan/front
    ❌ /RFIDScanFront

  Service: 动作 + 宾语
    ✅ /get_book_info
    ❌ /bookInfoGet

  Action: 动词短语
    ✅ /find_book
    ❌ /bookFinding

原则2：明确的错误码和状态
  每个API返回明确的status
  Service: 成功/失败 + 错误消息
  Action: 实时反馈包含progress和status

原则3：合理的超时机制
  Service: 默认5秒超时
  Action: 可配置timeout（默认5分钟）
  Topic: 数据驱动，无需超时

原则4：版本兼容性
  接口名称保持稳定
  消息字段只增不减
  新增参数设置默认值
```

### D5.2 Topic接口

#### /rfid/scan/{front,back,left,right}

```yaml
消息类型: libbot_msgs/RFIDScan
发布频率: 10Hz

消息结构:
std_msgs/Header header
libbot_msgs/RFIDTag[] detected_tags
  string tag_id            # RFID标签ID
  float64 signal_strength  # 0.0-1.0
  float64 distance         # 米
  geometry_msgs/Vector3 direction  # 相对方向
uint32 total_scans         # 总扫描次数

使用示例:
ros2 topic echo /rfid/scan/front
```

#### /books/locations

```yaml
消息类型: visualization_msgs/MarkerArray
发布频率: 1Hz

用途: 在RViz中显示所有图书位置
每个图书一个Marker，包含3D位置、尺寸、颜色
```

#### /system/health

```yaml
消息类型: libbot_msgs/SystemHealth
发布频率: 1Hz

消息结构:
builtin_interfaces/Time stamp
string[] node_names              # 节点名称列表
int32[] node_status              # 0=OK, 1=WARNING, 2=ERROR
float32 navigation_health        # 0.0-1.0
float32 perception_health        # 0.0-1.0
float32 database_health          # 0.0-1.0
string[] active_warnings
string[] active_errors
```

### D5.3 Service接口

#### /get_book_info

```yaml
请求:
string book_id          # 图书唯一ID
  or
string isbn             # ISBN号（二选一）

响应:
bool success
string message          # 错误消息（如果失败）

# 图书信息（成功时）
string id, isbn, title, author, category
string shelf_zone       # "A3"
int32 shelf_level       # 0-4
int32 shelf_position
geometry_msgs/Pose pose
string status           # on_shelf | borrowed | misplaced

错误码:
  SUCCESS: 0, NOT_FOUND: 1, DB_ERROR: 2, INVALID_ID: 3
```

#### /update_book_location

```yaml
请求:
string book_id
string shelf_zone       # 新位置
int32 shelf_level
int32 shelf_position
geometry_msgs/Pose new_pose
string reason           # "inventory_scan" | "manual_correction"

响应:
bool success
string message

错误码:
  SUCCESS: 0, BOOK_NOT_FOUND: 1, INVALID_LOCATION: 2, DB_UPDATE_FAILED: 3

业务逻辑:
  - 更新books表位置信息
  - inventory_log记录旧位置和新位置
  - 如果位置不同，标记为misplaced
```

#### /check_robot_status

```yaml
请求: std_srvs/srv/Trigger（空请求）

响应:
bool success
string message

# 状态信息
geometry_msgs/Pose current_pose
string current_task_id    # 空表示无任务
string task_status        # idle | querying_db | navigating | scanning | completed | error
string nav_status         # navigation2状态
float32 current_speed
string rfid_status
int32 detected_books_last_minute
float64 uptime            # 秒
int32 cpu_percent
int32 memory_mb

使用场景: UI每1秒调用一次，更新状态面板
```

### D5.4 Action接口

#### /find_book

```yaml
Goal:
string book_id          # 目标图书ID
bool guide_patron       # 是否引导读者（Phase 1: false）

Result:
bool success
string message

# 找到的图书信息
BookInfo book
geometry_msgs/Pose book_pose
float32 search_time
int32 navigation_attempts
int32 scan_attempts

状态码:
  SUCCESS: 0, BOOK_NOT_FOUND: 1, NAVIGATION_FAILED: 2
  TASK_CANCELLED: 3, TASK_TIMEOUT: 4, UNKNOWN_ERROR: 5

Feedback:
string status           # querying_db | navigating | scanning
float32 progress        # 0.0-1.0

# 导航阶段
string nav_status
float32 distance_to_goal
geometry_msgs/Pose current_pose

# 扫描阶段
int32 books_detected
float32 signal_strength
string detection_direction  # front | back | left | right
float32 estimated_remaining  # 预计剩余时间（秒）
```

#### /perform_inventory

```yaml
Goal:
string zone              # "A" | "B" | "C" | "D" | "all"
string scan_mode         # "fast" | "detailed"

Result:
bool success
string message

# 盘点结果
int32 total_books         # 数据库总数
int32 books_found         # 实际检测到
int32 books_missing       # 缺失数量
int32 books_misplaced

# 详细清单
BookInfo[] found_books
BookInfo[] missing_books
BookDisplacement[] misplaced_books
  - book_id
  - expected_zone
  - detected_zone

float32 total_scan_time
int32 shelves_scanned

Feedback:
string status               # moving | scanning_shelf
float32 progress
int32 current_shelf
int32 books_at_current_shelf
float32 elapsed_time

状态码:
  SUCCESS: 0, ZONE_EMPTY: 1, PARTIAL_SCAN: 2
  CANCELLED: 3, ERROR: 4
```

### D5.5 接口版本管理

```yaml
版本号: libbot_msgs v1.0.0 (Phase 1)

版本兼容性规则:
- 保持接口名称不变
- 消息格式只增不减
- 新增字段必须设置默认值

未来升级:
- 大改 → libbot_msgs_2
- 小改 → 保持现有名称，添加可选字段
```

---

## D1-D5 功能实现优先级

### Phase 1 必须实现（P0）
- ✓ D1: UI基础界面（找书、状态显示、日志）
- ✓ D2: 基础错误处理（L1/L2恢复、任务取消）
- ✓ D3: 基础日志（ROS2日志 + SQLite业务日志）
- ✓ D4: 基础配置（library_config.yaml + 动态参数）
- ✓ D5: 核心API（/find_book Action、/get_book_info Service）

### Phase 1 推荐实现（P1）
- ⭕ D1: UI高级功能（统计、暂停/取消按钮）
- ⭕ D2: 错误码定义、恢复决策引擎
- ⭕ D3: 监控指标统计
- ⭕ D4: 多环境配置切换
- ⭕ D5: 完整API（/perform_inventory Action）

### Phase 2+ 可选（P2）
- ❌ D1: UI深色主题、日志搜索
- ❌ D2: L3恢复、节点心跳监控
- ❌ D3: 独立监控节点、离线日志分析
- ❌ D4: 参数热更新、配置界面
- ❌ D5: API版本2.0

---

**文档维护：** 本附录应在功能细节变更时更新

**最后更新：** 2026-4-7

---
- 2026-4-7：新增性能与优化决策章节（图书50-100本、书架24个、图书禁用碰撞、3-4个动态障碍物）

---

## 附录C：性能与优化决策（高层设计）

### C.1 图书数量与性能分层

| 测试级别 | 图书数量 | 启动时间 | 用途说明 |
|---------|----------|----------|----------|
| Level 1 (开发测试) | 10-20本 | <5秒 | 快速迭代，基础功能验证 |
| Level 2 (默认配置) | **50-100本** | ~15秒 | 完整功能测试（推荐） |
| Level 3 (场景测试) | 200-300本 | ~30秒 | 复杂场景验证 |
| Level 4 (压力测试) | 500本（上限） | ~45秒 | 性能基准测试 |

**决策理由：** 默认50-100本在功能完整性和启动速度间取得最佳平衡

### C.2 书架数量配置

| 配置类型 | 数量 | 布局 | 用途 |
|---------|------|------|------|
| 默认配置 | **24个** | 4排 × 6个（A1-D6） | 日常开发和测试 |
| 扩展配置 | 60个 | 6排 × 10个（A1-F10） | 压力测试（手动启用） |

**决策理由：** 24个书架可容纳50-100本书，且启动时间可控

### C.3 性能优化关键策略

| 优化项 | 原方案 | 新方案 | 性能提升 |
|--------|--------|--------|----------|
| **图书碰撞检测** | 启用完整碰撞 | **禁用**（仅视觉） | 减少90%物理计算 |
| **模型加载** | 独立SDF文件 | **参数化实例化** | 内存占用减少60% |
| **书架模型** | 独立文件 | **参数化模板** | 加载时间减少50% |
| **动态障碍物** | 未指定 | **3-4个**（精确控制） | CPU负载可控 |

**核心原则：** 图书仅用于视觉显示和RFID检测，不参与物理碰撞，因为图书在书架上不会阻挡机器人路径。

### C.4 动态障碍物配置（最终方案）

**总数量：3-4个障碍物**

1. **移动读者（1个）**
   - 类型：Gazebo Actor
   - 行为：完整路径循环（书架 → 阅览 → 归还）
   - 周期：90秒
   - 速度：0.3-0.5 m/s

2. **静止读者（1个）**
   - 类型：Gazebo Actor（静态）
   - 行为：站在书架前浏览
   - 持续时间：60-120秒
   - 用途：测试静态障碍物避障

3. **可移动椅子（1-2个）**
   - 类型：静态模型 + 随机运动插件
   - 行为：每30秒随机偏移0-0.5米
   - 用途：测试动态障碍物代价地图更新

**性能影响：**
- 每个Actor增加CPU负载 ~2-3%
- 总负载：3-4个障碍物 ≈ 8-12% CPU
- 在可接受范围内

### C.5 性能目标

| 指标 | 目标值 | 实测方法 |
|------|--------|----------|
| 启动时间 | <15秒 | 从ros2 launch到Gazebo Ready |
| 运行帧率 | >30 FPS | Gazebo stats实时监控 |
| 内存占用 | <2GB | top / htop监控 |
| 导航响应 | <2秒 | 从目标提交到机器人移动 |

