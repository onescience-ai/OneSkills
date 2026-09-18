# CLI 故障诊断与错误处理

## 适用范围

当需要在非交互式环境（自动化流水线、CI/CD、远程执行）中运行命令行工具时，本卡提供标准化的故障分类、诊断流程与恢复策略。适用于任何通过进程退出码、超时信号或资源隔离机制进行错误报告的 CLI 工具，包括科学计算脚本、数据处理管道和远程任务提交系统。

## 输入

- CLI 工具的退出码（exit code）或异常信号
- 标准错误输出（stderr）
- 执行环境信息（操作系统、shell 类型、权限配置）
- 超时配置参数（timeout）

## 输出

- 错误分类结果（成功/应用错误/系统错误/信号终止/配置错误）
- 故障根因定位报告
- 恢复建议（重试策略/配置修正/权限调整）

## 流程节点

### 1. 退出码采集与初步分类

捕获进程的退出码并映射到标准错误类别：

- `0` → 成功（EXIT_SUCCESS）[D1]
- `1-63` → 应用程序自定义错误 [D3]
- `64-78` → 标准化错误类型（sysexits.h）[D3]
- `126` → 命令不可执行（权限不足）
- `127` → 命令未找到（PATH 配置错误）
- `128+N` → 被信号 N 终止（如 SIGKILL=137, SIGTERM=143）[D1]

### 2. 标准错误输出分析

解析 stderr 内容以获取详细错误信息：

- 检查是否包含超时关键词（timeout, timed out）
- 检查是否包含权限错误（Permission denied, EACCES）
- 检查是否包含资源错误（ENOMEM, ENOSPC）
- 检查是否包含配置错误（config, argument）

### 3. 退出码语义细化

对 sysexits.h 范围（64-78）进行语义映射 [D3]：

| 退出码 | 常量名 | 语义 |
|--------|--------|------|
| 64 | EX_USAGE | 命令使用错误（参数数量/标志/语法） |
| 65 | EX_DATAERR | 输入数据格式错误 |
| 66 | EX_NOINPUT | 输入文件不存在或不可读 |
| 69 | EX_UNAVAILABLE | 服务不可用 |
| 70 | EX_SOFTWARE | 内部软件错误 |
| 71 | EX_OSERR | 操作系统错误（fork/pipe 失败） |
| 73 | EX_CANTCREAT | 无法创建输出文件 |
| 74 | EX_IOERR | I/O 错误 |
| 75 | EX_TEMPFAIL | 临时失败（可重试） |
| 76 | EX_PROTOCOL | 协议错误 |
| 77 | EX_NOPERM | 权限不足 |
| 78 | EX_CONFIG | 配置错误 |

### 4. 超时故障诊断

当退出码为 124（timeout 命令）或进程被 SIGALRM 终止时 [D4]：

- 检查超时配置是否合理（计算密集型任务需更长时间）
- 检查是否存在死循环或阻塞调用
- 检查系统负载（CPU/内存/IO 等待）
- 建议：增加超时阈值或优化算法复杂度

### 5. 沙箱隔离故障诊断

当进程因权限不足或资源限制失败时 [D5]：

- 检查进程权限配置（setuid/setgid）
- 检查命名空间隔离设置（unshare/setns）
- 检查资源限制（setrlimit：CPU时间、内存、文件大小）
- 检查文件系统访问权限（chroot/容器）

### 6. 信号终止诊断

当退出码 ≥128 时，表示进程被信号终止 [D1]：

| 退出码 | 信号 | 含义 |
|--------|------|------|
| 129 | SIGHUP | 终端挂起或控制进程终止 |
| 130 | SIGINT | 键盘中断（Ctrl+C） |
| 137 | SIGKILL | 强制终止（不可捕获） |
| 143 | SIGTERM | 终止请求（可捕获） |
| 139 | SIGSEGV | 段错误（内存访问越界） |

## 关键参数

### 通用判据（方法层，同类体系可参考）

| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| 超时检测退出码 | 124 | [D3] | timeout 命令标准退出码 |
| SIGKILL 映射退出码 | 127+N | [D1] | POSIX 标准信号终止码计算 |
| stderr 缓冲区大小 | ≥4096 bytes | [D2] | 避免错误信息截断 |
| 重试间隔 | 指数退避 | [D3] | EX_TEMPFAIL 时推荐 |

### 校准数值（体系专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| POSIX 最低 8 位退出码 | status & 0377 | [D1] | 只有最低 8 位可通过 wait() 获取 |
| SIGALRM 最大延迟 | UINT_MAX 秒 | [D4] | 无符号整数最大值 |
| Python subprocess timeout 单位 | 秒（浮点数） | [D2] | 支持小数精度 |

## 边界与分流

### 超时配置不合理

**前提**：超时阈值足够覆盖正常执行时间。
**不成立时**：增加超时阈值，或优化任务拆分（将长任务分解为多个短任务）。

### 权限不足

**前提**：执行环境具有足够权限。
**不成立时**：使用 sudo 提权，或调整 setuid/setgid 配置，或切换到容器化执行。

### 资源耗尽

**前提**：系统资源（CPU/内存/磁盘）充足。
**不成立时**：使用 cgroup 或容器限制资源使用，或迁移到资源更丰富的环境。

### 信号不可捕获

**前提**：目标信号可被捕获和处理。
**不成立时**：SIGKILL 和 SIGSTOP 不可捕获，只能从系统层面调整（如增加内存、修复代码）。

## 质量检查

- 退出码是否映射到正确的错误类别
- stderr 输出是否包含足够的诊断信息
- 超时配置是否与任务复杂度匹配
- 沙箱配置是否与安全要求匹配

## 回退策略

- **退出码未知**：收集 stderr 全文并人工分析
- **信号终止**：检查系统日志（dmesg/journalctl）获取内核级错误
- **权限不足**：切换到非沙箱环境测试，确认是否为沙箱配置问题
- **资源耗尽**：使用资源监控工具（top/htop/iostat）定位瓶颈

## 资源召回建议

当遇到以下场景时召回本卡：
- CLI 工具在自动化流水线中非零退出
- 远程执行任务超时或被终止
- 需要标准化处理不同 CLI 工具的错误输出
- 需要设计 CLI 工具的错误处理策略

配套资源：
- `json-schema-report-contract`：报告交付契约验证

## 补充证据（开源文档）

[D1] The Open Group Base Specifications Issue 7 - exit, IEEE/The Open Group, POSIX.1-2017, URL: https://pubs.opengroup.org/onlinepubs/9699919799/functions/exit.html (accessed 2026-09-16, 交叉验证)

[D2] subprocess — Subprocess management, Python Software Foundation, Python 3.x, URL: https://docs.python.org/3/library/subprocess.html (accessed 2026-09-16, 交叉验证)

[D3] sysexits(3) - FreeBSD Manual Pages, FreeBSD Project, Version 3, URL: https://www.freebsd.org/cgi/man.cgi?query=sysexits&sektion=3 (accessed 2026-09-16, 交叉验证)

[D4] The Open Group Base Specifications Issue 7 - alarm, IEEE/The Open Group, POSIX.1-2017, URL: https://pubs.opengroup.org/onlinepubs/9699919799/functions/alarm.html (accessed 2026-09-16, 交叉验证)

[D5] os — Miscellaneous operating system interfaces, Python Software Foundation, Python 3.x, URL: https://docs.python.org/3/library/os.html (accessed 2026-09-16, 交叉验证)

[D6] exit(3) - Linux manual page, Linux man-pages project, Version 3, URL: https://man7.org/linux/man-pages/man3/exit.3.html (accessed 2026-09-16, 交叉验证)

## 证据来源

[D1] The Open Group Base Specifications Issue 7 - exit, IEEE/The Open Group, 2018

[D2] subprocess — Subprocess management, Python Software Foundation, Python 3.x

[D3] sysexits(3) - FreeBSD Manual Pages, FreeBSD Project, Version 3

[D4] The Open Group Base Specifications Issue 7 - alarm, IEEE/The Open Group, 2018

[D5] os — Miscellaneous operating system interfaces, Python Software Foundation, Python 3.x

[D6] exit(3) - Linux manual page, Linux man-pages project, Version 3
## 批次补充（2026-09-17：CLI基准测试与黑盒差异测试知识）

### 论文证据补充

从最新检索的论文中抽取以下知识，丰富CLI故障诊断与错误处理体系：

**[1] Evaluating LLM-Based 0-to-1 Software Generation in End-to-End CLI Tool Scenarios (DOI: 2604.06742)**

| 概念 | 描述 | 来源 | 说明 |
|------|------|------|------|
| CLI-Tool-Bench | 结构无关的基准，用于评估从零开始生成CLI工具 | [1] | 使用自动化黑盒差异测试框架 |
| 黑盒差异测试 | 在隔离沙箱中执行生成的软件，比较系统级副作用和终端输出 | [1] | 使用严格的多层级等价度量 |
| 隔离沙箱执行 | 在隔离环境中执行CLI工具，确保安全性和可重复性 | [1] | 防止系统级副作用影响宿主环境 |
| 多层级等价度量 | 比较生成的输出与人类编写的预言机 | [1] | 评估CLI工具的功能正确性 |

### 补充边界与分流

- **基准测试验证**：当需要评估CLI工具生成功能时，应使用CLI-Tool-Bench等基准进行黑盒差异测试[1]
- **隔离沙箱执行**：在测试CLI工具时，应在隔离沙箱中执行，防止系统级副作用[1]
- **多层级等价度量**：使用严格的多层级等价度量比较生成的输出与人类编写的预言机[1]
- **LLM生成评估**：对于LLM生成的CLI工具，应评估其成功率（最高43.8%）[1]

### 补充质量检查

- 验证CLI工具是否在隔离沙箱中执行
- 检查黑盒差异测试是否使用多层级等价度量
- 确保基准测试覆盖多种编程语言和复杂度级别
- 验证LLM生成CLI工具的成功率评估

### 补充回退策略

- **基准测试失败**：当基准测试失败时，应检查CLI工具的生成过程，或使用更简单的测试用例
- **隔离沙箱不可用**：当隔离沙箱不可用时，应使用其他隔离技术（如容器、虚拟机）
- **等价度量不匹配**：当等价度量不匹配时，应调整度量阈值或使用更宽松的比较策略
- **LLM生成质量差**：当LLM生成质量差时，应优化提示词或使用更强大的模型

## 批次补充（2026-09-17：任务51归因分析CLI故障诊断案例）

### 实际应用案例

基于归因分析任务（任务ID：51，大卷积核RNA二级结构预测）的CLI故障诊断案例：

#### 故障症状
- **退出码**：1（非零退出）
- **故障类型**：CLI非交互执行失败
- **错误特征**：归因分析智能体未正常完成生命周期
- **输出特征**：缺少核心必填字段，包含额外字段，任务身份不一致

#### 故障根因分析
- CLI进程未正常完成生命周期，导致输出结构不符合Schema定义
- 输出格式为错误响应而非预期的归因报告格式
- 任务身份字段缺失或不匹配，无法关联到正确的任务索引
- 可能原因：CLI参数错误、认证失败、超时、资源限制

#### 修复验证要点
- 检查CLI命令参数是否正确，特别是任务ID和任务名称
- 验证认证配置和权限设置
- 检查超时配置是否合理
- 确保输出格式符合JSON Schema契约
- 使用report-schema.json校验最终输出并执行错配字段反例测试

#### 与前次失败案例的对比
- Task 29、Task 49、Task 81、Task 291、Task 292同样出现退出码1和CLI执行失败
- Task 51的特征与Task 292相似：CLI进程未正常完成，输出格式错误
- 共同根因：CLI执行成功但输出格式不符合Schema校验要求

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码 | 1 | 任务51案例 | 非零退出表示失败 |
| 故障类型 | CLI非交互执行失败 | 任务51案例 | 归因分析智能体未正常完成 |
| 输出格式错误 | 缺少必填字段 | 任务51案例 | 缺少task_id, task, summary, issues |
| 额外字段存在 | 包含未定义字段 | 任务51案例 | error, sessionID, timestamp, type |
| 任务身份不一致 | task_id与索引不匹配 | 任务51案例 | 无法关联到正确的任务 |

## 批次补充（2026-09-18：任务232归因分析CLI故障诊断案例）

### 实际应用案例

基于归因分析任务（任务ID：232，全球航空危险云微物理要素1—7天预报）的CLI故障诊断案例：

#### 故障症状
- **退出码**：1（非零退出）
- **故障类型**：CLI非交互执行失败
- **错误特征**：归因分析智能体未正常完成生命周期
- **输出特征**：缺少核心必填字段，包含额外字段，任务身份不一致

#### 故障根因分析
- CLI进程未正常完成生命周期，导致输出结构不符合Schema定义
- 输出格式为错误响应而非预期的归因报告格式
- 任务身份字段缺失或不匹配，无法关联到正确的任务索引
- 可能原因：CLI参数错误、认证失败、超时、资源限制

#### 修复验证要点
- 检查CLI命令参数是否正确，特别是任务ID和任务名称
- 验证认证配置和权限设置
- 检查超时配置是否合理
- 确保输出格式符合JSON Schema契约
- 使用report-schema.json校验最终输出并执行错配字段反例测试

#### 与前次失败案例的对比
- Task 51、Task 29、Task 49、Task 81、Task 291、Task 292同样出现退出码1和CLI执行失败
- Task 232的特征与Task 51相似：CLI进程未正常完成，输出格式错误
- 共同根因：CLI执行成功但输出格式不符合Schema校验要求

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码 | 1 | 任务232案例 | 非零退出表示失败 |
| 故障类型 | CLI非交互执行失败 | 任务232案例 | 归因分析智能体未正常完成 |
| 输出格式错误 | 缺少必填字段 | 任务232案例 | 缺少task_id, task, summary, issues |
| 额外字段存在 | 包含未定义字段 | 任务232案例 | error, sessionID, timestamp, type |
| 任务身份不一致 | task_id与索引不匹配 | 任务232案例 | 无法关联到正确的任务 |
