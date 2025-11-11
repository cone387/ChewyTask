"""
基础功能测试脚本

测试定时任务的基本功能。
"""

import time
import signal
import sys
from chewy_task import ChewyTask, IntervalSchedule

# 创建应用实例
app = ChewyTask()

# 计数器
task1_count = 0
task2_count = 0


@app.task(schedule=IntervalSchedule(interval=2))
def task1():
    global task1_count
    task1_count += 1
    print(f"[Task1] 执行次数: {task1_count}")


@app.task(schedule=IntervalSchedule(interval=3))
def task2():
    global task2_count
    task2_count += 1
    print(f"[Task2] 执行次数: {task2_count}")


def signal_handler(sig, frame):
    """处理 Ctrl+C 信号"""
    print(f"\n\n测试结束:")
    print(f"  Task1 执行了 {task1_count} 次（预期约 5 次）")
    print(f"  Task2 执行了 {task2_count} 次（预期约 3 次）")
    
    if task1_count >= 4 and task2_count >= 2:
        print("\n✓ 基础功能测试通过！")
    else:
        print("\n✗ 测试未达到预期")
    
    app.shutdown()
    sys.exit(0)


if __name__ == '__main__':
    # 设置信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGALRM, signal_handler)
    
    # 设置 10 秒后自动退出
    signal.alarm(10)
    
    print("启动基础功能测试...")
    print("将运行 10 秒，或按 Ctrl+C 提前结束\n")
    
    # 阻塞模式运行
    app.start()
