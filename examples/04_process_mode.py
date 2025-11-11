"""
示例 4：进程模式

演示使用进程池执行任务，适合 CPU 密集型任务。
注意：进程模式下任务函数必须可序列化（pickle）。
"""

import time
import os
from chewy_task import ChewyTask, IntervalSchedule


# CPU 密集型任务示例
def calculate_fibonacci(n):
    """计算斐波那契数"""
    if n <= 1:
        return n
    return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)


app = ChewyTask()


@app.task
def cpu_task(n: int):
    pid = os.getpid()
    print(f"[进程 {pid}] 开始计算 fibonacci({n})")
    result = calculate_fibonacci(n)
    print(f"[进程 {pid}] fibonacci({n}) = {result}")
    return result


@app.task(schedule=IntervalSchedule(interval=5))
def monitor_task():
    print(f"[{time.strftime('%H:%M:%S')}] 监控任务运行中（主进程）")


if __name__ == '__main__':
    print(f"主进程 PID: {os.getpid()}\n")
    
    # 使用进程模式启动（后台）
    app.start(auto=True, threading=False)
    
    print("调度器已在后台进程中运行\n")
    
    # 提交 CPU 密集型任务
    for i in range(30, 36):
        future = cpu_task.delay(n=i)
        print(f"提交任务: fibonacci({i})")
        time.sleep(1)
    
    print("\n等待所有任务完成...")
    time.sleep(15)
    
    print("\n关闭调度器")
    app.shutdown()
