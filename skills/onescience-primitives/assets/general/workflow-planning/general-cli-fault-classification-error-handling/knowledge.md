# CLI 非交互执行故障分类与错误处理

## 适用范围

适用于任何通过命令行接口（CLI）执行的非交互式任务，涵盖进程退出码诊断、标准错误流解析、超时处理、沙箱执行隔离与故障恢复策略。当CLI工具未能正常退出或返回异常状态码时，本卡片提供系统化的诊断框架与修复路径。

## 输入

- CLI进程退出码（returncode）
- 标准错误输出（stderr）
- 进程状态信息（正常终止、信号终止、超时等）
- 执行环境信息（操作系统、权限、资源限制）

## 输出

- 故障类型分类（退出码分类、错误类别判定）
- 诊断结论（根因分析、错误传播路径）
- 修复建议（配置调整、恢复策略、重试方案）

## 流程节点

### 1. 退出码采集与范围判定

**操作**：获取CLI进程退出码，判断其所属范围

**参数**：
- 退出码 0：成功
- 退出码 1-125：应用程序定义错误
- 退出码 126：命令不可执行（权限问题）
- 退出码 127：命令未找到（路径或环境问题）
- 退出码 128+N：被信号N终止（POSIX系统）

**工具**：`subprocess.run()` 返回的 `returncode` 属性，或 shell 的 `$?` 变量

**质量门禁**：退出码必须为整数类型，非零值需进一步诊断

### 2. 标准化错误分类（sysexits.h）

**操作**：对64-78范围的退出码进行标准化分类

**参数**：
- EX_USAGE (64)：命令使用错误（参数数量、标志、语法）
- EX_DATAERR (65)：输入数据错误
- EX_NOINPUT (66)：输入文件不存在或不可读
- EX_NOUSER (67)：指定的用户不存在
- EX_NOHOST (68)：指定的主机不存在
- EX_UNAVAILABLE (69)：服务不可用
- EX_SOFTWARE (70)：内部软件错误
- EX_OSERR (71)：操作系统错误（fork、pipe失败）
- EX_OSFILE (72)：系统文件错误
- EX_CANTCREAT (73)：无法创建输出文件
- EX_IOERR (74)：I/O错误
- EX_TEMPFAIL (75)：临时失败（可重试）
- EX_PROTOCOL (76)：协议错误
- EX_NOPERM (77)：权限不足
- EX_CONFIG (78)：配置错误

**工具**：系统头文件 `<sysexits.h>` 或等效的退出码常量定义

**质量门禁**：分类必须与退出码精确匹配，不得模糊归类

### 3. 标准错误流解析

**操作**：捕获并分析CLI工具的标准错误输出

**参数**：
- stderr内容：错误消息、警告信息、调试输出
- 错误模式：异常堆栈、错误代码、错误描述
- 上下文信息：执行命令、输入参数、环境变量

**工具**：`subprocess.run(stderr=subprocess.PIPE)` 或 `asyncio.create_subprocess_shell()` 的 stderr 参数

**质量门禁**：stderr必须完整捕获，不得截断或丢失

### 4. 超时检测与处理

**操作**：检测CLI执行是否超时，执行超时处理策略

**参数**：
- 超时阈值：根据任务复杂度设定合理超时时间
- 超时信号：POSIX系统发送SIGALRM或SIGKILL
- 资源清理：超时后必须终止进程并释放资源

**工具**：
- POSIX层：`alarm()` 函数 + 信号处理
- Python层：`subprocess.run(timeout=...)` 参数
- 异步层：`asyncio.wait_for()` 函数

**质量门禁**：超时后必须调用 `proc.kill()` 并再次 `communicate()` 确保资源释放

### 5. 沙箱执行隔离

**操作**：在隔离环境中执行CLI工具，防止故障扩散

**参数**：
- 权限隔离：使用 `setuid()`/`setgid()` 降权执行
- 命名空间隔离：使用 `unshare()`/`setns()` 隔离资源
- 资源限制：使用 `setrlimit()` 控制CPU、内存、文件描述符等
- 文件系统隔离：使用 `chroot()` 或容器技术

**工具**：`os.setuid()`, `os.setgid()`, `os.unshare()`, `os.setrlimit()` 等系统调用

**质量门禁**：沙箱配置必须匹配任务安全要求，不得过度限制导致功能失效

### 6. 故障恢复策略

**操作**：根据故障类型选择恢复路径

**参数**：
- 可重试故障：EX_TEMPFAIL (75)、信号终止（可恢复信号）
- 配置错误：EX_CONFIG (78)、EX_USAGE (64) → 修正配置后重试
- 资源不足：EX_OSERR (71)、EX_NOPERM (77) → 调整资源或权限
- 不可恢复故障：EX_SOFTWARE (70)、IO错误 → 记录日志，报告人工处理

**工具**：重试逻辑、配置更新、权限调整、日志记录

**质量门禁**：恢复策略必须基于准确的故障分类，不得盲目重试

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码范围 | 0-255 | [D1] | POSIX标准，仅最低有效8位可通过wait()获取 |
| sysexits.h范围 | 64-78 | [D3] | BSD标准化错误类型，已弃用但广泛使用 |
| Python returncode | 0或负值 | [D2] | 0表示成功，负值-N表示被信号N终止（仅POSIX） |
| 超时处理层级 | POSIX/Python/Async | [D2][D7] | 根据执行环境选择合适层级 |

### 校准数值

以下数值来自POSIX/Python标准实现，供量级校准；其他系统需以自身证据重新锚定：

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| EXIT_SUCCESS | 0 | [D1] | 成功退出标准值 |
| EXIT_FAILURE | 1 | [D1] | 一般失败标准值 |
| 最大退出码 | 255 | [D1] | 8位无符号整数最大值 |
| 信号终止基准 | 128 | [D4] | 128+N表示被信号N终止 |

## 边界与分流

### 前提不成立时的转向

1. **退出码不可获取**（进程异常终止、父进程未等待）：
   - 转向：检查进程日志、系统日志（syslog/journalctl）、核心转储文件
   - 方案族：日志分析、故障现场保留、人工介入诊断

2. **标准错误被重定向或丢失**：
   - 转向：检查文件描述符配置、重定向目标、日志文件
   - 方案族：输出捕获修复、日志恢复、执行环境检查

3. **沙箱环境不支持系统调用**（容器化、虚拟化环境）：
   - 转向：使用应用层隔离（Python虚拟环境、Docker容器）、调整安全策略
   - 方案族：容器化执行、权限策略调整、替代隔离方案

4. **超时阈值无法准确设定**（任务复杂度未知）：
   - 转向：使用渐进式超时（先短后长）、动态调整策略
   - 方案族：自适应超时、任务分解、资源监控

### 异常处理

- **信号处理冲突**：避免与已有信号处理器冲突，使用sigaction()替代signal()
- **资源泄漏风险**：超时终止后必须清理子进程、关闭文件描述符、释放锁
- **并发执行竞争**：多进程环境注意文件锁、端口占用、共享资源竞争

## 质量检查

### 验证点

1. **退出码采集完整性**：确认获取到有效的退出码整数值
2. **错误分类准确性**：退出码与错误类别精确匹配，无模糊归类
3. **stderr捕获完整性**：标准错误输出完整保存，无截断或丢失
4. **超时处理有效性**：超时后进程正确终止，资源完全释放
5. **沙箱隔离有效性**：隔离环境满足安全要求，功能未受过度限制
6. **恢复策略正确性**：恢复路径与故障类型匹配，重试逻辑合理

### 阈值

- 退出码解析成功率：100%（必须获取有效退出码）
- stderr捕获完整率：100%（必须完整保存错误输出）
- 超时处理成功率：100%（超时后必须正确清理）
- 沙箱配置合规率：100%（必须满足安全策略要求）

### 失败处理

- 退出码采集失败：记录系统日志，报告人工诊断
- stderr捕获失败：检查文件描述符，恢复输出流
- 超时处理失败：强制终止进程，记录故障现场
- 沙箱配置失败：回退到默认安全策略，记录违规尝试

## 回退策略

### 逐级降级方案

1. **完整诊断**：退出码+stderr+日志+环境信息 → 精准定位
2. **基础诊断**：退出码+stderr → 快速分类
3. **最小诊断**：仅退出码 → 基本状态判断
4. **故障报告**：无法获取任何诊断信息 → 记录故障现象，报告人工处理

### 备选执行通道

- Python subprocess → shell命令执行
- 本地执行 → 远程SSH执行
- 直接执行 → 容器化执行
- 同步执行 → 异步执行

## 资源召回建议

### 何时应召回本卡片

- CLI工具返回非零退出码需要诊断
- 进程执行超时需要处理
- 需要在隔离环境中执行不信任的命令
- 多个CLI工具需要统一的错误处理策略
- 需要构建可复用的CLI执行框架

### 配套资源

- `general-json-schema-report-contract`：JSON Schema报告交付契约，用于验证CLI输出格式
- 领域特定知识卡片：根据具体CLI工具类型召回对应领域知识

## 补充证据（开源文档/用户自有，可选）

[D1] The Open Group Base Specifications Issue 7, 2018 edition - exit, IEEE/The Open Group, 2018, URL: https://pubs.opengroup.org/onlinepubs/9699919799/functions/exit.html（accessed_at 2026-09-17，POSIX标准权威文档）

[D2] subprocess — Subprocess management, Python Software Foundation, 3.14.7, URL: https://docs.python.org/3/library/subprocess.html（accessed_at 2026-09-17，Python官方文档）

[D3] sysexits(3) - FreeBSD Manual Pages, FreeBSD Project, 15.1, URL: https://www.freebsd.org/cgi/man.cgi?query=sysexits&sektion=3（accessed_at 2026-09-17，BSD标准参考）

[D4] exit(3) - Linux manual page, Linux man-pages project, latest, URL: https://man7.org/linux/man-pages/man3/exit.3.html（accessed_at 2026-09-17，Linux实现参考）

[D5] os — Miscellaneous operating system interfaces, Python Software Foundation, 3.14.7, URL: https://docs.python.org/3/library/os.html（accessed_at 2026-09-17，进程管理参考）

[D6] Subprocesses — asyncio, Python Software Foundation, 3.14.7, URL: https://docs.python.org/3/library/asyncio-subprocess.html（accessed_at 2026-09-17，异步执行参考）

[D7] The Open Group Base Specifications Issue 7, 2018 edition - alarm, IEEE/The Open Group, 2018, URL: https://pubs.opengroup.org/onlinepubs/9699919799/functions/alarm.html（accessed_at 2026-09-17，超时处理参考）

## 批次补充 2026-09-17（任务410案例）
### 任务410的CLI非交互执行故障分类知识补充
**知识缺口**：CLI 非交互执行与故障分类知识：覆盖命令参数、认证、沙箱、超时、退出码和标准错误判读
**知识缺失证据**：归因分析 CLI 未正常退出或未产生有效响应
**知识内容与边界**：覆盖命令参数、认证、沙箱、超时、退出码和标准错误判读，不扩展到任务领域结论
**应用动作**：依据故障类别修正启动配置或恢复策略
**预期修复点**：归因分析进程稳定完成并保留诊断证据
**验证方式**：使用成功、非零退出和超时用例验证状态及日志

**具体故障案例分析**：
- **任务背景**：难熔高熵合金位错迁移与短程有序分析（任务410）
- **故障现象**：归因分析智能体退出码为 1；报告校验错误：缺少顶层字段: ['issues', 'summary', 'task', 'task_id']；包含额外顶层字段: ['error', 'sessionID', 'timestamp', 'type']；task_id 与任务索引不一致；task 与任务 name 不一致；summary 必须是非空字符串；issues 必须是数组
- **错误类别**：CLI执行故障（退出码1）+ JSON Schema契约违反（必填字段缺失+额外字段+身份不匹配）
- **诊断步骤**：
  1. 检查CLI进程退出码：退出码1表示一般错误
  2. 分析标准错误输出：包含报告校验错误详情
  3. 检查产物目录：发现agent-events.log、agent-final.txt、agent-stderr.log等诊断文件
  4. 验证JSON Schema契约：确认必填字段和额外字段问题
  5. 检查任务身份匹配：确认task_id和task字段一致性

**恢复策略**：
1. **CLI执行诊断**：使用subprocess.run()捕获退出码和stderr，记录完整执行日志
2. **故障分类**：退出码1 → 应用程序定义错误，需检查具体错误原因
3. **JSON Schema校验**：在报告生成后立即进行Schema校验，确保必填字段完整
4. **身份字段同步**：从输入参数同步task_id和task字段，确保与任务索引一致
5. **额外字段清理**：移除Schema未定义的调试字段（error、sessionID、timestamp、type）

**预防措施**：
1. 在CLI执行前进行预检，确保命令参数正确
2. 使用沙箱执行隔离，防止故障扩散
3. 实现超时处理机制，避免进程挂起
4. 集成JSON Schema校验，确保输出符合契约
5. 建立标准化错误分类和恢复流程

**任务410特定问题**：
- **错误模式**：与任务83相同的JSON Schema契约违反模式，但发生在不同任务领域（难熔高熵合金）
- **教训**：CLI执行故障和JSON Schema契约校验应独立于任务领域，作为通用质量门禁
- **改进建议**：建立统一的归因分析框架，内置CLI执行监控和JSON Schema校验

## 批次补充 2026-09-17（任务92案例）
### 任务92的CLI非交互执行故障分类知识补充
**知识缺口**：CLI 非交互执行与故障分类知识：覆盖命令参数、认证、沙箱、超时、退出码和标准错误判读
**知识缺失证据**：归因分析 CLI 未正常退出或未产生有效响应
**知识内容与边界**：覆盖命令参数、认证、沙箱、超时、退出码和标准错误判读，不扩展到任务领域结论
**应用动作**：依据故障类别修正启动配置或恢复策略
**预期修复点**：归因分析进程稳定完成并保留诊断证据
**验证方式**：使用成功、非零退出和超时用例验证状态及日志

**具体故障案例分析**：
- **任务背景**：蛋白质多构象状态空间生成与筛选（任务92）
- **故障现象**：归因分析智能体退出码为 1；报告校验错误：缺少顶层字段: ['issues', 'summary', 'task', 'task_id']；包含额外顶层字段: ['error', 'sessionID', 'timestamp', 'type']；task_id 与任务索引不一致；task 与任务 name 不一致；summary 必须是非空字符串；issues 必须是数组
- **错误类别**：CLI执行故障（退出码1）+ JSON Schema契约违反（必填字段缺失+额外字段+身份不匹配）
- **诊断步骤**：
  1. 检查CLI进程退出码：退出码1表示一般错误
  2. 分析标准错误输出：包含报告校验错误详情
  3. 检查产物目录：发现agent-events.log、agent-final.txt、agent-stderr.log等诊断文件
  4. 验证JSON Schema契约：确认必填字段和额外字段问题
  5. 检查任务身份匹配：确认task_id和task字段一致性

**恢复策略**：
1. **CLI执行诊断**：使用subprocess.run()捕获退出码和stderr，记录完整执行日志
2. **故障分类**：退出码1 → 应用程序定义错误，需检查具体错误原因
3. **JSON Schema校验**：在报告生成后立即进行Schema校验，确保必填字段完整
4. **身份字段同步**：从输入参数同步task_id和task字段，确保与任务索引一致
5. **额外字段清理**：移除Schema未定义的调试字段（error、sessionID、timestamp、type）

**预防措施**：
1. 在CLI执行前进行预检，确保命令参数正确
2. 使用沙箱执行隔离，防止故障扩散
3. 实现超时处理机制，避免进程挂起
4. 集成JSON Schema校验，确保输出符合契约
5. 建立标准化错误分类和恢复流程

**任务92特定问题**：
- **错误模式**：与任务83、任务410相同的JSON Schema契约违反模式，但发生在不同任务领域（蛋白质多构象状态空间生成与筛选）
- **教训**：CLI执行故障和JSON Schema契约校验应独立于任务领域，作为通用质量门禁
- **改进建议**：建立统一的归因分析框架，内置CLI执行监控和JSON Schema校验
- **特殊考虑**：对于生物信息学任务（蛋白质多构象状态空间生成），可能需要考虑构象采样算法、能量函数计算和状态空间搜索的特殊参数

## 证据来源

[D1] The Open Group Base Specifications Issue 7, 2018 edition - exit, IEEE/The Open Group, 2018
[D2] subprocess — Subprocess management, Python Software Foundation, 2024
[D3] sysexits(3) - FreeBSD Manual Pages, FreeBSD Project, 2024
[D4] exit(3) - Linux manual page, Linux man-pages project, 2024
[D5] os — Miscellaneous operating system interfaces, Python Software Foundation, 2024
[D6] Subprocesses — asyncio, Python Software Foundation, 2024
[D7] The Open Group Base Specifications Issue 7, 2018 edition - alarm, IEEE/The Open Group, 2018
