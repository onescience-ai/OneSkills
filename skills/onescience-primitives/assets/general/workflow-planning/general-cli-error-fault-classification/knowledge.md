# CLI 非交互执行退出码语义解读与故障分类

## 适用范围

**触发条件**：
- 需要在自动化流水线（CI/CD、Agent 调度）中调用外部 CLI 工具并可靠判断其成功或失败
- CLI 工具以非零退出码退出，需要将退出码映射为可操作的故障类别
- 需要根据 stderr 内容、超时信号和进程终止原因进行自动化诊断

**适用场景**：
- 归因分析 CLI、数据处理脚本、科学计算工具的自动化调用与故障诊断
- Agent 编排系统中子进程失败后的恢复策略选择
- 超时控制与信号终止的分类处理

**不适用场景**：
- 交互式 CLI 工具的人机对话场景
- 不产生退出码的库函数调用（应使用异常机制）
- 需要深度应用级语义诊断的场景（如数据库连接池耗尽的具体排查）

## 输入

- 进程退出码（returncode）
- stderr 捕获内容
- 超时配置与实际耗时
- 进程启动参数（命令、参数列表）

## 输出

结构化故障分类，包含：
- 故障类别标签（参数错误 / 环境缺失 / 运行时异常 / 超时 / 信号终止 / 成功）
- 推荐恢复动作
- 诊断上下文（退出码、stderr 摘要、信号编号）

## 流程节点

### Step 1：捕获进程退出状态
- **操作**：通过 `subprocess.run()` 或 `Popen` 获取 `returncode`、`stdout`、`stderr`
- **参数**：`capture_output=True` 或显式 `stdout=PIPE, stderr=PIPE`
- **工具**：Python subprocess 模块
- **质量门禁**：进程已终止（returncode 非 None）

### Step 2：退出码区间映射
- **操作**：根据退出码数值区间判定故障大类
- **参数**：退出码映射规则（见关键参数表）
- **工具**：条件分支逻辑
- **质量门禁**：映射结果为预定义故障类别之一

### Step 3：超时与信号检测
- **操作**：检查是否因超时被终止（TimeoutExpired 异常）或因信号终止（returncode < 0）
- **参数**：超时阈值、信号编号
- **工具**：subprocess.TimeoutExpired 异常捕获
- **质量门禁**：超时与信号终止互斥判定

### Step 4：stderr 关键词模式匹配
- **操作**：对 stderr 内容进行关键词扫描，细化故障子类别
- **参数**：关键词模式库（如 "Permission denied"、"No such file"、"ModuleNotFoundError"）
- **工具**：正则表达式匹配
- **质量门禁**：匹配结果与退出码类别一致

### Step 5：生成诊断报告
- **操作**：汇总退出码、stderr 摘要、故障类别和推荐恢复动作
- **参数**：诊断模板
- **工具**：字符串格式化
- **质量门禁**：诊断报告包含故障类别、退出码、推荐动作三个必填字段

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码 = 0 | 成功 | [D1] | 进程正常完成 |
| 退出码 = 1 | 通用应用错误 | [D1] | 应用逻辑层面的失败，需结合 stderr 细化 |
| 退出码 = 2 | 命令用法错误 | POSIX 惯例 | 参数格式或用法不正确 |
| 退出码 = 126 | 权限不足或不可执行 | POSIX 惯例 | 找到文件但无法执行 |
| 退出码 = 127 | 命令未找到 | POSIX 惯例 | PATH 中找不到指定命令 |
| 退出码 128+N | 信号终止 | [D1] | 被编号为 N 的信号终止（如 SIGTERM=15 → 143） |
| returncode < 0 | 信号直接终止 | [D1] | POSIX 平台子进程被信号 N 终止时返回 -N |
| TimeoutExpired | 超时异常 | [D1] | 超时后子进程被 kill，需捕获后重试 communicate() |

### 校准数值（示例体系）

以下数值来自 Python subprocess 标准行为，供量级校准；其他语言或平台的 CLI 工具需以自身文档重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| CalledProcessError.returncode | 非零整数 | [D1] | check=True 时抛出，含 cmd/output/stdout/stderr 属性 |
| TimeoutExpired.timeout | 秒数 | [D1] | 用户指定的超时阈值 |
| TimeoutExpired.output | bytes 或 None | [D1] | 超时前已捕获的 stdout 内容 |
| POSIX 信号编号 SIGTERM | 15 | [D1] | 终止信号，对应退出码 143（128+15） |
| POSIX 信号编号 SIGKILL | 9 | [D1] | 强制终止信号，不可捕获 |

## 边界与分流

- **退出码无意义（进程被 SIGKILL 强杀）**：无法从退出码推断应用层原因，转向系统级诊断（内存不足、OOM killer）
- **stderr 为空但退出码非零**：应用未输出错误信息，转向日志文件或 core dump 分析
- **超时后子进程未终止**：TimeoutExpired 后必须调用 `proc.kill()` 再 `proc.communicate()` 清理，否则管道资源泄漏
- **Windows 平台退出码语义不同**：Windows 不使用 POSIX 信号编号体系，退出码 < 0 无信号含义，需查阅 Win32 API 文档
- **shell=True 时退出码反映 shell 本身**：需额外检查 shell 的退出状态（如 bash 的 $?）

## 质量检查

- 退出码映射覆盖 0–127+N 全区间
- stderr 关键词模式库包含至少 5 种常见故障模式
- 超时场景测试：正常完成、超时触发、超时后 kill 的三种路径
- 信号终止场景测试：SIGTERM、SIGKILL 两种信号

## 回退策略

- 退出码映射失败时，标记为 "unknown_fault" 并保留原始退出码和 stderr 供人工审查
- stderr 捕获失败（如管道断裂）时，标记为 "diagnostic_unavailable"

## 资源召回建议

当任务涉及以下场景时应召回本卡片：
- 在 Agent 流水线中调用外部 CLI 工具（归因分析、数据处理、模型训练脚本等）
- 需要根据 CLI 退出状态选择恢复策略（重试、跳过、降级、终止）
- 需要将 CLI 故障分类为可操作类别以支持自动化诊断

配套卡片：`general-json-schema-report-validation`（结构化报告输出校验）

## 补充证据

[D1] "subprocess — Subprocess management", Python 3.14.7 Documentation, Python Software Foundation, version 3.14.7, URL: https://docs.python.org/3/library/subprocess.html（accessed 2026-09-17，交叉验证：官方文档权威来源）

## 证据来源

[1] Python 3.14 subprocess 模块官方文档，Python Software Foundation, 2026, URL: https://docs.python.org/3/library/subprocess.html
