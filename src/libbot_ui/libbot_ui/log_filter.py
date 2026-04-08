#!/usr/bin/env python3


class LogFilter:
    """日志过滤器 - 支持多种过滤条件"""

    def __init__(self):
        self.level_filter = "ALL"
        self.search_filter = ""
        self.time_range = None

    def matches(self, log_entry):
        """检查日志条目是否匹配过滤条件

        Args:
            log_entry: 日志条目字典，包含timestamp, level, message等字段

        Returns:
            bool: 是否匹配过滤条件
        """
        # 级别过滤
        if self.level_filter != "ALL" and log_entry["level"] != self.level_filter:
            return False

        # 搜索过滤
        if self.search_filter and self.search_filter.lower() not in log_entry["message"].lower():
            return False

        # 时间范围过滤
        if self.time_range:
            start_time, end_time = self.time_range
            if not (start_time <= log_entry["timestamp"] <= end_time):
                return False

        return True

    def set_level_filter(self, level):
        """设置级别过滤

        Args:
            level: 日志级别 (ALL/INFO/WARN/ERROR/DEBUG)
        """
        self.level_filter = level

    def set_search_filter(self, search_text):
        """设置搜索过滤

        Args:
            search_text: 搜索关键词
        """
        self.search_filter = search_text

    def set_time_range(self, start_time, end_time):
        """设置时间范围过滤

        Args:
            start_time: 开始时间戳
            end_time: 结束时间戳
        """
        self.time_range = (start_time, end_time)

    def clear_time_range(self):
        """清除时间范围过滤"""
        self.time_range = None

    def clear_all_filters(self):
        """清除所有过滤条件"""
        self.level_filter = "ALL"
        self.search_filter = ""
        self.time_range = None

    def get_active_filters(self):
        """获取当前激活的过滤条件

        Returns:
            dict: 激活的过滤条件
        """
        filters = {}
        if self.level_filter != "ALL":
            filters["level"] = self.level_filter
        if self.search_filter:
            filters["search"] = self.search_filter
        if self.time_range:
            filters["time_range"] = self.time_range
        return filters