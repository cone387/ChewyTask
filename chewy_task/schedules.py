"""
调度规则模块

定义任务的调度规则，包括固定间隔调度等。
"""


class IntervalSchedule:
    """固定间隔调度规则
    
    按照固定的时间间隔执行任务。
    
    Args:
        interval: 时间间隔（秒）
    
    Example:
        >>> schedule = IntervalSchedule(interval=5)  # 每5秒执行一次
    """
    
    def __init__(self, interval: float):
        """初始化间隔调度规则
        
        Args:
            interval: 时间间隔（秒），必须大于0
            
        Raises:
            ValueError: 当 interval 小于等于0时
        """
        if interval <= 0:
            raise ValueError(f"Interval must be greater than 0, got {interval}")
        self.interval = interval
    
    def __repr__(self):
        return f"IntervalSchedule(interval={self.interval})"
