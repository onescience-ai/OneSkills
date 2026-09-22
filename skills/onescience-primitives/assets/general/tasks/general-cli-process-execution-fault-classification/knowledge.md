# CLI 非交互式进程执行与故障分类

## 适用范围

本卡覆盖在无用户交互的自动化流水线中启动、监控和诊断 CLI 子进程的完整任务链。适用于需要通过 subprocess 或 shell 脚本调用外部 CLI 工具（如归因分析器、科学计算 runner、数据处理管线）并要求可靠退出状态判读的场景。不适用于交互式终端会话、Web 服务 API 调用（那些走 HTTP 状态码）或 GUI 应用。

## 输入

- **CLI 命令**：命令名称、参数列表（推荐序列格式而非单字符串，避免 shell 注入风险）[D1]
- **工作目录**：可选 cwd 路径
- **环境变量**：可选 env 映射
- **超时阈值**：秒数，超时后强制终止子进程
- **重试策略**：最大重试次数、退避参数（指数退避+抖动）
- **输出捕获**：是否捕获 stdout/stderr、是否合并为 stdout

## 输出

- **退出码**（returncode）：整数，0 表示成功，非零表示故障
- **stdout/stderr**：捕获的标准输出/错误输出
- **超时标志**：是否因超时被终止
- **信号终止码**：POSIX 下负数 returncode 表示被信号终止（如 -9 = SIGKILL）
- **诊断摘要**：退出码 + stderr 前 N 行 + 超时/信号状态

## 流程节点

### 1. 进程创建与参数组装
- 使用 `subprocess.run()` 或 `subprocess.Popen()` 创建子进程
- 参数以序列形式传递（`["cmd", "arg1", "arg2"]`），避免 `shell=True` [D1]
- 如需 shell 特性（管道、通配符），显式设置 `shell=True` 并用 `shlex.quote()` 转义用户输入 [D1]

### 2. 输出捕获配置
- `stdout=subprocess.PIPE, stderr=subprocess.PIPE` 捕获输出
- `text=True` 以文本模式获取字符串（否则为 bytes）
- `capture_output=True` 是 `stdout=PIPE, stderr=PIPE` 的简写 [D1]
- 大数据量输出时避免 `communicate()` 全量缓冲，改用流式读取

### 3. 超时控制
- `timeout=N`（秒），超时后子进程被 SIGTERM（POSIX）或 TerminateProcess（Windows）终止 [D1]
- 超时后必须显式 `proc.kill()` 清理残留进程，再调用 `proc.communicate()` 收集输出 [D1]
- 超时异常为 `subprocess.TimeoutExpired`，包含 cmd、timeout、output、stdout、stderr 属性 [D1]

### 4. 退出码语义分类
| 退出码范围 | 含义 | 处理策略 |
|-----------|------|---------|
| 0 | 成功完成 | 正常继续 |
| 1 | 通用错误/应用级错误 | 检查 stderr 中的错误信息 |
| 2 | 命令行用法错误（参数/选项） | 修正命令参数 |
| 126 | 命令不可执行（权限不足） | 检查文件权限 |
| 127 | 命令未找到 | 检查 PATH 和命令名称 |
| 128+N | 被信号 N 终止（如 130=SIGINT, 137=SIGKILL） | 分析信号来源，检查是否为超时或资源限制 |
| 负数（POSIX） | 被信号 -N 终止 | 同 128+N 规则，通过 `os.WTERMSIG()` 提取信号编号 |

### 5. stderr 诊断分析
- 捕获 stderr 内容，按关键词匹配常见错误模式
- 关键词列表：`error`, `exception`, `traceback`, `failed`, `timeout`, `permission denied`, `no such file`
- 提取前 500 字符作为诊断摘要

### 6. 错误恢复与重试
- 识别可恢复错误（超时、临时网络问题、资源竞争）
- 指数退避重试：等待时间 = base * 2^attempt + jitter [1]
- 不可恢复错误（命令不存在、权限不足、参数错误）不重试
- 重试日志记录每次尝试的退出码和耗时

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 超时范围 | 1-3600 秒 | [D1] | 取决于任务复杂度，科学计算任务通常 300-3600 秒 |
| 重试上限 | 3-5 次 | [1] | 超过此次数视为不可恢复错误 |
| 退避基数 | 1-2 秒 | [1] | 首次重试等待时间 |
| 退避因子 | 2 | [1] | 指数退避倍数 |
| 抖动范围 | 0-1 秒 | [1] | 防止重试风暴 |
| stderr 截断长度 | 500 字符 | — | 诊断摘要的最大长度 |

### 校准数值（以 Python subprocess 为例）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| PIPE 缓冲 | 系统默认（通常 64KB-1MB） | [D1] | 大输出需流式处理避免死锁 |
| 信号终止映射 | returncode = -(signal_number) | [D1] | POSIX 下 returncode 为负数表示信号终止 |
| shell=True 返回码 | 反映 shell 本身的退出状态 | [D1] | 如 bash 的 exit status，信号映射为 128+N |

## 边界与分流

- **参数错误**（ValueError 异常）：检查 Popen 参数合法性，不重试
- **文件不存在**（OSError/ENOENT）：检查可执行文件路径，不重试
- **权限不足**（PermissionError）：检查文件权限，不重试
- **超时**（TimeoutExpired）：可恢复，执行 kill + communicate 清理后重试
- **管道死锁**：使用 `communicate()` 而非直接 `.stdin.write()`/`.stdout.read()` [D1]
- **Windows 特殊性**：`kill()` 等同于 `terminate()`（TerminateProcess），不发送 SIGKILL [D1]
- **shell=True 安全风险**：用户输入必须转义，避免 shell 注入 [D1]

## 质量检查

- 进程退出后必须调用 `poll()` 或 `communicate()` 确认 returncode 已设置
- 超时后必须显式 kill 进程，避免僵尸进程
- stderr 内容必须被捕获和检查，不得忽略
- 重试前必须记录当前退出码和错误信息
- 退出码为 None 表示进程尚未终止，不应在此时做诊断判断

## 回退策略

- subprocess 模块不可用时（如嵌入式 Python 环境）：使用 `os.system()` 仅获取退出码（无输出捕获）
- 无法捕获 stderr 时：记录 "stderr-not-captured" 并仅依赖退出码分类
- 超时机制不可用时：使用外部 watchdog 进程监控 PID 并强制 kill

## 资源召回建议

- 当任务需要调用外部 CLI 工具并解析其退出状态时召回本卡
- 配套卡片：若需要结构化报告交付，配合 `general-json-schema-report-validation-contract` 卡
- 当需要处理 Python subprocess 超时、信号终止或管道死锁问题时召回

## 补充证据

[D1] Python subprocess module documentation, Python Software Foundation, v3.14.7, URL: https://docs.python.org/3/library/subprocess.html (accessed_at: 2026-09-21, 权威官方文档)

## 证据来源

[1] Adaptive Resilience in API Polling Frameworks: A Hybrid Approach with Retry Strategies, Timeout Policies, Fallback Mechanisms, and Event-Driven Strategies, Mithilesh Ramaswamy, International Journal of Scientific Research in Engineering and Management, 2024, DOI: 10.55041/ijsrem16747

[2] SimpleSecure-CLI: A PowerShell-Based Framework for Windows Security Hardening and Compliance Automation, Ansar Shaikh, International Journal of Scientific Research in Engineering and Management, 2025, DOI: 10.55041/ijsrem50200

[3] Bumps in the Code: Error Handling During Software Development, Tamara Lopez et al., IEEE Software, 2021, DOI: 10.1109/ms.2020.3024981
