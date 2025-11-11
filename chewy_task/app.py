"""
ChewyTask 应用主模块

提供 ChewyTask 应用类，实现 @task 和 @schedule 装饰器。
"""

import logging
from typing import Callable, Dict, Optional, Any
from concurrent.futures import Future

from .task import Task, TaskEntry
from .scheduler import Scheduler
from .executor import create_executor, BaseExecutor

# 配置默认日志
logger = logging.getLogger("ChewyTask")
if not logger.handlers:
    formatter = logging.Formatter("[%(asctime)s][%(levelname)s][%(threadName)s]%(name)s:%(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class ChewyTask:
    """ChewyTask 应用类
    
    类 Celery 的轻量级任务调度系统，支持定时任务和异步任务。
    
    Example:
        >>> app = ChewyTask()
        >>> @app.task(schedule=IntervalSchedule(interval=5))
        >>> def hello():
        >>>     print("Hello, ChewyTask!")
        >>> app.start()
    """
    
    def __init__(
        self,
        max_workers: Optional[int] = None,
        task_timeout: Optional[float] = None,
        custom_logger: Optional[logging.Logger] = None
    ):
        """初始化 ChewyTask 应用
        
        Args:
            max_workers: 执行器最大工作线程/进程数，None 表示自动选择
            task_timeout: 单个任务最大执行时间（秒），暂未实现
            custom_logger: 自定义日志对象
        """
        self.max_workers = max_workers
        self.task_timeout = task_timeout
        self.logger = custom_logger or logger
        
        # 任务注册表
        self._tasks: Dict[str, Task] = {}
        
        # 执行器和调度器（延迟初始化）
        self._executor: Optional[BaseExecutor] = None
        self._scheduler: Optional[Scheduler] = None
        self._started = False
    
    def task(self, func: Optional[Callable] = None, *, schedule=None, name: Optional[str] = None, **options):
        """任务装饰器
        
        支持两种用法：
        1. @app.task  （不带括号）
        2. @app.task(schedule=..., name=...)  （带参数）
        
        Args:
            func: 被装饰的函数
            schedule: 调度规则对象（IntervalSchedule 等）
            name: 任务名称，默认使用函数名
            **options: 其他选项（预留）
            
        Returns:
            装饰后的任务函数（附加了 delay 方法）
        """
        def decorator(f: Callable) -> Task:
            # 创建 Task 对象
            task_name = name or f.__name__
            task = Task(func=f, name=task_name, app=self)
            
            # 注册任务
            self._tasks[task.name] = task
            logger.info(f"Task registered: {task.name}")
            
            # 如果提供了调度规则，添加到定时任务队列
            if schedule is not None:
                self._ensure_scheduler_initialized()
                if self._scheduler:
                    task_entry = TaskEntry(task, schedule)
                    self._scheduler.add_scheduled_task(task_entry)
            
            return task
        
        # 支持不带括号的用法：@app.task
        if func is not None:
            return decorator(func)
        
        # 支持带括号的用法：@app.task(...)
        return decorator
    
    def schedule(self, schedule, name: Optional[str] = None):
        """调度装饰器
        
        专门用于定义定时执行的函数，不支持 delay 调用。
        
        Args:
            schedule: 调度规则对象（必填）
            name: 任务名称，默认使用函数名
            
        Returns:
            装饰后的函数
        """
        if schedule is None:
            raise ValueError("schedule is required for @app.schedule decorator")
        
        def decorator(func: Callable) -> Callable:
            # 创建 Task 对象（不绑定 app，因此无法 delay）
            task_name = name or func.__name__
            task = Task(func=func, name=task_name, app=None)
            
            # 注册任务
            self._tasks[task.name] = task
            logger.info(f"Scheduled function registered: {task.name}")
            
            # 添加到定时任务队列
            self._ensure_scheduler_initialized()
            if self._scheduler:
                task_entry = TaskEntry(task, schedule)
                self._scheduler.add_scheduled_task(task_entry)
            
            # 返回原函数（不是 Task 对象，因此没有 delay 方法）
            return func
        
        return decorator
    
    def submit_task(self, task: Task, *args, **kwargs) -> Future:
        """提交即时任务到执行器
        
        供 Task.delay() 方法调用。
        
        Args:
            task: Task 对象
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            Future 对象
        """
        self._ensure_scheduler_initialized()
        if self._scheduler:
            return self._scheduler.submit_instant_task(task, *args, **kwargs)
        raise RuntimeError("Scheduler not initialized")
    
    def start(self, auto: bool = False, threading: bool = True):
        """启动调度器
        
        Args:
            auto: 是否自动启动（后台模式），False 表示阻塞运行
            threading: True 为线程模式，False 为进程模式
        """
        if self._started:
            logger.warning("Scheduler already started")
            return
        
        # 初始化执行器和调度器
        self._ensure_scheduler_initialized(threading=threading)
        
        if not self._scheduler:
            raise RuntimeError("Failed to initialize scheduler")
        
        self._started = True
        
        if auto:
            # 后台模式
            self._scheduler.start_background(use_thread=threading)
            logger.info(f"ChewyTask started in background ({'thread' if threading else 'process'} mode)")
        else:
            # 阻塞模式
            logger.info("ChewyTask starting in blocking mode...")
            self._scheduler.run()
    
    def shutdown(self):
        """关闭调度器"""
        if self._scheduler:
            self._scheduler.shutdown()
        self._started = False
    
    def _ensure_scheduler_initialized(self, threading: bool = True):
        """确保调度器已初始化
        
        Args:
            threading: True 为线程模式，False 为进程模式
        """
        if self._scheduler is None:
            # 创建执行器
            self._executor = create_executor(
                threading=threading,
                max_workers=self.max_workers
            )
            
            # 创建调度器
            self._scheduler = Scheduler(executor=self._executor)
            logger.debug("Scheduler initialized")
