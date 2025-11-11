# ChewyTask

Celery 的轻量替代方案 —— 保留 Celery 的直观语法，剥离分布式复杂性，同时整合 APScheduler 的灵活调度能力，适合单机环境快速落地。

## 核心优势

- **Celery 式易用性**：沿用`@task`装饰器、`delay()`延迟执行等熟悉语法，开发者零学习成本，迁移只需微调。
- **轻量无依赖**：无需 RabbitMQ/Redis 等中间件，单文件部署，依赖极简，启动秒级响应。
- **单机多进程**：内置进程池，自动利用多核资源，兼顾并行效率与部署简洁性。
- **灵活调度**：支持 cron 定时、固定间隔、延迟任务等，调度能力对标 APScheduler。

适用场景：从脚本定时任务到中小应用异步处理，ChewyTask 让你用熟悉的方式，轻松搞定单机任务调度。

## 快速开始

### 安装

```bash
# 使用 uv 安装
uv add chewy-task

# 或使用 pip
pip install chewy-task
```

### 基础使用

```python
from chewy_task import ChewyTask, IntervalSchedule

app = ChewyTask()

# 定时任务：每 5 秒执行一次
@app.task(schedule=IntervalSchedule(interval=5))
def hello():
    print("Hello, ChewyTask!")

# 异步任务
@app.task
def process_data(data):
    print(f"Processing: {data}")
    return f"Done: {data}"

if __name__ == '__main__':
    # 启动调度器（阻塞模式）
    app.start()
    
    # 或后台模式
    # app.start(auto=True, threading=True)
    # process_data.delay("my_data")  # 异步调用
```

## 功能特性

### 1. 多种启动模式

```python
# 阻塞模式（默认）
app.start()  # 主线程被阻塞，直到 Ctrl+C

# 后台线程模式
app.start(auto=True, threading=True)  # 后台运行，主线程继续

# 后台进程模式（适合 CPU 密集型任务）
app.start(auto=True, threading=False)
```

### 2. 装饰器语法

```python
# @task 装饰器：支持定时 + 异步
@app.task(schedule=IntervalSchedule(interval=10))
def scheduled_job():
    print("Scheduled execution")

@app.task  # 不带括号也可以！
def async_job():
    print("Async execution")

# @schedule 装饰器：仅用于定时任务
@app.schedule(schedule=IntervalSchedule(interval=60))
def cleanup():
    print("Cleanup job")
```

### 3. delay() 异步调用

```python
@app.task
def send_email(to: str, subject: str):
    print(f"Sending email to {to}")
    return "Email sent"

# 异步提交任务
future = send_email.delay(to="user@example.com", subject="Hello")

# 获取结果（可选）
result = future.result(timeout=10)
```

## 项目结构

```
ChewyTask/
├── chewy_task/          # 主包目录
│   ├── __init__.py      # 公共接口
│   ├── app.py           # ChewyTask 主类
│   ├── task.py          # Task 定义
│   ├── scheduler.py     # 调度器
│   ├── executor.py      # 执行器抽象
│   └── schedules.py     # 调度规则
├── examples/            # 使用示例
│   ├── 01_basic_scheduled.py
│   ├── 02_background_mode.py
│   ├── 03_schedule_decorator.py
│   └── 04_process_mode.py
├── pyproject.toml       # 项目配置
└── README.md
```

## API 参考

### ChewyTask

主应用类，管理任务注册和调度。

**初始化参数：**
- `max_workers` (int, optional): 最大工作线程/进程数
- `task_timeout` (float, optional): 任务超时时间（秒）
- `custom_logger` (Logger, optional): 自定义日志对象

**方法：**
- `task(func=None, *, schedule=None, name=None)`: 任务装饰器
- `schedule(schedule, name=None)`: 定时任务装饰器
- `start(auto=False, threading=True)`: 启动调度器
- `shutdown()`: 关闭调度器

### IntervalSchedule

固定间隔调度规则。

```python
schedule = IntervalSchedule(interval=5)  # 5 秒间隔
```

## 测试

```bash
# 运行基础功能测试
uv run test_basic.py

# 运行高级功能测试
uv run test_advanced.py

# 运行示例
uv run examples/01_basic_scheduled.py
```

## 开发路线图

### v0.1.0 (当前版本)

- ✅ 基础任务装饰器 (@app.task)
- ✅ 固定间隔调度 (IntervalSchedule)
- ✅ 延迟执行 (task.delay)
- ✅ 线程/进程模式切换
- ✅ 自动/手动启动
- ✅ 独立调度装饰器 (@app.schedule)

### v0.2.0 (规划中)

- ⚡ Cron 表达式支持
- ⚡ 任务结果查询
- ⚡ 任务重试机制
- ⚡ 任务链和依赖

## 注意事项

1. **进程模式限制**：任务函数及参数必须可序列化（pickle）
2. **GIL 影响**：线程模式适合 I/O 密集型，进程模式适合 CPU 密集型
3. **调度精度**：基于轮询，最小精度约 100ms，不适合毫秒级需求

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
