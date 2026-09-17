# CLI 进程故障诊断

## 适用范围

面向命令行接口（CLI）程序在非交互模式下执行时的故障诊断场景。适用于需要通过退出码、标准错误输出、超时异常等信号判断进程失败原因，并据此修正启动配置或设计恢复策略的任务。典型触发条件包括：CLI 工具返回非零退出码、进程超时未响应、标准错误输出包含异常信息。不适用于交互式终端调试、图形界面应用或网络服务端故障诊断。

## 输入

- CLI 命令及其参数序列
- 预期退出码（通常为 0 表示成功）
- 超时阈值（秒）
- 标准输出/标准错误的捕获配置

## 输出

- 进程退出状态（returncode）
- 标准输出内容（stdout）
- 标准错误内容（stderr）
- 故障分类诊断结果

## 流程节点

1. **进程启动** → 使用 subprocess.run() 或 Popen() 启动 CLI 进程
2. **输出捕获** → 配置 stdout=PIPE、stderr=PIPE 或 capture_output=True
3. **超时监控** → 设置 timeout 参数，捕获 TimeoutExpired 异常
4. **退出码检查** → 读取 returncode 属性或捕获 CalledProcessError
5. **标准错误分析** → 解析 stderr 内容识别错误模式
6. **故障分类** → 根据退出码和错误信息归类故障类型

每步含：操作、参数、工具、质量门禁

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| returncode = 0 | 成功 | [D1] | 进程正常执行完成 |
| returncode > 0 | 应用错误 | [D1] | 进程检测到错误并主动退出 |
| returncode < 0 | 信号终止 | [D1] | 进程被信号终止（POSIX 系统） |
| timeout | 秒数 | [D1] | 超时后触发 TimeoutExpired 异常 |
| check=True | 布尔值 | [D1] | 非零退出码时抛出 CalledProcessError |

### 校准数值

以下数值来自 Python subprocess 模块标准行为，供量级校准；其他语言/平台需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 基类异常 | SubprocessError | [D1] | 所有子进程异常的基类 |
| 超时异常 | TimeoutExpired | [D1] | 超时到期时抛出 |
| 非零退出异常 | CalledProcessError | [D1] | check=True 时非零退出码抛出 |
| 进程等待方法 | poll() / wait() / communicate() | [D1] | 三种等待进程结束的方式 |

## 边界与分流

- **超时异常捕获后**：应调用 proc.kill() 终止子进程，再调用 communicate() 清理管道，避免僵尸进程
- **shell=True 场景**：退出码反映 shell 自身状态（如 Bash 的 128+N 表示被信号 N 终止），需额外解析
- **Windows 平台**：kill() 是 terminate() 的别名，SIGTERM 映射为 TerminateProcess()
- **管道死锁风险**：使用 communicate() 而非直接读写 stdin/stdout/stderr，避免 OS 管道缓冲区满导致阻塞
- **异常未捕获时**：进程可能成为僵尸进程，需在 finally 块中确保资源清理

## 质量检查

| 检查点 | 阈值 | 失败处理 |
|--------|------|----------|
| 退出码校验 | returncode == 0 | 记录 stderr，触发重试或告警 |
| 超时检测 | 进程运行时间 < timeout | 终止进程，记录超时日志 |
| 输出完整性 | stdout/stderr 非 None | 检查管道配置是否正确 |
| 异常捕获 | 所有 SubprocessError 子类 | 记录异常堆栈，分类故障 |

## 回退策略

- 退出码异常时：检查命令路径、参数格式、环境变量
- 超时时：增加 timeout 值或优化 CLI 程序性能
- 管道死锁时：改用 communicate() 或异步 IO
- 权限错误时：检查文件系统权限或使用 sudo

## 资源召回建议

当用户遇到以下场景时应召回本卡片：
- CLI 工具返回非零退出码需要诊断
- 进程超时需要设置合理的 timeout 值
- 需要捕获和分析标准错误输出
- 需要设计 CLI 执行的容错和恢复机制
- 跨平台（Linux/Windows/macOS）CLI 兼容性问题

配套资源：general-json-schema-validation-contract（当 CLI 输出需要结构化校验时）

## 补充证据（开源权威文档）

[D1] subprocess — Subprocess management — Python 3.14.7 documentation, Python Software Foundation, v3.14.7, URL: https://docs.python.org/3/library/subprocess.html（accessed_at 2026-09-16，官方权威文档）

## 证据来源

[1] subprocess — Subprocess management — Python 3.14.7 documentation, Python Software Foundation, 2026, URL: https://docs.python.org/3/library/subprocess.html