# CLI非交互执行与故障分类

## 适用范围
适用于归因分析CLI、科学计算CLI等需要非交互式执行并需要精确故障诊断的场景。覆盖命令参数解析、进程生命周期管理、超时控制、退出码分类与标准错误处理。

## 输入
- 命令行参数序列或字符串
- 可选：标准输入数据（通过stdin管道或input参数）
- 环境变量配置
- 超时时间设置（秒）

## 输出
- CompletedProcess对象，包含returncode、stdout、stderr
- 异常信息（如发生故障）

## 流程节点

1. **进程创建** → 使用subprocess.run()或Popen()启动子进程
2. **输入/输出管道连接** → 配置stdin/stdout/stderr的管道重定向
3. **超时等待** → 使用timeout参数或communicate()等待进程完成
4. **退出码检查** → 根据returncode判断执行结果
5. **异常处理** → 捕获并分类异常类型

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| returncode | 0 | [D1] | 进程成功退出 |
| returncode | 负值-N | [D1] | 进程被信号N终止（仅POSIX） |
| returncode | 正值 | [D1] | 进程异常退出，具体含义由程序定义 |

## 故障分类

### 异常类型
| 异常 | 触发条件 | 诊断动作 |
|------|----------|----------|
| TimeoutExpired | 进程超过timeout未完成 | 检查进程是否挂起，考虑增大超时或终止进程 |
| CalledProcessError | check=True时进程返回非零退出码 | 检查stdout/stderr获取具体错误信息 |
| OSError | 进程无法启动（如文件不存在） | 检查可执行文件路径和权限 |
| ValueError | 参数无效 | 检查Popen构造参数 |

### 退出码解读
- **0**: 正常完成，无错误
- **1-125**: 程序定义的错误码（具体含义需查阅程序文档）
- **126**: 命令不可执行（权限问题）
- **127**: 命令未找到
- **128+N**: 进程被信号N终止（如129=SIGHUP, 137=SIGKILL）

## 边界与分流
- 超时发生时：子进程不会自动终止，需手动调用proc.kill()清理
- stdout=PIPE时：避免使用wait()，应使用communicate()避免死锁
- shell=True时：需注意shell注入风险，建议使用shlex.quote()转义参数

## 质量检查
- 检查returncode是否符合预期（0=成功或程序定义的错误码）
- 验证stdout/stderr捕获是否完整
- 超时后必须调用kill()确保进程清理

## 回退策略
- 若subprocess.run()失败，可尝试更低级的Popen()接口
- 若管道死锁，使用communicate()替代单独的read/write操作
- 考虑使用asyncio.create_subprocess_exec()处理高并发场景

## 资源召回建议
- 当需要执行外部CLI工具并需要诊断执行结果时召回本卡片
- 配套卡片：JSON Schema报告交付契约（用于验证CLI输出格式）

## 补充证据（开源权威文档）
[D1] Python subprocess文档: subprocess - Subprocess management, Python Software Foundation, Python 3.14, https://docs.python.org/3/library/subprocess.html (accessed 2026-09-21)
[D2] GNU C Library manual - Exit Status, GNU Project, glibc 2.44, https://www.gnu.org/software/libc/manual/html_node/Exit-Status.html (accessed 2026-09-21)
