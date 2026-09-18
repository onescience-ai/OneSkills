# CLI 非交互执行故障分类与恢复

## 适用范围

面向任何通过命令行接口（CLI）驱动的自动化流水线——无论调用的是科学计算工具、数据处理脚本还是系统管理命令——本卡提供对非交互执行过程中常见故障的分类体系、诊断判据和恢复决策框架。适用于需要在无人值守或远程调度环境下稳定运行的场景，包括批处理作业、CI/CD 流水线和分布式任务编排。

## 输入

- 要执行的 CLI 命令及其参数序列（推荐 list 形式，避免 shell 注入）
- 可选的超时时间（秒）
- 可选的输入数据（通过 stdin 管道）
- 运行环境上下文（操作系统、shell 类型、工作目录）

## 输出

- 执行结果结构体：包含 returncode、stdout、stderr
- 故障分类标签（见流程节点）
- 恢复决策建议（重试/跳过/终止/降级）

## 流程节点

### 1. 命令构建与参数校验

**操作**：将命令拆分为参数列表，校验可执行文件路径和必要参数。

**参数**：
- 使用完整路径或 `shutil.which()` 解析可执行文件
- 参数以 list 形式传递，避免 shell 注入风险

**质量门禁**：可执行文件存在且可执行；参数无 shell 元字符（除非显式使用 `shell=True`）

### 2. 进程启动与超时监控

**操作**：通过 `subprocess.run()` 或 `Popen` 启动子进程，设置超时。

**参数**：
- `timeout`：超时秒数，超时后进程被 kill
- `capture_output=True` 或 `stdout=PIPE, stderr=PIPE` 捕获输出

**质量门禁**：超时触发时捕获 `TimeoutExpired` 异常，记录已捕获的部分输出

### 3. 退出码分类与诊断

根据 returncode 进行故障分类：

| 退出码范围 | 含义 | 分类标签 | 诊断动作 |
|-----------|------|---------|---------|
| `0` | 正常退出 | `success` | 无 |
| `1` | 通用错误 | `generic_error` | 检查 stderr 输出内容 |
| `2` | 误用 shell 命令 | `misuse` | 检查命令语法和参数 |
| `126` | 权限不足或非可执行文件 | `permission_denied` | 检查文件权限和 shebang |
| `127` | 命令未找到 | `command_not_found` | 检查 PATH 和可执行文件路径 |
| `128+N` | 被信号 N 终止 | `signal_terminated` | 根据信号类型判断（SIGKILL=9, SIGTERM=15） |
| `-N` (POSIX) | 被信号 N 终止 | `signal_terminated` | 同上 |
| `130` | Ctrl+C (SIGINT) | `interrupted` | 用户中断，通常不重试 |
| `137` | OOM Killer (SIGKILL) | `oom_killed` | 检查内存限制，增大内存或优化 |
| `143` | SIGTERM | `terminated` | 正常终止请求，检查是否需要清理 |

### 4. 异常类型分类

| 异常类 | 触发条件 | 分类标签 | 恢复策略 |
|--------|---------|---------|---------|
| `TimeoutExpired` | 超时 | `timeout` | 增加超时或优化命令 |
| `CalledProcessError` | 非零退出码（`check=True`） | `nonzero_exit` | 解析 returncode 和 stderr |
| `OSError` | 可执行文件不存在或权限错误 | `os_error` | 检查路径和权限 |
| `FileNotFoundError` | 可执行文件未找到 | `command_not_found` | 检查 PATH |

### 5. 输出解析与错误判读

**操作**：解析 stdout/stderr，提取关键错误信息。

**判读规则**：
- stderr 包含 "error"/"Error"/"ERROR" → 高优先级错误
- stderr 包含 "warning"/"Warning" → 可忽略或降级处理
- stdout 为空且 returncode 非零 → 命令可能未执行
- 输出包含 "timeout"/"timed out" → 超时相关

### 6. 恢复决策

| 故障类型 | 重试策略 | 降级策略 |
|---------|---------|---------|
| `success` | 无需重试 | 无需 |
| `timeout` | 增加超时重试（最多 2 次） | 使用更简化的命令 |
| `generic_error` | 分析 stderr 后决定 | 跳过或使用替代方案 |
| `permission_denied` | 修复权限后重试 | 切换用户或使用 sudo |
| `command_not_found` | 修复路径后重试 | 使用替代命令 |
| `oom_killed` | 增大内存后重试 | 优化内存使用或分批处理 |
| `signal_terminated` | 分析信号原因后决定 | 记录并跳过 |

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码 0 | 成功 | [D1] subprocess 文档 | 进程正常退出 |
| 退出码 126 | 权限问题 | [D1] subprocess 文档 | 文件不可执行或权限不足 |
| 退出码 127 | 命令未找到 | [D1] subprocess 文档 | PATH 中不存在该命令 |
| 退出码 128+N | 信号终止 | [D1] subprocess 文档 | N 为信号编号 |
| TimeoutExpired | 超时异常 | [D1] subprocess 文档 | timeout 参数触发 |
| CalledProcessError | 非零退出 | [D1] subprocess 文档 | check=True 时触发 |
| 风险分类 F1-score | 0.85–0.92 | [2] | 基于 Transformer 的 CLI 风险分类模型 |
| 命令拦截误报率 | <5% | [2] | 敏感命令检测系统的误报率 |
| 敏感数据检测准确率 | 0.90 | [2] | CLI 风险建模中的敏感信息识别 |

### 校准数值

以下数值来自 Python 标准库实现，供量级校准；其他语言运行时需以自身文档重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| SIGKILL 对应退出码 | 137 (128+9) | [D1] subprocess 文档 | POSIX 系统 |
| SIGTERM 对应退出码 | 143 (128+15) | [D1] subprocess 文档 | POSIX 系统 |
| SIGINT 对应退出码 | 130 (128+2) | [D1] subprocess 文档 | Ctrl+C |

## 边界与分流

- **当 CLI 不支持超时参数时**：转向使用操作系统级 kill（如 `taskkill` on Windows, `kill` on POSIX）配合 watchdog 定时器
- **当 shell=True 是必需时**：必须使用 `shlex.quote()` 转义用户输入，避免 shell 注入；此时退出码语义可能变化（反映 shell 自身退出状态）
- **当需要交互式输入时**：本卡不适用，应转向 pexpect/paramiko 等交互式方案
- **当目标是 Windows 批处理文件时**：注意 COMSPEC 环境变量和 shell 搜索顺序变化
- **当需要认证时**：检查环境变量、配置文件或密钥管理服务中的凭证；认证失败通常表现为非零退出码或特定错误消息（如 "Permission denied"、"Authentication failed"）
- **当需要沙箱隔离时**：使用容器（Docker）、虚拟环境或 chroot 限制 CLI 进程的资源访问；沙箱内的退出码语义与宿主环境一致，但文件系统和网络访问受限

## 质量检查

| 验证点 | 阈值 | 失败处理 |
|--------|------|---------|
| 可执行文件解析成功 | `shutil.which()` 非 None | 报错并终止 |
| 进程在超时内完成 | returncode 非 None | 触发 TimeoutExpired |
| stderr 可正确编码 | 无 UnicodeDecodeError | 使用 errors='replace' |
| 恢复策略已执行 | 重试次数 ≤ 配置上限 | 降级或终止 |

## 回退策略

1. **多次重试失败**：记录完整诊断日志，返回 `failed` 状态
2. **环境不兼容**：检查操作系统、Python 版本、依赖库
3. **资源不足**：检查磁盘空间、内存、文件描述符限制

## 资源召回建议

- 当任务涉及 CLI 命令执行时召回本卡
- 配套使用 `general-json-schema-report-validation` 卡验证 CLI 输出格式
- 对于特定领域（气象/生信/材料）的 CLI 工具，需结合领域知识卡片

## 补充证据（权威文档）

[D1] subprocess — Subprocess management, Python 3.14.7 documentation, Python Software Foundation, v3.14.7, URL: https://docs.python.org/3/library/subprocess.html（accessed_at 2026-09-16，官方权威）

## 证据来源

[1] subprocess — Subprocess management — Python 3.14.7 documentation, Python Software Foundation, 2026, URL: https://docs.python.org/3/library/subprocess.html
[2] Command-line Risk Classification using Transformer-based Neural Architectures, Notaro et al., arXiv 2024, DOI: 10.48550/arXiv.2412.01655v1
[3] Command Line Interface Risk Modeling, Faulds, arXiv 2023, DOI: 10.48550/arXiv.2302.01749v1

## 批次补充（2026-09-17）

本次合并从 `cli-fault-classification-diagnostics` 卡片引入 2 篇学术论文证据，扩展了风险分类模型的定量指标（F1-score、误报率、检测准确率），并补充了认证与沙箱隔离场景的分流指引。
