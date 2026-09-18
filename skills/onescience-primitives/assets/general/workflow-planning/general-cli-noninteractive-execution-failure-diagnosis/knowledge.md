# CLI 非交互执行故障诊断与分类

## 适用范围

面向 CLI 工具在自动化流水线中的非交互执行场景，覆盖进程启动、参数校验、认证、沙箱隔离、超时处理、退出码判读和标准错误捕获的全流程故障诊断。适用于需要从 CLI 退出状态推断故障类别并制定恢复策略的工程实践，不适用于交互式终端操作或图形界面应用的错误处理。

## 输入

- CLI 命令及其参数组合
- 执行环境信息（操作系统、shell 类型、Python 版本）
- 进程退出码（exit code / return code）
- stdout 和 stderr 捕获内容
- 执行耗时与超时配置

## 输出

- 故障类别判定（参数错误、认证失败、资源不可用、超时、信号终止等）
- 退出码语义映射
- 恢复策略建议（重试、降级、终止）

## 流程节点

### Step 1：进程退出状态捕获
- **操作**：捕获 CLI 进程的退出码、stdout、stderr
- **参数**：exit_code = 进程返回值, stdout = 标准输出缓冲, stderr = 标准错误缓冲
- **工具**：subprocess.run() / os.system() / shell $? 变量
- **质量门禁**：退出码必须为整数类型，stdout/stderr 编码正确（UTF-8 或平台默认编码）

### Step 2：退出码分类映射
- **操作**：将退出码映射到标准故障类别
- **参数**：见关键参数表
- **工具**：人工查表或自动化分类脚本
- **质量门禁**：分类结果必须覆盖所有已知退出码范围

### Step 3：超时与信号检测
- **操作**：检测进程是否因超时或信号被终止
- **参数**：timeout_exit_code = 124（coreutils 标准）, signal_base = 128
- **工具**：时间戳比对、信号编号解析
- **质量门禁**：信号终止必须记录信号编号（SIGTERM=15, SIGKILL=9, SIGINT=2）

### Step 4：stderr 内容分析
- **操作**：从 stderr 中提取错误关键词和堆栈信息
- **参数**：关键词模式库（Error, Exception, Permission denied, Timeout, etc.）
- **工具**：正则表达式匹配、关键词频率统计
- **质量门禁**：必须捕获至少一类错误关键词

### Step 5：故障类别判定与恢复建议
- **操作**：综合退出码、信号、stderr 信息判定最终故障类别
- **参数**：故障类别映射表
- **工具**：决策树或规则引擎
- **质量门禁**：判定结果必须有对应的恢复策略

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| EXIT_SUCCESS | 0 | [D1] POSIX.1-2017 | 成功退出（所有平台通用） |
| EXIT_FAILURE | 非零 | [D1] POSIX.1-2017 | 通用失败（C 标准常量） |
| 退出码有效位 | 低 8 位 (status & 0377) | [D1] POSIX.1-2017 | wait()/waitpid() 可获取的位数 |
| 应用定义失败范围 | 1–125 | [D2] BSD sysexits.h | 应用程序自定义退出码安全范围 |
| 命令不可执行 | 126 | [D3] Bash Exit Codes | 权限不足或非可执行文件 |
| 命令未找到 | 127 | [D3] Bash Exit Codes | PATH 中不存在该命令 |
| 信号终止计算 | 128 + N | [D3] Bash Exit Codes | N 为信号编号（SIGTERM=15, SIGKILL=9） |
| 超时退出码 | 124 | [D3] Bash Exit Codes / coreutils | timeout 命令标准超时退出码 |
| 用户自定义码范围 | 64–113 | [D3] Bash Exit Codes | 避免与系统保留码冲突 |
| 退出值取模 | value % 256 | [D3] Bash Exit Codes | 大于 255 的退出值被取模 |

### BSD sysexits.h 标准化退出码

| 退出码 | 名称 | 含义 | 来源 |
|--------|------|------|------|
| 0 | EX_OK | 成功终止 | [D2] |
| 64 | EX_USAGE | 命令行用法错误 | [D2] |
| 65 | EX_DATAERR | 数据格式错误 | [D2] |
| 66 | EX_NOINPUT | 无法打开输入 | [D2] |
| 69 | EX_UNAVAILABLE | 服务不可用 | [D2] |
| 70 | EX_SOFTWARE | 内部软件错误 | [D2] |
| 71 | EX_OSERR | 系统错误（如 fork 失败） | [D2] |
| 73 | EX_CANTCREAT | 无法创建输出文件 | [D2] |
| 74 | EX_IOERR | I/O 错误 | [D2] |
| 75 | EX_TEMPFAIL | 临时失败，建议重试 | [D2] |
| 77 | EX_NOPERM | 权限被拒绝 | [D2] |
| 78 | EX_CONFIG | 配置错误 | [D2] |

### 信号终止映射

| 退出码 | 信号 | 含义 | 来源 |
|--------|------|------|------|
| 130 | SIGINT (2) | 用户中断（Ctrl-C） | [D3] |
| 137 | SIGKILL (9) | 强制终止（不可捕获） | [D3] |
| 143 | SIGTERM (15) | 优雅终止请求 | [D3] |
| 139 | SIGSEGV (11) | 段错误（内存访问违规） | [D3] |
| 134 | SIGABRT (6) | 异常中止 | [D3] |

## 边界与分流

- **退出码超出已知范围**：记录原始值，标记为"未知退出码"，建议查阅目标工具文档
- **stderr 为空但退出码非零**：可能是静默失败，建议检查日志文件或开启 verbose 模式
- **超时退出码 124 但无超时配置**：可能是其他工具约定使用 124，需确认超时来源
- **信号终止但无法确定信号来源**：可能是外部进程杀子进程（OOM Killer），检查系统日志
- **Python SystemExit 异常**：退出码由 sys.exit() 参数决定，字符串参数会打印后退出码为 1

## 质量检查

- 退出码必须在 0–255 范围内（超出部分取模 256）
- 信号终止必须能反推原始信号编号
- stderr 捕获必须使用与进程相同的编码
- 超时检测必须有明确的超时阈值配置
- 恢复策略必须与故障类别一一对应

## 回退策略

- 退出码无法分类时：执行一次带 verbose 输出的重试，收集更多诊断信息
- stderr 被截断时：增加 stderr 缓冲区大小或重定向到文件
- 超时不确定时：设置显式超时阈值并记录实际耗时

## 资源召回建议

当遇到以下场景时应召回本卡片：
- CLI 工具在自动化流水线中频繁退出码异常
- 需要区分参数错误、认证失败、资源不可用等不同故障类别
- 需要为 CLI 退出码设计统一的错误处理框架
- 需要处理超时和信号终止的诊断逻辑

配套资源：`general-json-schema-report-delivery-contract`（结构化输出契约校验）

## 证据来源

[1] "Process-level trajectory evaluation for environment configuration in software engineering agents", J Kuang et al., ICLR 2026
[2] "Agentprocessbench: Diagnosing step-level process quality in tool-using agents", S Fan et al., ACM, 2026
[3] "Terminal-bench: Benchmarking agents on hard, realistic tasks in command line interfaces", M Merrill et al., ICLR 2026

## 补充证据（权威文档）

[D1] POSIX.1-2017 exit() Function Specification, The Open Group (IEEE Std 1003.1-2017), Issue 7, 2018 edition, URL: https://pubs.opengroup.org/onlinepubs/9699919799/functions/exit.html（accessed 2026-09-17，交叉验证）
[D2] BSD sysexits.h Standardized Exit Codes, FreeBSD Project, main branch, URL: https://raw.githubusercontent.com/freebsd/freebsd-src/main/include/sysexits.h（accessed 2026-09-17，交叉验证）
[D3] Bash Advanced Scripting Guide - Exit Codes With Special Meanings, The Linux Documentation Project, URL: https://tldp.org/LDP/abs/html/exitcodes.html（accessed 2026-09-17，交叉验证）
