"""
示例 2：后台模式 + delay 异步调用

演示后台模式启动调度器，以及使用 delay() 方法异步执行任务。
"""

import time
from chewy_task import ChewyTask, IntervalSchedule

app = ChewyTask()


# 定时任务
@app.task(schedule=IntervalSchedule(interval=3))
def scheduled_task():
    print(f"[{time.strftime('%H:%M:%S')}] 定时任务执行")


# 不带 schedule 的任务，仅供 delay 调用
@app.task
def async_task(name: str, count: int):
    print(f"[{time.strftime('%H:%M:%S')}] 异步任务: {name} - 计数 {count}")
    return f"完成: {name}"


if __name__ == '__main__':
    print("启动后台调度器...")
    
    # 后台线程模式启动
    app.start(auto=True, threading=True)
    
    print("调度器已在后台运行，主线程继续执行\n")
    
    # 主线程可以继续做其他事情
    for i in range(5):
        time.sleep(2)
        
        # 异步提交任务
        future = async_task.delay(name=f"任务{i+1}", count=i+1)
        print(f"[主线程] 提交了异步任务 {i+1}")
    
    print("\n等待任务完成...")
    time.sleep(5)
    
    print("关闭调度器")
    app.shutdown()
