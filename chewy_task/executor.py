"""
执行器模块

提供任务执行器的抽象层，支持线程模式和进程模式。
"""

import logging
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Future, Executor
from typing import Callable, Any, Optional

logger = logging.getLogger("ChewyTask")


class BaseExecutor(ABC):
    """执行器基类
    
    定义执行器的接口规范，屏蔽线程/进程差异。
    """
    
    def __init__(self, max_workers: Optional[int] = None):
        """初始化执行器
        
        Args:
            max_workers: 最大工作线程/进程数，None 表示自动选择
        """
        self.max_workers = max_workers
        self._executor: Optional[Executor] = None
    
    @abstractmethod
    def _create_executor(self) -> Executor:
        """创建底层执行器（子类实现）"""
        pass
    
    def start(self):
        """启动执行器"""
        if self._executor is None:
            self._executor = self._create_executor()
            logger.info(f"{self.__class__.__name__} started with {self.max_workers or 'auto'} workers")
    
    def submit(self, fn: Callable, *args, **kwargs) -> Future:
        """提交任务到执行器
        
        Args:
            fn: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            Future 对象，用于获取任务执行结果
        """
        if self._executor is None:
            self.start()
        
        try:
            future = self._executor.submit(fn, *args, **kwargs)
            return future
        except Exception as e:
            logger.error(f"Failed to submit task: {e}", exc_info=True)
            raise
    
    def shutdown(self, wait: bool = True, timeout: Optional[float] = None):
        """关闭执行器
        
        Args:
            wait: 是否等待正在运行的任务完成
            timeout: 等待超时时间（秒），None 表示无限等待
        """
        if self._executor is not None:
            logger.info(f"Shutting down {self.__class__.__name__}...")
            try:
                # Python 3.9+ 支持 cancel_futures 参数
                self._executor.shutdown(wait=wait)
            except Exception as e:
                logger.error(f"Error during executor shutdown: {e}", exc_info=True)
            finally:
                self._executor = None


class ThreadExecutor(BaseExecutor):
    """线程执行器
    
    使用线程池执行任务，适合 I/O 密集型任务。
    共享主进程内存空间，数据传递无需序列化。
    """
    
    def _create_executor(self):
        """创建线程池执行器"""
        return ThreadPoolExecutor(max_workers=self.max_workers)


class ProcessExecutor(BaseExecutor):
    """进程执行器
    
    使用进程池执行任务，适合 CPU 密集型任务。
    进程间隔离，避免 GIL 限制，但任务和参数必须可序列化。
    """
    
    def _create_executor(self):
        """创建进程池执行器"""
        return ProcessPoolExecutor(max_workers=self.max_workers)


def create_executor(threading: bool = True, max_workers: Optional[int] = None) -> BaseExecutor:
    """工厂函数：根据模式创建执行器
    
    Args:
        threading: True 为线程模式，False 为进程模式
        max_workers: 最大工作线程/进程数
        
    Returns:
        执行器实例
    """
    if threading:
        return ThreadExecutor(max_workers=max_workers)
    else:
        return ProcessExecutor(max_workers=max_workers)
