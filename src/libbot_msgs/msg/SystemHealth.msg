# 系统健康状态消息
# 发布到/system/health Topic

std_msgs/Header header  # 时间戳

float32 navigation_health    # 导航系统健康度 (0-1)
float32 perception_health    # 感知系统健康度 (0-1)
float32 database_health      # 数据库健康度 (0-1)
float32 battery_level        # 电池电量 (0-1)

string[] active_warnings     # 当前警告列表
string[] active_errors       # 当前错误列表

# 机器人状态
geometry_msgs/Pose robot_pose  # 机器人位置

int32 active_tasks           # 当前活动任务数