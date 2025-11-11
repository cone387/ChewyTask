"""
ChewyTask - 轻量级任务调度系统

Celery 的轻量替代方案 —— 保留 Celery 的直观语法，剥离分布式复杂性，
适合单机环境快速落地。

Example:
    >>> from chewy_task import ChewyTask, IntervalSchedule
    >>> 
    >>> app = ChewyTask()
    >>> 
    >>> @app.task(schedule=IntervalSchedule(interval=5))
    >>> def hello():
    >>>     print("Hello, ChewyTask!")
    >>> 
    >>> app.start()
"""

__version__ = "0.1.0"

from .app import ChewyTask
from .task import Task, TaskEntry
from .schedules import IntervalSchedule
from .executor import ThreadExecutor, ProcessExecutor

__all__ = [
    "ChewyTask",
    "Task",
    "TaskEntry",
    "IntervalSchedule",
    "ThreadExecutor",
    "ProcessExecutor",
]
