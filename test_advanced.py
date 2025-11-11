"""
高级功能测试脚本

测试后台模式、delay 方法和进程模式。
"""

import time
from chewy_task import ChewyTask, IntervalSchedule

app = ChewyTask()

# 计数器
scheduled_count = 0
delay_count = 0


@app.task(schedule=IntervalSchedule(interval=2))
def scheduled_task():
    global scheduled_count
    scheduled_count += 1
    print(f"[定时任务] 执行次数: {scheduled_count}")


@app.task
def delay_task(task_id: int):
    global delay_count
    delay_count += 1
    print(f"[异步任务 {task_id}] 执行完成，总执行次数: {delay_count}")
    return f"Task {task_id} done"


if __name__ == '__main__':
    print("=== 测试 1: 后台线程模式 + delay 方法 ===\n")
    
    # 启动后台调度器
    app.start(auto=True, threading=True)
    print("✓ 后台调度器已启动\n")
    
    # 主线程继续执行
    time.sleep(1)
    
    # 提交异步任务
    print("提交 5 个异步任务...")
    futures = []
    for i in range(5):
        future = delay_task.delay(task_id=i+1)
        futures.append(future)
        print(f"  ✓ 提交任务 {i+1}")
        time.sleep(0.5)
    
    # 等待定时任务执行几次
    print("\n等待任务执行...")
    time.sleep(6)
    
    print(f"\n=== 测试结果 ===")
    print(f"定时任务执行次数: {scheduled_count} (预期 2-3 次)")
    print(f"异步任务执行次数: {delay_count} (预期 5 次)")
    
    if scheduled_count >= 2 and delay_count == 5:
        print("\n✓ 后台模式和 delay 功能测试通过！")
    else:
        print("\n✗ 测试未达到预期")
    
    # 关闭调度器
    print("\n关闭调度器...")
    app.shutdown()
    print("✓ 测试完成")
