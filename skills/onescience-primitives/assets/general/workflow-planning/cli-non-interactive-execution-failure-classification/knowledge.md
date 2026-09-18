# CLI非交互执行与故障分类

## 适用范围

本卡片为命令行接口（CLI）工具在非交互式执行环境中的故障诊断与恢复提供方法论框架。适用于自动化脚本、批处理任务、CI/CD流水线、远程SSH执行、容器化部署等场景，覆盖退出码解读、超时处理、错误分类与恢复策略。不适用于交互式终端调试或GUI应用错误处理。

## 输入

- **CLI工具**：待执行的命令行程序或脚本
- **执行环境**：操作系统类型（Linux/macOS/Windows）、Shell类型（bash/zsh/cmd/PowerShell）、远程执行上下文
- **配置参数**：命令参数、环境变量、超时设置、重试策略
- **故障信息**：退出码（exit code）、标准错误输出（stderr）、日志文件、系统错误信息

## 输出

- **故障分类报告**：错误类型、严重等级、根因分析
- **恢复建议**：重试策略、配置修正、降级方案
- **诊断证据**：退出码解读、错误日志摘要、环境状态快照

## 流程节点

1. **执行监控** → 记录命令启动时间、进程ID、资源使用
2. **退出码解析** → 根据Shell标准解读退出状态码
3. **错误分类** → 按错误类型（参数错误、资源错误、超时、信号中断等）分类
4. **根因分析** → 结合退出码、错误输出、日志定位故障原因
5. **恢复决策** → 根据故障类型选择重试、跳过、降级或终止
6. **证据归档** → 保存诊断信息供后续分析

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码范围 | 0-255 | [D1] | Shell标准限制，超出部分被截断 |
| 成功退出码 | 0 | [D1] | 表示命令成功执行 |
| 通用错误码 | 1-125 | [D1] | 表示各类执行错误 |
| 信号中断码 | 128+N | [D1] | N为信号编号，如Ctrl+C为130 |
| 命令未找到 | 127 | [D1] | 系统无法找到指定命令 |
| 权限拒绝 | 126 | [D1] | 命令存在但不可执行 |

### 校准数值

以下数值来自Bash和POSIX标准，供量级校准；其他Shell实现需以自身文档重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Bash内置命令错误码 | 2 | [D1] | 表示用法错误（无效选项或缺少参数） |
| Click异常退出码 | 1 | [D2] | Click框架Abort异常默认退出码 |
| Click用法错误退出码 | 2 | [D2] | Click框架UsageError默认退出码 |
| 超时退出码 | 124 | [D1] | timeout命令超时退出码（GNU coreutils） |
| SIGTERM信号编号 | 15 | [D1] | 终止信号，退出码143（128+15） |
| SIGKILL信号编号 | 9 | [D1] | 强制终止信号，退出码137（128+9） |

## 边界与分流

- **Shell差异**：不同Shell（bash/zsh/cmd/PowerShell）退出码语义可能不同，需查阅对应Shell文档
- **跨平台**：Windows命令提示符（cmd.exe）退出码语义与Unix系统不完全一致
- **信号处理**：某些信号（如SIGKILL）无法被捕获或处理
- **超时机制**：需依赖外部工具（如timeout命令）实现，非所有Shell内置
- **嵌套执行**：子进程退出码可能被父进程修改或覆盖

## 质量检查

- 验证退出码是否在0-255范围内
- 检查错误输出是否包含足够的诊断信息
- 确认日志记录是否完整（时间戳、进程ID、环境信息）
- 验证重试策略是否考虑了幂等性
- 检查降级方案是否影响核心功能

## 回退策略

- **退出码不可读**：记录原始返回值，尝试从错误输出推断原因
- **日志缺失**：启用详细模式（-v/--verbose）重新执行
- **环境问题**：检查依赖项、权限、资源限制
- **信号中断**：实现优雅终止，保存中间状态

## 资源召回建议

- 当任务涉及CLI工具自动化执行时召回本卡片
- 当需要诊断CLI工具在批处理或远程环境中的故障时召回本卡片
- 当需要设计CLI工具的错误处理和退出码策略时召回本卡片
- 配套卡片：`cli-json-schema-report-validation`（用于JSON格式报告的验证）

## 补充证据（Python subprocess模块）

[D4] Python subprocess 模块文档提供以下关键知识：

### 退出码语义扩展

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| returncode | 0 | [D4] | 表示子进程成功执行 |
| returncode | 负值 -N | [D4] | 表示子进程被信号N终止（POSIX only） |
| returncode | None | [D4] | 表示进程尚未终止 |
| CalledProcessError.returncode | 非零 | [D4] | check=True时抛出异常 |

### 异常类型分类

| 异常类 | 触发条件 | 来源 | 说明 |
|--------|----------|------|------|
| SubprocessError | 所有子进程异常基类 | [D4] | 继承自Exception |
| CalledProcessError | 进程返回非零退出码 | [D4] | check=True时触发 |
| TimeoutExpired | 超时时间到期 | [D4] | timeout参数触发 |
| OSError | 进程无法启动 | [D4] | 可执行文件不存在或权限问题 |

### 子进程执行最佳实践

- 使用 `subprocess.run()` 替代旧的 `os.system()` 和 `os.popen()`
- `capture_output=True` 可同时捕获 stdout 和 stderr
- `check=True` 可在非零退出码时自动抛出 CalledProcessError
- 使用 `timeout` 参数防止进程挂起
- Windows 平台使用 `creationflags` 控制进程创建行为

## 证据来源

[D1] Bash Reference Manual - Exit Status, GNU Project, https://www.gnu.org/software/bash/manual/html_node/Exit-Status.html (accessed 2026-09-17)
[D2] Click Documentation - Exception Handling and Exit Codes, Pallets Projects, https://click.palletsprojects.com/en/8.1.x/exceptions/ (accessed 2026-09-17)
[D3] POSIX Shell Command Language - Exit Status for Commands, The Open Group, https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html (accessed 2026-09-17)
[D4] Python subprocess 模块文档, Python Software Foundation, https://docs.python.org/3/library/subprocess.html (accessed 2026-09-17)