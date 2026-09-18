# CLI 非交互执行故障分类与诊断

## 适用范围

面向命令行工具在自动化流水线、CI/CD 环境和远程调度系统中的非交互执行场景，提供进程异常退出的分类方法与诊断决策框架。适用于需要理解 CLI 工具退出码语义、参数解析错误类型、超时挂起原因和认证失败模式的工程任务。不适用于交互式终端调试或 GUI 应用程序故障诊断。

## 输入

- CLI 工具的退出码（exit code）
- stderr 输出内容
- 进程信号信息（SIGTERM/SIGKILL/SIGTIMEOUT）
- 参数解析错误消息
- 超时时间阈值配置

## 输出

- 故障分类结果（参数错误/运行时错误/环境错误/超时/认证失败）
- 诊断决策树路径
- 恢复策略建议

## 流程节点

### Step 1：退出码采集
- **操作**：捕获 CLI 进程退出码，区分正常退出与异常退出
- **参数**：exit_code ∈ {0, 1, 2, 126-128+N, 130-139, 255}
- **工具**：进程管理器、shell 脚本
- **质量门禁**：退出码被正确捕获且未被 shell 层截断

### Step 2：退出码分类
- **操作**：按 POSIX 标准与 Python argparse 规范对退出码分类
- **参数**：见关键参数表
- **工具**：分类决策树
- **质量门禁**：分类结果与实际故障原因一致

### Step 3：stderr 语义分析
- **操作**：解析 stderr 输出，提取错误类型与上下文信息
- **参数**：错误关键词匹配模式
- **工具**：正则表达式、日志分析
- **质量门禁**：错误消息被正确归类到对应故障类型

### Step 4：恢复策略选择
- **操作**：根据故障类型选择恢复策略
- **参数**：重试次数、超时调整、参数修正
- **工具**：策略模板
- **质量门禁**：恢复策略在同类故障场景下验证有效

### Step 5：沙箱环境验证（可选）
- **操作**：验证 CLI 工具在隔离沙箱中的执行行为
- **参数**：沙箱类型（Docker、虚拟机、chroot）、资源限制、网络隔离
- **工具**：沙箱管理工具、系统监控
- **质量门禁**：沙箱内外行为一致，无副作用泄漏 [1]

### Step 6：差异测试验证（可选）
- **操作**：使用多层等价性度量比较系统级副作用和终端输出
- **参数**：预期输出（oracle）、比较策略、容差阈值
- **工具**：差异测试框架、输出比较工具
- **质量门禁**：生成软件与参考实现行为等价 [1]

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 正常退出码 | 0 | [D1] | 任务成功完成 |
| 通用错误码 | 1 | [D1] | 运行时错误或未指定错误 |
| 参数/用法错误码 | 2 | [D1][D2] | argparse 解析失败或参数无效 |
| 不可执行文件码 | 126 | [D1] | 文件存在但无执行权限 |
| 命令未找到码 | 127 | [D1] | 可执行文件不存在 |
| 无效退出参数码 | 128+N | [D1] | exit 命令参数无效 |
| SIGINT 中断码 | 130 | [D1] | Ctrl+C 或 kill -INT |
| SIGTERM 终止码 | 143 | [D1] | kill -15 正常终止请求 |
| argparse 参数错误 | 2 | [D2] | parse_args() 遇到无效参数时退出 |

### 校准数值

以下数值来自 POSIX.1-2017 标准与 Python 3.14 argparse 实现，供量级校准；其他 CLI 工具需以自身文档重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| argparse exit_on_error 默认值 | True | [D2] | 参数错误时自动退出，退出码为 2 |
| argparse suggest_on_error | False(默认) | [D2] | 拼写建议功能，默认关闭 |
| argparse add_help 默认值 | True | [D2] | 自动添加 -h/--help 选项 |
| POSIX PATH 搜索顺序 | 从左到右 | [D1] | 按 PATH 变量顺序查找可执行文件 |

## 边界与分流

**关键前提 1**：CLI 工具遵循 POSIX 退出码约定
- **不成立时**：工具使用自定义退出码（如 Windows ERRORLEVEL 语义不同），需查阅工具文档获取专用语义

**关键前提 2**：stderr 输出可被捕获且未被重定向
- **不成立时**：输出被重定向到文件或管道，需检查文件描述符配置；或输出被其他进程截断

**关键前提 3**：进程未被外部信号强制终止
- **不成立时**：进程被 SIGKILL（exit code 137）或 OOM Killer 终止，需检查系统资源限制

**关键前提 4**：沙箱环境配置正确
- **不成立时**：沙箱隔离不充分导致系统级副作用泄漏，需检查文件系统、网络和进程隔离配置 [1]

## 质量检查

- 退出码分类与 stderr 内容一致性验证
- 参数解析错误的详细错误消息检查
- 超时场景下的进程存活状态确认
- 认证失败的凭证有效性二次验证
- 沙箱环境隔离性验证（文件系统、网络、进程）[1]
- 系统级副作用检测（文件创建、网络请求、进程创建）[1]

## 回退策略

- 退出码不明确时：收集完整 stderr + stdout 日志进行人工分析
- 参数错误：使用 --help 或 -h 选项获取用法提示
- 超时故障：增加超时阈值或拆分任务降低单次执行负载
- 认证失败：重新获取凭证或检查凭证过期时间

## 资源召回建议

当遇到以下场景时召回本卡片：
- CLI 工具在自动化流水线中异常退出
- 需要理解 exit code 语义进行故障分类
- argparse 参数解析错误诊断
- 远程作业提交后状态异常
- 沙箱环境配置与验证
- 差异测试与行为等价性验证

配套资源：
- general-json-schema-report-delivery-contract（结构化输出契约）

## 补充证据

[D1] "The Open Group Base Specifications Issue 7 - 8. Environment Variables", IEEE/The Open Group, POSIX.1-2017, URL: https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap08.html (accessed 2026-09-17，交叉验证：exit code 语义与 POSIX 标准一致)
[D2] "argparse — Parser for command-line options, arguments and subcommands", Python Software Foundation, version 3.14.7, URL: https://docs.python.org/3/library/argparse.html (accessed 2026-09-17，交叉验证：argparse 退出行为与 Python 官方文档一致)

## 批次补充（2026-09-18）

[1] Ruida Hu et al., "Evaluating LLM-Based 0-to-1 Software Generation in End-to-End CLI Tool Scenarios", arXiv:2604.06742, 2026. 该论文提出了 CLI-Tool-Bench 基准测试，包含 94 个真实世界 CLI 工具仓库，使用自动化黑盒差异测试框架评估 LLM 生成的 CLI 工具。关键发现：(a) 隔离沙箱执行可检测系统级副作用；(b) 多层等价性度量比较终端输出与预期 oracle；(c) 顶级模型最高成功率仅 43.8%，说明 CLI 工具生成仍是挑战性任务。
[2] Mohammad Masudur Rahman, Chanchal K. Roy, "On the Use of Context in Recommending Exception Handling Code Examples", arXiv:1807.02261, 2018. 该论文提出了上下文感知的异常处理代码推荐方法，关键发现：(a) 结构和词汇特征分析可识别异常处理模式；(b) 启发式质量度量评估异常处理器有效性；(c) 开源代码库可作为异常处理知识来源。

## 证据来源

[1] Ruida Hu, Xinchen Wang, Chao Peng, Cuiyun Gao, David Lo, "Evaluating LLM-Based 0-to-1 Software Generation in End-to-End CLI Tool Scenarios", arXiv:2604.06742, 2026
[2] Mohammad Masudur Rahman, Chanchal K. Roy, "On the Use of Context in Recommending Exception Handling Code Examples", arXiv:1807.02261, 2018
[D1] "The Open Group Base Specifications Issue 7 - 8. Environment Variables", IEEE/The Open Group, POSIX.1-2017
[D2] "argparse — Parser for command-line options, arguments and subcommands", Python Software Foundation, version 3.14.7