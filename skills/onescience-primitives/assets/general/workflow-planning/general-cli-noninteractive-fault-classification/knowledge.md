# CLI 非交互执行与故障分类

## 适用范围

面向任意命令行工具的非交互式调用场景：自动化流水线、CI/CD 作业、批量任务调度中需要可靠地启动子进程、捕获输出、判断成功/失败并进行故障分类。适用于 Python subprocess 模块及其他语言等价机制（Node.js child_process、Go exec.Command）的通用流程。不适用于交互式终端会话或需要用户输入的场景。

## 输入

- 目标 CLI 命令及其参数（字符串序列或 shell 命令行）
- 可选：工作目录（cwd）、环境变量（env）、标准输入数据
- 可选：超时时间（秒）、编码方式

## 输出

- 进程退出码（returncode）
- 标准输出（stdout）与标准错误（stderr）内容
- 故障分类标签（成功 / 非零退出 / 超时 / 启动失败 / 信号终止）
- 诊断日志（含命令、退出码、输出摘要、异常类型）

## 流程节点

### 1. 进程启动

操作：使用 `subprocess.run()` 或 `Popen()` 创建子进程。  
参数：`args`（命令序列，推荐列表形式避免 shell 注入）、`capture_output=True`、`text=True`（文本模式）、`timeout=N`。  
工具：Python subprocess 模块。  
质量门禁：命令参数必须为列表形式（非单字符串+shell=True），避免 shell 注入风险。  
证据来源 [D1]

### 2. 执行等待与超时处理

操作：`run()` 内部调用 `communicate()` 等待进程完成；若超时则抛出 `TimeoutExpired`。  
参数：`timeout` 秒数。  
工具：subprocess.run / Popen.communicate。  
质量门禁：捕获 `TimeoutExpired` 后必须显式 `kill()` 进程再调用 `communicate()` 清理管道，避免僵尸进程。  
证据来源 [D1]

### 3. 退出码语义解析

操作：读取 `CompletedProcess.returncode` 或 `Popen.returncode`。  
退出码约定：

| 退出码 | 含义 | 诊断动作 |
|--------|------|----------|
| 0 | 成功 | 正常继续 |
| 1–125 | 应用错误 | 解析 stderr 中的具体错误信息 |
| 126 | 命令不可执行 | 检查文件权限 |
| 127 | 命令未找到 | 检查 PATH 和可执行文件路径 |
| 128+N | 被信号 N 终止 | 记录信号编号（如 137=SIGKILL） |
| 负值 -N | POSIX 信号终止 | 同上 |

工具：returncode 属性 + shell 手册（如 Bash Exit Status）。  
质量门禁：非零退出码必须配合 stderr 内容共同诊断，不可仅凭退出码断言根因。  
证据来源 [D1]

### 4. 标准流捕获与诊断

操作：stdout/stderr 已通过 `capture_output=True` 捕获为字符串。  
参数：`text=True` 确保字符串而非字节。  
工具：CompletedProcess.stdout / .stderr。  
质量门禁：输出过大时截断保存，记录总长度；stderr 是故障诊断的第一手来源。  
证据来源 [D1]

### 5. 异常分类与恢复策略

操作：根据异常类型分类故障并选择恢复策略。

| 异常类型 | 含义 | 恢复策略 |
|----------|------|----------|
| CalledProcessError | 非零退出码 | 解析 stderr，按退出码分类后重试或跳过 |
| TimeoutExpired | 超时 | kill 进程，记录超时前输出，增大 timeout 或分解任务 |
| OSError / FileNotFoundError | 启动失败 | 检查可执行文件路径、权限、依赖 |
| PermissionError | 权限不足 | 以适当权限重试或修改文件权限 |

质量门禁：每种异常必须有对应的恢复策略，不可静默忽略。  
证据来源 [D1]

### 6. 诊断日志输出

操作：将执行结果结构化记录为诊断日志。  
必记字段：命令文本、退出码、stdout 摘要（前 500 字符）、stderr 全文、异常类型、耗时。  
质量门禁：日志必须保留原始 stderr 内容，不可仅记录异常消息。

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 参数传递形式 | 列表（非字符串） | [D1] | 避免 shell 注入，Windows 下自动处理引号 |
| shell 参数 | False（默认） | [D1] | 除非确实需要 shell 特性（管道、通配符），否则保持 False |
| capture_output | True | [D1] | 自动捕获 stdout+stderr 到 PIPE |
| text/encoding | text=True | [D1] | 输出为字符串而非字节，便于日志和解析 |
| timeout | 按任务设定 | [D1] | 必须配合异常捕获和进程清理 |

### 校准数值

以下数值来自 Python 标准库实践，供量级校准；其他运行时需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码 126 | 命令不可执行 | [D1] | POSIX 标准，shell 预定义 |
| 退出码 127 | 命令未找到 | [D1] | POSIX 标准，shell 预定义 |
| 退出码 128+N | 信号终止 | [D1] | N 为信号编号，Bash 约定 |
| stderr 截断阈值 | 500 字符 | 实践建议 | 诊断日志中 stderr 摘要长度 |

## 边界与分流

- **子进程产生大量输出导致管道阻塞**：不可使用 `Popen.stdout.read()`，必须使用 `communicate()` 避免死锁。改道：始终用 `communicate()` 读取管道。
- **Windows 平台 shell=True 行为差异**：Windows 下 `shell=True` 使用 `%COMSPEC%`，当前目录搜索顺序与 POSIX 不同。改道：跨平台时统一用 `shell=False` + 列表参数。
- **信号终止 vs 正常退出**：POSIX 下负 returncode 表示信号终止，Windows 下 `kill()` 等价于 `terminate()`。改道：按平台分别处理信号语义。
- **认证/沙箱限制**：CLI 工具可能需要 API key、代理或沙箱环境。改道：通过 `env` 参数注入环境变量，或在 `cwd` 中设置工作目录。

## 质量检查

- [ ] 命令以列表形式传递（非 shell=True + 字符串）
- [ ] timeout 异常被捕获并清理子进程
- [ ] 非零退出码配合 stderr 进行诊断
- [ ] 诊断日志包含命令、退出码、stdout 摘要、stderr 全文
- [ ] 跨平台兼容性：shell=False 优先

## 回退策略

- subprocess 不可用时：回退到 `os.system()`（功能受限，无输出捕获）
- 需要交互式输入时：回退到 `pexpect`（POSIX）或 `pexpect` 的 Windows 等价物
- 需要异步执行时：回退到 `asyncio.create_subprocess_exec`

## 批次补充（2026-09-21）

### Python argparse exit_on_error 参数

Python argparse 模块提供 `exit_on_error` 参数控制错误处理行为：
- `exit_on_error=True`（默认）：解析错误时打印到 stderr 并以退出码 2 退出
- `exit_on_error=False`：解析错误时抛出 `argparse.ArgumentError` 异常，由调用方处理

```python
parser = argparse.ArgumentParser(exit_on_error=False)
try:
    parser.parse_args('--integers a'.split())
except argparse.ArgumentError:
    print('Catching an argumentError')
```

证据来源 [D2]

### 扩展退出码语义（POSIX 标准）

| 退出码 | 含义 | 来源 | 说明 |
|--------|------|------|------|
| 0 | 成功 | [D3] | 正常退出 |
| 1 | 一般错误 | [D3] | 杂项错误（如除零） |
| 2 | shell 内置命令误用 | [D3] | 缺少关键字或命令 |
| 126 | 命令不可执行 | [D3] | 权限问题或非可执行文件 |
| 127 | 命令未找到 | [D3] | PATH 问题或拼写错误 |
| 128+N | 被信号 N 终止 | [D3] | 如 137=SIGKILL, 130=Ctrl+C |
| 130 | 脚本被 Ctrl+C 终止 | [D3] | 信号 2 的 128+2 |
| 255 | 退出状态超出范围 | [D3] | exit 只接受 0-255 |

证据来源 [D3]

## 资源召回建议

当任务涉及以下场景时应召回本卡片：
- 自动化流水线中调用第三方 CLI 工具
- 需要根据退出码判断任务成功/失败
- CLI 超时导致流水线卡死
- 需要诊断 CLI 执行失败的根因
- 跨平台（Linux/Windows）CLI 调用兼容性问题

配套卡片：`general-json-schema-report-validation-contract`（当 CLI 输出需要结构化校验时）

## 补充证据（开源权威文档）

[D1] subprocess — Subprocess management, Python Software Foundation, Python 3.14.7 documentation, URL: https://docs.python.org/3/library/subprocess.html（accessed 2026-09-17，官方标准库文档，权威性高）

## 证据来源

[1] Python 3.14.7 标准库文档 — subprocess 模块, Python Software Foundation, 2026, URL: https://docs.python.org/3/library/subprocess.html
