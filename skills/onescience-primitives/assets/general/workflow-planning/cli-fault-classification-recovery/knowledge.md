# CLI 故障分类与恢复策略

## 适用范围

面向自动化 CLI 工具执行场景，当进程以非交互方式运行时，根据退出状态、异常类型和标准错误输出分类故障类别，并选择对应的恢复策略。适用于任何通过 subprocess 调用外部命令的自动化工作流，包括科学计算管道、数据分析流水线和 CI/CD 任务。

## 输入

- CLI 命令及其参数
- 可选：超时时间（秒）
- 可选：是否检查退出码（check 参数）
- 可选：是否捕获输出（capture_output 参数）

## 输出

- 故障类别分类（timeout / non-zero-exit / signal-termination / stderr-diagnostic）
- 推荐恢复策略（retry / fix-config / escalate / abort）
- 诊断证据（stdout, stderr, returncode）

## 流程节点

### 1. 进程启动与监控
- **操作**：使用 `subprocess.run()` 或 `subprocess.Popen()` 启动子进程
- **参数**：timeout（超时秒数）、check（是否自动检查退出码）、capture_output（是否捕获输出）
- **工具**：Python subprocess 模块
- **质量门禁**：进程成功启动且未立即崩溃

### 2. 退出状态分类
根据进程终止方式分为四类故障：

| 故障类别 | 触发条件 | 诊断标志 |
|---------|---------|---------|
| **超时** | 进程在 timeout 秒内未完成 | `TimeoutExpired` 异常 |
| **非零退出** | 进程退出码 ≠ 0 | `CalledProcessError` 或 returncode ≠ 0 |
| **信号终止** | 进程被信号杀死 | returncode 为负数（POSIX） |
| **stderr 异常** | 进程正常退出但 stderr 有错误输出 | stderr 非空 |

### 3. 恢复策略选择
根据故障类别选择恢复策略：

| 故障类别 | 推荐策略 | 操作 |
|---------|---------|------|
| 超时 | retry / escalate | 检查资源限制，增加超时或优化命令 |
| 非零退出 | fix-config | 检查参数、认证、沙箱环境 |
| 信号终止 | abort / escalate | 检查系统资源（内存、进程数） |
| stderr 异常 | fix-config | 分析 stderr 内容，修正配置 |

### 4. 诊断证据收集
- **操作**：记录 stdout、stderr、returncode
- **参数**：使用 capture_output=True 确保捕获所有输出
- **工具**：CompletedProcess 对象属性
- **质量门禁**：所有诊断字段非空

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| timeout | 用户指定 | [D1] | 进程超时秒数，到期后触发 TimeoutExpired |
| check | True/False | [D1] | 是否在非零退出时自动抛出 CalledProcessError |
| capture_output | True | [D1] | 是否捕获 stdout 和 stderr |
| returncode | 0/-N/正整数 | [D1] | 0=成功，负数=信号终止（POSIX），正整数=应用错误 |

## 边界与分流

- **超时后进程未终止**：必须调用 `proc.kill()` 或 `proc.terminate()` 强制终止，否则进程成为僵尸进程
- **shell=True 时的退出码**：返回码反映 shell 本身的退出状态（如 `/bin/sh` 的 `128+N`），需查阅 shell 文档
- **Windows 平台差异**：`kill()` 是 `terminate()` 的别名，不区分 SIGTERM 和 SIGKILL
- **管道死锁**：使用 `communicate()` 而非直接读写 `.stdin/.stdout/.stderr`，避免管道缓冲区满导致死锁

## 质量检查

- 进程启动前验证命令路径存在（使用 `shutil.which()`）
- 超时后必须强制终止进程
- 退出码分类后记录诊断证据
- stderr 内容用于细化故障原因

## 回退策略

- `subprocess.run()` 失败时回退到 `Popen()` 手动管理
- 超时重试仍失败时升级人工干预
- 非零退出时检查环境变量、工作目录、认证信息

## 资源召回建议

- 当自动化工作流需要调用外部 CLI 工具时召回本卡片
- 当出现进程超时、非零退出或信号终止时召回本卡片
- 配套资源：`json-schema-report-validation`（输出格式校验）

## 补充证据

[D1] subprocess — Subprocess management — Python 3.14.7 documentation, Python Software Foundation, v3.14.7, URL: https://docs.python.org/3/library/subprocess.html（accessed_at 2026-09-18，权威官方文档）

## 证据来源

[1] subprocess — Subprocess management — Python 3.14.7 documentation, Python Software Foundation, 2026, URL: https://docs.python.org/3/library/subprocess.html
