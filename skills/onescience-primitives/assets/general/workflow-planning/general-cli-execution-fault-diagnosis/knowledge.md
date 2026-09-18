# CLI 执行故障诊断与恢复

## 适用范围

面向命令行工具的非交互执行场景，诊断进程退出异常、超时挂起、标准错误捕获失败等故障，提供分类判据与恢复策略。适用于自动化流水线、CI/CD 集成、批处理任务等需要程序化调用外部 CLI 工具的场景。

## 输入

- CLI 命令及其参数
- 执行环境信息（操作系统、shell 类型、环境变量）
- 进程退出码（returncode）
- 标准输出（stdout）和标准错误（stderr）
- 可选：超时配置、重试策略

## 输出

- 故障分类结果（退出码异常、超时、捕获失败、权限错误等）
- 恢复建议（重试、降级、人工介入）
- 诊断日志（含退出码、stderr 摘要、耗时）

## 流程节点

### 1. 进程启动与参数验证

**操作**：验证命令格式、路径合法性、参数序列正确性
**参数**：
- `args`：命令参数序列（推荐）或单字符串
- `shell`：是否通过 shell 执行（默认 False）
**工具**：subprocess.Popen 或 subprocess.run
**质量门禁**：命令路径存在且可执行；参数无 shell 注入风险

### 2. 超时控制与进程监控

**操作**：设置超时阈值，监控进程状态
**参数**：
- `timeout`：超时秒数（默认 None，无超时）
**工具**：subprocess.Popen.communicate(timeout=N)
**质量门禁**：超时触发后必须清理子进程（kill/terminate）

### 3. 退出码分类

**操作**：根据 returncode 判定故障类别
**参数**：
- `returncode=0`：成功
- `returncode>0`：应用层错误（具体含义由程序定义）
- `returncode<0`：被信号终止（POSIX，-N 表示信号 N）
- `returncode=None`：进程未终止
**工具**：subprocess.CompletedProcess.check_returncode()
**质量门禁**：非零退出码必须触发异常或日志记录

### 4. 标准流捕获与解析

**操作**：捕获 stdout/stderr，解析错误信息
**参数**：
- `stdout=PIPE`：捕获标准输出
- `stderr=PIPE` 或 `stderr=STDOUT`：捕获标准错误
- `text=True`：文本模式（默认二进制）
**工具**：subprocess.PIPE, subprocess.STDOUT
**质量门禁**：管道使用时必须用 communicate() 避免死锁

### 5. 异常分类与恢复

**操作**：根据故障类型选择恢复策略
**参数**：
- `TimeoutExpired`：超时异常，需 kill 子进程并重试
- `CalledProcessError`：非零退出码，需检查 stderr
- `OSError`：系统错误（命令不存在、权限不足）
**工具**：异常类层次结构
**质量门禁**：异常必须被捕获并记录，不得静默吞没

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| returncode | 0 | [D1] | 进程成功退出 |
| returncode | >0 | [D1] | 应用层错误码，具体含义由程序定义 |
| returncode | <0 | [D1] | 被信号终止（POSIX），-N 表示信号 N |
| timeout | None | [D1] | 默认无超时，可能导致进程挂起 |
| shell | False | [D1] | 默认不通过 shell，避免注入风险 |

### 校准数值

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| timeout 推荐值 | 30-300s | [D1] | 根据任务复杂度调整，CLI 工具通常 30-60s 足够 |
| 管道缓冲区 | 64KB | [D1] | stdout/stderr 输出超过此值可能阻塞子进程 |

## 边界与分流

### 超时处理分流

- **前提**：timeout 参数已设置且进程未响应
- **动作**：调用 `proc.kill()` 终止子进程，再调用 `communicate()` 收集输出
- **分流目标**：若 kill 后仍无法清理 → 记录为僵尸进程，报告系统级问题

### 退出码异常分流

- **前提**：returncode 非零
- **动作**：解析 stderr 内容，分类为"命令不存在""权限不足""参数错误""运行时错误"
- **分流目标**：命令不存在 → 检查 PATH；权限不足 → 检查执行权限；参数错误 → 验证输入；运行时错误 → 报告上游

### 捕获失败分流

- **前提**：stdout/stderr 为空或异常
- **动作**：检查进程是否正常退出；若进程被信号终止，尝试从 core dump 或日志获取信息
- **分流目标**：无诊断信息 → 记录为"不可诊断"，建议复现

## 质量检查

| 检查点 | 阈值 | 失败处理 |
|--------|------|----------|
| 命令路径存在 | 存在 | 报错退出，提示安装或检查 PATH |
| 参数序列合法 | 无 shell 注入 | 使用 shlex.quote() 转义 |
| 超时触发清理 | 必须 kill | 强制 kill 后等待 5s，仍失败则记录僵尸进程 |
| 退出码记录 | 非零必须记录 | 写入日志，触发告警或异常 |
| stderr 捕获 | 非空必须解析 | 提取关键错误信息，避免全文输出 |

## 回退策略

1. **命令不存在**：尝试替代命令（如 `python` → `python3`）或提示安装
2. **权限不足**：提示使用 sudo 或修改文件权限
3. **超时挂起**：降低超时阈值，或拆分为多个子任务
4. **管道死锁**：改用 communicate() 而非直接读写 stdin/stdout
5. **输出过大**：使用 DEVNULL 丢弃不需要的输出，或重定向到文件

## 资源召回建议

- 当任务涉及自动化调用外部 CLI 工具时召回本卡
- 配套资源：`general-json-schema-report-delivery-contract`（结构化输出校验）
- 适用场景：CI/CD 流水线、批处理脚本、科学计算工具集成

## 证据来源

[D1] Python subprocess module documentation, Python Software Foundation, v3.14.7, https://docs.python.org/3/library/subprocess.html (accessed 2026-09-17)

[D2] The GNU C Library manual - Exit Status, Free Software Foundation, v2.44, https://www.gnu.org/software/libc/manual/html_node/Exit-Status.html (accessed 2026-09-17)