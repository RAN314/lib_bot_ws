# RFID扫描结果消息
# 从四个方向的RFID天线发布扫描结果

std_msgs/Header header  # 时间戳和坐标系

string antenna_position        # 天线位置: front, back, left, right, stop
string[] detected_book_ids     # 检测到的图书ID列表
float32[] signal_strengths     # 对应信号强度 (0-1)
float32 detection_range        # 检测范围（米）
bool is_moving                 # 机器人是否正在移动
