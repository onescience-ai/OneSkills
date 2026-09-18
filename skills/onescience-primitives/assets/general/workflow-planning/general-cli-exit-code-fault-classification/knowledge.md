# CLI 退出码分类与故障诊断

## 适用范围

面向命令行界面工具在非交互模式下的执行监控与故障诊断场景。适用于自动化脚本、CI/CD 流水线、归因分析 CLI 等需要判断进程执行状态并进行故障分类的通用任务，不适用于需要人工交互式调试的场景。

## 输入

- CLI 命令执行的退出码（exit code / return code）
- 进程的 stdout/stderr 输出内容
- 执行环境信息（操作系统、shell 类型）
- 可选：超时配置、信号处理策略

## 输出

- 故障分类结果（成功/可控错误/系统错误/被信号终止）
- 诊断报告（含退出码、错误类型、建议处理策略）
- 修复或恢复动作建议

## 流程节点

1. **进程启动** → 设置执行参数（超时、环境变量、工作目录）
2. **执行监控** → 捕获 stdout/stderr，检测超时
3. **退出码获取** → 获取进程返回码
4. **退出码分类** → 按标准规范进行故障分类
5. **诊断生成** → 生成结构化诊断报告
6. **恢复决策** → 基于分类结果选择重试/降级/终止策略

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 成功退出码 | 0 | [D1] POSIX | 进程正常完成 |
| 应用错误范围 | 1-125 | [D1] POSIX | 程序自定义错误码 |
| 命令不可执行 | 126 | [D1] POSIX | 文件存在但无执行权限 |
| 命令未找到 | 127 | [D1] POSIX | 命令或脚本不存在 |
| 信号终止码 | 128+N | [D1] POSIX | 被信号N终止（如130=SIGINT） |
| Python CalledProcessError | 非零退出码 | [D2] Python | check=True 时抛出 |
| Python TimeoutExpired | 超时秒数 | [D2] Python | timeout 到期时抛出 |

### 校准数值（Python subprocess 实践）

以下数值来自 Python subprocess 模块实践，供量级校准；其他语言或工具需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| PIPE 常量 | -1 或专用值 | [D2] Python | 捕获子进程输出 |
| DEVNULL 常量 | os.devnull | [D2] Python | 丢弃子进程输出 |
| 默认缓冲区 | io.DEFAULT_BUFFER_SIZE | [D2] Python | stdout/stderr 缓冲 |
| Windows 信号 | CTRL_C_EVENT/CTRL_BREAK_EVENT | [D2] Python | Windows 特有信号 |

## 边界与分流

| 前提条件 | 不满足时转向方案 |
|----------|-----------------|
| 进程可正常启动 | 检查命令路径、权限、依赖环境，尝试 OSError 异常捕获 |
| 退出码在 0-255 范围 | 截断为低8位（POSIX 规范），或按平台特性处理 |
| shell=True 可用 | 切换为 shell=False + 参数列表，避免 shell 注入风险 |
| 超时机制有效 | 使用 asyncio.create_subprocess_exec 替代同步等待 |
| stdout/stderr 不阻塞 | 使用 communicate() 而非直接 read/write |

## 质量检查

| 检查点 | 阈值/标准 | 失败处理 |
|--------|----------|----------|
| 退出码解析 | 必须返回整数 | 记录异常值，标记为"未知故障" |
| stderr 内容 | 非空时提取关键错误信息 | 解析失败时保留原始输出 |
| 超时检测 | 超时阈值需匹配任务复杂度 | 超时后 kill() + 重新运行 |
| 信号终止识别 | 检查 128+N 模式 | 记录信号类型，判断是否可重试 |

## 回退策略

1. **进程无法启动** → 检查可执行文件路径、环境变量 PATH、文件权限
2. **退出码异常** → 保留完整 stderr 用于人工审查，不自动重试
3. **超时后重试** → 最多重试 N 次（N 由调用方配置），每次递增超时时间
4. **信号终止** → 检查是否为 SIGPIPE（管道断裂）或 SIGKILL（资源不足），针对性修复

## 资源召回建议

- 当任务涉及 CLI 工具执行时召回本卡片
- 配套召回：general-json-schema-report-contract（用于结构化输出校验）
- 适用于归因分析、自动化测试、流水线执行等场景的故障诊断

## 补充证据（权威文档）

[D1] The Open Group Base Specifications Issue 7 - Shell Command Language, IEEE Std 1003.1-2017, URL: https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html（accessed 2026-09-17，权威标准，交叉验证）

[D2] Python 3.14.7 Documentation - subprocess: Subprocess management, Python Software Foundation, URL: https://docs.python.org/3/library/subprocess.html（accessed 2026-09-17，官方文档，权威来源）

## 证据来源

[D1] The Open Group Base Specifications Issue 7 - Shell Command Language, IEEE/The Open Group, 2018

[D2] Python 3.14.7 Documentation - subprocess: Subprocess management, Python Software Foundation, 2026