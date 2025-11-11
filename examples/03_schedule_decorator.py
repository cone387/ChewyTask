"""
示例 3：使用 @schedule 装饰器

演示使用 @schedule 装饰器定义纯定时任务。
"""

import time
from chewy_task import ChewyTask, IntervalSchedule

app = ChewyTask()


# 使用 @schedule 装饰器，仅用于定时执行，不能 delay
@app.schedule(schedule=IntervalSchedule(interval=3))
def cleanup_job():
    print(f"[{time.strftime('%H:%M:%S')}] 执行清理任务")


@app.schedule(schedule=IntervalSchedule(interval=5))
def health_check():
    print(f"[{time.strftime('%H:%M:%S')}] 执行健康检查")


if __name__ == '__main__':
    print("启动定时任务调度器...")
    print("按 Ctrl+C 停止\n")
    
    # 阻塞模式运行
    app.start()
