"""
任务模块

定义 Task 和 TaskEntry，实现任务的基本结构和调度入口。
"""

import time
import logging
from typing import Callable, Any, Optional
from uuid import uuid4

logger = logging.getLogger("ChewyTask")


class Task:
    """任务对象
    
    封装一个可执行的任务函数，提供 delay() 方法用于异步执行。
    
    Attributes:
        func: 原始任务函数
        name: 任务名称
        app: 所属的 ChewyTask 应用实例
    """
    
    def __init__(self, func: Callable, name: Optional[str] = None, app=None):
        """初始化任务对象
        
        Args:
            func: 任务函数
            name: 任务名称，默认使用函数名
            app: 所属的应用实例，用于 delay 调用
        """
        self.func = func
        self.name = name or func.__name__
        self.app = app
        
        # 保留原函数的属性
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
        self.__module__ = func.__module__
        self.__wrapped__ = func
    
    def run(self, *args, **kwargs) -> Any:
        """执行任务函数
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            任务函数的返回值
        """
        try:
            logger.debug(f"Running task: {self.name}")
            result = self.func(*args, **kwargs)
            logger.debug(f"Task {self.name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Task {self.name} failed with error: {e}", exc_info=True)
            raise
    
    def delay(self, *args, **kwargs):
        """异步执行任务
        
        将任务提交到即时任务队列，由调度器异步执行。
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            Future 对象，可用于获取任务执行结果
            
        Raises:
            RuntimeError: 当任务未关联到应用实例时
        """
        if self.app is None:
            raise RuntimeError(
                f"Task '{self.name}' is not bound to any ChewyTask application. "
                f"Make sure to use @app.task decorator."
            )
        return self.app.submit_task(self, *args, **kwargs)
    
    def __call__(self, *args, **kwargs):
        """直接调用任务函数"""
        return self.func(*args, **kwargs)
    
    def __repr__(self):
        return f"<Task: {self.name}>"


class TaskEntry:
    """任务调度入口
    
    包含任务的调度信息，用于定时任务队列。
    
    Attributes:
        id: 任务入口的唯一标识
        task: 关联的 Task 对象
        schedule: 调度规则（IntervalSchedule 等）
        args: 任务参数（位置参数）
        kwargs: 任务参数（关键字参数）
        last_run_at: 上次执行时间（时间戳）
    """
    
    def __init__(self, task: Task, schedule, args=None, kwargs=None):
        """初始化任务调度入口
        
        Args:
            task: Task 对象
            schedule: 调度规则对象
            args: 任务的位置参数
            kwargs: 任务的关键字参数
        """
        self.id = str(uuid4())
        self.task = task
        self.schedule = schedule
        self.args = args or []
        self.kwargs = kwargs or {}
        self.last_run_at: Optional[float] = None
    
    def is_due(self) -> tuple[bool, float]:
        """检查任务是否到期需要执行
        
        Returns:
            (是否到期, 距离下次执行的剩余时间)
        """
        now = time.time()
        
        # 首次运行
        if self.last_run_at is None:
            return True, self.schedule.interval
        
        # 计算下次运行时间
        next_run = self.last_run_at + self.schedule.interval
        remaining = next_run - now
        
        if remaining <= 0:
            return True, self.schedule.interval
        
        return False, remaining
    
    def __repr__(self):
        return f"<TaskEntry: {self.task.name} - {self.schedule}>"
