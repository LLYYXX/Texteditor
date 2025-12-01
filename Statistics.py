"""
Lab2新增: 统计模块
使用观察者模式(Observer Pattern)跟踪文件编辑时长
使用装饰器模式(Decorator Pattern)为文件名添加时长信息
"""
import time


class StatisticsManager:
    """统计管理器 (Observer)"""
    def __init__(self):
        self._active_file_start_time = {}
        self._total_editing_time = {}
        self._current_active_file = None
    
    def start_timing(self, filepath):
        """开始计时"""
        if self._current_active_file and self._current_active_file != filepath:
            self.stop_timing(self._current_active_file)
        self._active_file_start_time[filepath] = time.time()
        self._current_active_file = filepath
        if filepath not in self._total_editing_time:
            self._total_editing_time[filepath] = 0
    
    def stop_timing(self, filepath):
        """停止计时"""
        if filepath in self._active_file_start_time:
            start_time = self._active_file_start_time[filepath]
            elapsed = time.time() - start_time
            if filepath in self._total_editing_time:
                self._total_editing_time[filepath] += elapsed
            else:
                self._total_editing_time[filepath] = elapsed
            del self._active_file_start_time[filepath]
        if self._current_active_file == filepath:
            self._current_active_file = None
    
    def reset_timing(self, filepath):
        """重置时长"""
        if filepath in self._total_editing_time:
            del self._total_editing_time[filepath]
        if filepath in self._active_file_start_time:
            del self._active_file_start_time[filepath]
    
    def get_editing_time(self, filepath):
        """获取文件的编辑时长(秒)"""
        total = self._total_editing_time.get(filepath, 0)
        if filepath in self._active_file_start_time:
            start_time = self._active_file_start_time[filepath]
            total += time.time() - start_time
        return total
    
    def format_time(self, seconds):
        """格式化时长为可读格式"""
        if seconds < 0:
            return "0秒"
        seconds = int(seconds)
        if seconds < 60:
            return f"{seconds}秒"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}分钟"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            if minutes > 0:
                return f"{hours}小时{minutes}分钟"
            else:
                return f"{hours}小时"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            if hours > 0:
                return f"{days}天{hours}小时"
            else:
                return f"{days}天"
    
    def get_formatted_time(self, filepath):
        """获取格式化后的编辑时长字符串"""
        seconds = self.get_editing_time(filepath)
        return self.format_time(seconds)


class TimeDecorator:
    """时间装饰器 (Decorator Pattern)"""
    def __init__(self, statistics_manager):
        self.stats = statistics_manager
    
    def decorate(self, filepath):
        """装饰文件名：添加时长"""
        time_str = self.stats.get_formatted_time(filepath)
        return f"{filepath} ({time_str})"
    
    def decorate_with_status(self, filepath, is_active=False, is_modified=False):
        """装饰文件名：添加状态和时长"""
        active_marker = "* " if is_active else "  "
        modified_marker = " [modified]" if is_modified else ""
        time_str = self.stats.get_formatted_time(filepath)
        return f"{active_marker}{filepath}{modified_marker} ({time_str})"


