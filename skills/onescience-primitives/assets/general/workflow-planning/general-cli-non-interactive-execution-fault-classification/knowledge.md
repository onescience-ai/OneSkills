# CLI非交互执行与故障分类通用方法

## 适用范围
面向任何需要通过命令行接口（CLI）工具执行自动化任务的场景，包括脚本调用、工作流编排、批量处理、持续集成等。适用于Python subprocess模块、shell命令执行、外部工具集成等。不适用于交互式命令行（如REPL）或图形界面工具。

## 输入
- 命令行工具或脚本路径
- 命令参数序列
- 工作目录（可选）
- 环境变量（可选）
- 输入数据（通过stdin管道传递）
- 超时设置（可选）

## 输出
- 进程返回码（exit code）
- 标准输出（stdout）
- 标准错误（stderr）
- 异常信息（如TimeoutExpired, CalledProcessError）
- 故障分类与诊断信息

## 流程节点
1. **命令构建** → 构建参数序列，避免shell注入风险
2. **进程创建** → 使用subprocess.run或Popen启动子进程
3. **输入重定向** → 通过stdin管道传递输入数据
4. **输出捕获** → 捕获stdout和stderr，支持文本或二进制模式
5. **超时控制** → 设置超时时间，超时后终止进程
6. **返回码检查** → 根据返回码判断成功/失败
7. **异常处理** → 捕获并处理TimeoutExpired、CalledProcessError等异常
8. **资源清理** → 确保子进程终止，释放文件描述符

每步含：操作、参数、工具、质量门禁

## 关键参数
### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| stdin | PIPE | [D1] | 用于向子进程传递输入数据 |
| stdout | PIPE | [D1] | 用于捕获子进程标准输出 |
| stderr | PIPE或STDOUT | [D1] | 用于捕获子进程错误输出，STDOUT可合并到stdout |
| timeout | 秒数 | [D1] | 超时后子进程将被终止并抛出TimeoutExpired异常 |
| check | True/False | [D1] | 为True时，非零返回码将抛出CalledProcessError |
| shell | True/False | [D1] | 为True时通过shell执行，需注意安全风险 |
| text | True/False | [D1] | 为True时以文本模式打开文件对象，进行编码转换 |
| encoding | 字符集 | [D1] | 指定文本模式的编码，如'utf-8' |
| cwd | 路径 | [D1] | 设置子进程的工作目录 |

### 校准数值
以下数值来自Python subprocess模块实践，供量级校准；其他系统需以自身证据重新锚定。
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 典型超时 | 30秒 | [D1] | 网络请求或短任务常用超时值 |
| 缓冲区大小 | -1（系统默认） | [D1] | 默认使用io.DEFAULT_BUFFER_SIZE |
| 返回码0 | 成功 | [D1] | 惯例：0表示成功，非0表示失败 |
| 负返回码 | -N | [D1] | 表示子进程被信号N终止（仅POSIX） |

## 边界与分流
- **shell=True时的参数处理**：当命令包含shell元字符（如管道、通配符）时，必须使用shell=True，但需确保参数正确引用以避免注入。
- **超时处理策略**：超时后需主动终止子进程（proc.kill()），并继续调用communicate()以清理资源。
- **输出缓冲区阻塞**：当使用stdout=PIPE且子进程输出量大时，应使用communicate()而非直接读取，避免死锁。
- **Windows与POSIX差异**：信号处理、进程组、会话创建等行为存在平台差异，需条件判断。
- **环境变量继承**：默认继承父进程环境变量，可通过env参数覆盖，但Windows下需包含%SystemRoot%。

## 质量检查
- **返回码验证**：始终检查返回码，非零返回码应触发错误处理流程。
- **输出完整性**：确保stdout和stderr被完整捕获，避免数据丢失。
- **资源泄漏检查**：确认子进程已终止，文件描述符已关闭。
- **超时有效性**：验证超时设置是否合理，避免过早超时或永不超时。
- **异常处理覆盖**：确保所有可能的异常（OSError, TimeoutExpired, CalledProcessError）都被处理。

## 回退策略
- **子进程无响应**：使用kill()强制终止，然后记录错误。
- **输出过大**：考虑使用临时文件替代管道，或分块读取。
- **环境不兼容**：检测操作系统类型，调整shell参数和信号处理。
- **依赖缺失**：检查可执行文件路径，使用shutil.which()查找。

## 资源召回建议
当遇到以下场景时召回本卡片：
- 需要在自动化脚本中调用外部CLI工具
- CLI工具返回非零退出码需要诊断
- 子进程执行超时需要处理
- 需要捕获和分析CLI工具的输出
- 跨平台CLI调用需要兼容性处理

## 补充证据（开源文档/用户自有，可选）
[D1] subprocess — Subprocess management — Python 3.14.7 documentation, Python Software Foundation, 3.14.7, URL: https://docs.python.org/3/library/subprocess.html（accessed_at 2026-09-17，权威文档）

## 证据来源
[D1] subprocess — Subprocess management — Python 3.14.7 documentation, Python Software Foundation, 2026, URL: https://docs.python.org/3/library/subprocess.html

## 批次补充：CLI退出码与故障分类扩展知识

### POSIX标准退出码规范

退出码为8位（0-255），仅最低有效8位通过wait()/waitpid()返回给父进程 [D2]。

| 退出码 | 含义 | 说明 |
|--------|------|------|
| 0 | EXIT_SUCCESS | 成功终止 |
| 非0 | 失败/错误 | 具体含义由应用程序定义 |
| 126 | 命令不可执行 | 权限问题 |
| 127 | command not found | 命令不存在 |
| 128+n | 致命信号n | 如kill -9返回137 (128+9) |
| 130 | Ctrl-C终止 | SIGINT (128+2) |
| 255 | 退出状态越界 | exit -1 |

### BSD sysexits.h 标准化退出码（64-78）

用于C/C++程序的标准化退出码集，适用于结构化错误报告 [D3]：

| 退出码 | 常量 | 含义 |
|--------|------|------|
| 64 | EX_USAGE | 命令行用法错误 |
| 65 | EX_DATAERR | 数据格式错误 |
| 66 | EX_NOINPUT | 无法打开输入 |
| 70 | EXSOFTWARE | 内部软件错误 |
| 71 | EX_OSERR | 系统错误（如无法fork） |
| 73 | EX_CANTCREAT | 无法创建输出文件 |
| 74 | EX_IOERR | 输入/输出错误 |
| 75 | EX_TEMPFAIL | 临时失败，建议重试 |
| 77 | EX_NOPERM | 权限被拒绝 |
| 78 | EX_CONFIG | 配置错误 |

### timeout命令行为（GNU Coreutils）

用于自动化执行中的超时控制 [D4]：

| 退出码 | 含义 |
|--------|------|
| 124 | 命令超时（未指定--preserve-status） |
| 125 | timeout命令本身失败 |
| 137 | 命令被SIGKILL终止 (128+9) |
| 其他 | 命令的原始退出状态 |

关键选项：
- `-s, --signal=SIGNAL`：超时后发送的信号（默认TERM）
- `-k, --kill-after=DURATION`：额外等待后发送KILL信号
- `-p, --preserve-status`：超时后返回命令原始退出状态

### 进程终止状态检查宏

通过waitpid()系统调用获取详细终止信息 [D5]：

| 宏 | 说明 |
|-----|------|
| WIFEXITED(wstatus) | 子进程正常终止 |
| WEXITSTATUS(wstatus) | 获取退出状态（低8位） |
| WIFSIGNALED(wstatus) | 子进程被信号终止 |
| WTERMSIG(wstatus) | 导致终止的信号编号 |
| WCOREDUMP(wstatus) | 子进程产生core dump |

### 资源限制导致的故障

关键资源限制（RLIMIT_*）影响CLI进程失败 [D6]：

| 资源 | 限制 | 超限行为 |
|------|------|----------|
| RLIMIT_CPU | CPU时间（秒） | 超软限制发SIGXCPU，超硬限制发SIGKILL |
| RLIMIT_FSIZE | 最大文件大小 | 超限发SIGXFSZ |
| RLIMIT_AS | 虚拟内存 | 超限ENOMEM |
| RLIMIT_NPROC | 最大进程数 | 超限fork()返回EAGAIN |
| RLIMIT_NOFILE | 最大文件描述符 | 超限EMFILE |

### 信号处理与故障诊断

标准信号及其默认行为 [D7]：

| 信号 | 默认动作 | 说明 |
|------|----------|------|
| SIGTERM | 终止 | 终止信号（可捕获） |
| SIGKILL | 终止 | 强制终止（不可捕获） |
| SIGXCPU | 终止 | CPU时间超限 |
| SIGXFSZ | 终止 | 文件大小超限 |
| SIGSEGV | core dump | 无效内存引用 |
| SIGINT | 终止 | 终端中断（Ctrl-C） |
| SIGPIPE | 终止 | 管道写入无读端 |

### Docker容器退出码

容器化环境中的特殊退出码 [D8]：

| 退出码 | 含义 |
|--------|------|
| 125 | Docker守护进程错误 |
| 126 | 容器命令无法调用 |
| 127 | 容器命令未找到 |
| 其他 | 容器命令的退出码 |

### 故障分类最佳实践

1. **立即检查退出码**：使用$?获取命令执行后的退出状态
2. **使用结构化退出码**：遵循sysexits.h约定（64-78范围）
3. **实现超时机制**：使用timeout命令处理长时间运行进程
4. **监控资源使用**：执行前检查RLIMIT_*值
5. **分离stderr**：将错误输出与正常输出分开处理
6. **记录进程元数据**：记录PID、启动时间、资源限制用于事后分析

### 恢复模式

1. **重试逻辑**：对EX_TEMPFAIL(75)或瞬态错误进行重试
2. **断路器模式**：N次失败后停止重试
3. **优雅降级**：处理SIGXCPU在终止前保存状态
4. **资源监控**：在接近RLIMIT_*边界时告警
5. **超时升级**：使用timeout -k进行渐进式终止

## 批次补充证据
[D2] exit(3) — Linux man page, man7.org, URL: https://man7.org/linux/man-pages/man3/exit.3.html
[D3] sysexits.h(3head) — Linux man page, man7.org, URL: https://man7.org/linux/man-pages/man3/sysexits.h.3head.html
[D4] timeout(1) — Linux man page, man7.org, URL: https://man7.org/linux/man-pages/man1/timeout.1.html
[D5] waitpid(2) — Linux man page, man7.org, URL: https://man7.org/linux/man-pages/man2/waitpid.2.html
[D6] getrlimit(2) — Linux man page, man7.org, URL: https://man7.org/linux/man-pages/man2/getrlimit.2.html
[D7] signal.h — POSIX standard, Open Group, URL: https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/signal.h.html
[D8] Docker exit codes — Docker documentation, URL: https://docs.docker.com/engine/reference/run/#exit-status

## 批次补充：合并CLI故障分类退出码卡片知识（2026-09-17）

### 论文证据补充

从arXiv论文中抽取以下知识，丰富CLI故障分类体系：

**[1] Invalidation Contracts for Cross-Episode Agent Memory (arXiv:2609.00243)**

| 概念 | 描述 | 来源 | 说明 |
|------|------|------|------|
| 失效契约 | 协议层，为每个恢复建议附加版本戳和缓存提示 | [1] | 客户端可无试错地驱逐过期条目 |
| 有效性 | 缓存建议在漂移事件后保持正确的比例 | [1] | 仅取决于协议，与供应商无关 |
| 合规性 | 规划器首次尝试时应用的比例 | [1] | 取决于规划器模型 |
| 版本戳有效性 | 确定性构建，跨所有模型和服务路径产生相同结果 | [1] | 整个评估中零契约失败 |

**[2] Recompilation Is Not Enough: Test-Guided Decompiled-C Repair (arXiv:2609.07201)**

| 概念 | 描述 | 来源 | 说明 |
|------|------|------|------|
| 测试引导修复 | 使用编译器反馈和相关官方测试修复反编译C代码 | [2] | 确保二进制文件行为与原始一致 |
| 退出状态验证 | 重新编译的命令行二进制文件可能返回不同的退出状态 | [2] | 需要通过测试验证行为一致性 |
| 语义修复 | 在编译修复后，通过冒烟检查和测试暴露行为差异 | [2] | 确保功能正确性 |
| 测试门反馈 | 87.5%的二进制文件重新编译并通过测试门 | [2] | 测试引导的LLM辅助修复更可审计 |

**[3] From Intent to Execution Grant: An Execution-Boundary Conformance Profile (arXiv:2609.11596)**

| 概念 | 描述 | 来源 | 说明 |
|------|------|------|------|
| 执行边界一致性配置文件 | 定义AI生成的候选操作是否可获得执行授权 | [3] | 绑定意图对象、策略、证据义务 |
| 执行释放契约 | 验证的ALLOW ERC可能支持单独的执行授权 | [3] | 不是授权承载令牌 |
| 策略非弱化 | 确保策略在执行过程中不会被削弱 | [3] | 保持安全约束完整性 |
| 推导验证 | 验证决策推导的正确性 | [3] | 确保授权决策可追溯 |

### 补充边界与分流

- **API错误恢复**：当CLI工具调用外部API失败时，应实现失效契约机制，为恢复建议附加版本戳，客户端可无试错地驱逐过期条目[1]
- **退出状态验证**：重新编译或修改后的命令行二进制文件，必须通过测试验证其退出状态与原始行为一致[2]
- **执行授权验证**：对于需要执行授权的CLI操作，应实现执行边界一致性配置文件，确保操作符合策略要求[3]
- **缓存一致性**：在多会话环境中，CLI工具应实现缓存失效机制，避免使用过期的恢复建议[1]

### 补充质量检查

- 验证CLI工具在多会话环境中的缓存一致性
- 检查API错误恢复建议的版本戳有效性
- 验证重新编译后的二进制文件退出状态与原始一致
- 确保执行授权决策可追溯和可审计

### 补充回退策略

- **契约失效时**：当失效契约检测到缓存建议过期时，应重新推导恢复建议
- **测试失败时**：当退出状态验证失败时，应检查语义修复是否正确应用
- **授权拒绝时**：当执行授权被拒绝时，应检查策略配置和证据义务

### 补充退出码分类细节

从TLDP退出码文档中抽取以下补充信息，丰富退出码分类体系：

| 退出码 | 含义 | 来源 | 说明 |
|--------|------|------|------|
| 1 | 一般错误 | [D5] | 杂项错误，如除零、权限问题 |
| 2 | Shell内置命令误用 | [D5] | 根据Bash文档，内置命令使用不当 |
| 126 | 命令不可执行 | [D5] | 权限问题或命令不是可执行文件 |
| 127 | 命令未找到 | [D5] | $PATH问题或命令拼写错误 |
| 128 | 无效exit参数 | [D5] | exit只接受0-255的整数参数 |
| 128+n | 致命信号n | [D5] | 进程收到信号n终止，如137=128+9（SIGKILL） |
| 130 | Ctrl+C终止 | [D5] | 脚本被Control-C终止，信号2 |
| 255 | 退出状态超出范围 | [D5] | exit参数超出0-255范围 |

### 补充校准数值

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 用户定义退出码范围 | 64-113 | [D5] | 建议用户自定义退出码使用此范围，避免与系统码冲突 |
| 退出码模运算 | exit 3809 → 225 | [D5] | 3809 % 256 = 225，超出范围的退出码会取模 |
| 保留退出码范围 | 1-2, 126-165, 255 | [D5] | 这些退出码有特殊含义，应避免用户自定义使用 |

### 补充边界与分流

- **超时处理**：当进程执行时间超过阈值时，强制终止并返回超时错误码（如124）
- **资源限制**：内存或CPU超限时，进程可能被系统终止（退出码137=128+9）
- **网络失败**：远程执行时网络中断，可能返回特定错误码或部分输出
- **认证失败**：SSH或API认证失败，通常返回非零退出码
- **沙箱隔离**：在受限环境中执行时，权限错误可能导致退出码126或127

### 补充质量检查

- 验证退出码是否在预期范围内（0-255）
- 检查标准错误输出是否包含有意义的错误信息
- 确认超时设置是否合理（避免过短导致误判，过长导致资源浪费）
- 验证错误分类是否与退出码和错误信息一致

### 补充回退策略

- **重试机制**：对于临时性错误（如网络超时），实现指数退避重试
- **降级执行**：当主要命令失败时，尝试备用命令或简化版本
- **告警通知**：关键任务失败时，发送告警通知（邮件、Slack等）
- **日志记录**：详细记录错误信息、上下文和执行环境，便于后续分析

## 合并证据来源
[1] Invalidation Contracts for Cross-Episode Agent Memory, arXiv:2609.00243, 2026
[2] Recompilation Is Not Enough: Test-Guided Decompiled-C Repair, arXiv:2609.07201, 2026
[3] From Intent to Execution Grant: An Execution-Boundary Conformance Profile, arXiv:2609.11596, 2026
[D5] Exit Codes With Special Meanings, The Linux Documentation Project, Advanced Bash-Scripting Guide Appendix E, 2026