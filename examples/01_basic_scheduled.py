"""
示例 1：基础定时任务（阻塞模式）

演示最简单的定时任务用法。
"""

from chewy_task import ChewyTask, IntervalSchedule

# 创建应用实例
app = ChewyTask()


# 使用装饰器注册定时任务
@app.task(schedule=IntervalSchedule(interval=2))
def task1():
    print("[Task1] 每2秒执行一次")


@app.task(schedule=IntervalSchedule(interval=5))
def task2():
    print("[Task2] 每5秒执行一次")


if __name__ == '__main__':
    print("启动调度器（阻塞模式）...")
    print("按 Ctrl+C 停止")
    
    # 阻塞模式运行（默认 auto=False）
    app.start()
