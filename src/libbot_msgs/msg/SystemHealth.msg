# 系统健康状态消息
# 发布到/system/health Topic

std_msgs/Header header       # 时间戳
string overall_health        # 整体健康状态 (HEALTHY, WARNING, ERROR, CRITICAL)

# 健康指标数据 (JSON格式)
string health_metrics_json   # 健康指标的JSON格式数据

# 活动告警
string[] active_warnings     # 当前警告列表
string[] active_errors       # 当前错误列表

# 机器人状态
geometry_msgs/Pose robot_pose  # 机器人位置
int32 active_tasks              # 当前活动任务数