"""
调度器模块

实现任务调度器，管理定时任务和即时任务队列。
"""

import time
import logging
import threading
import multiprocessing
from queue import Queue, Empty
from typing import Dict, Optional
from .task import TaskEntry, Task
from .executor import BaseExecutor

logger = logging.getLogger("ChewyTask")


class Scheduler:
    """任务调度器
    
    管理定时任务队列和即时任务队列，智能调度任务执行。
    
    Attributes:
        executor: 任务执行器
        scheduled_entries: 定时任务队列（字典）
        instant_queue: 即时任务队列
        running: 调度器运行状态
    """
    
    def __init__(self, executor: BaseExecutor):
        """初始化调度器
        
        Args:
            executor: 任务执行器
        """
        self.executor = executor
        self.scheduled_entries: Dict[str, TaskEntry] = {}
        self.instant_queue: Queue = Queue()
        self.running = False
        self._scheduler_thread: Optional[threading.Thread] = None
    
    def add_scheduled_task(self, task_entry: TaskEntry):
        """添加定时任务到调度队列
        
        Args:
            task_entry: 任务调度入口
        """
        self.scheduled_entries[task_entry.id] = task_entry
        logger.info(f"Scheduled task added: {task_entry.task.name} - {task_entry.schedule}")
    
    def submit_instant_task(self, task: Task, *args, **kwargs):
        """提交即时任务到队列
        
        Args:
            task: Task 对象
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            Future 对象
        """
        future = self.executor.submit(task.run, *args, **kwargs)
        logger.debug(f"Instant task submitted: {task.name}")
        return future
    
    def tick(self) -> float:
        """调度器的一次心跳
        
        检查定时任务是否到期，处理即时任务队列。
        
        Returns:
            下次唤醒的等待时间（秒）
        """
        next_wake = None
        
        # 检查定时任务
        for entry in self.scheduled_entries.values():
            due, remaining = entry.is_due()
            if due:
                logger.info(f"Running scheduled task: {entry.task.name}")
                try:
                    # 提交任务到执行器
                    self.executor.submit(entry.task.run, *entry.args, **entry.kwargs)
                    # 更新上次运行时间
                    entry.last_run_at = time.time()
                except Exception as e:
                    logger.error(f"Failed to submit scheduled task {entry.task.name}: {e}", exc_info=True)
            
            # 计算最近的唤醒时间
            if next_wake is None or remaining < next_wake:
                next_wake = remaining
        
        # 处理即时任务队列（非阻塞检查）
        try:
            while True:
                task, args, kwargs = self.instant_queue.get_nowait()
                logger.debug(f"Processing instant task from queue: {task.name}")
                try:
                    self.executor.submit(task.run, *args, **kwargs)
                except Exception as e:
                    logger.error(f"Failed to submit instant task {task.name}: {e}", exc_info=True)
        except Empty:
            pass
        
        # 返回休眠时间，默认最大1秒
        return min(next_wake or 1.0, 1.0)
    
    def run(self):
        """启动调度循环（阻塞模式）"""
        self.running = True
        logger.info("Scheduler started (blocking mode)")
        
        try:
            while self.running:
                sleep_time = self.tick()
                time.sleep(sleep_time)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user (KeyboardInterrupt)")
            self.running = False
        except Exception as e:
            logger.error(f"Scheduler error: {e}", exc_info=True)
            self.running = False
        finally:
            self.shutdown()
    
    def start_background(self, use_thread: bool = True):
        """在后台启动调度器
        
        Args:
            use_thread: True 使用线程，False 使用进程
        """
        if use_thread:
            self._scheduler_thread = threading.Thread(
                target=self.run,
                name="ChewyTask-Scheduler",
                daemon=True
            )
            self._scheduler_thread.start()
            logger.info("Scheduler started in background (thread mode)")
        else:
            # 进程模式
            process = multiprocessing.Process(
                target=self.run,
                name="ChewyTask-Scheduler",
                daemon=True
            )
            process.start()
            logger.info("Scheduler started in background (process mode)")
    
    def shutdown(self):
        """关闭调度器和执行器"""
        logger.info("Shutting down scheduler...")
        self.running = False
        
        # 关闭执行器
        if self.executor:
            self.executor.shutdown(wait=True)
        
        logger.info("Scheduler shutdown complete")
