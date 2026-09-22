# CLI非交互执行与故障分类

## 适用范围

面向需要在批处理、自动化流水线或无人值守环境中执行外部命令行工具的场景，提供进程管理、超时控制、退出码解读和故障分类的系统化方法。适用于科学计算脚本、数据处理流水线、CI/CD自动化测试等任何需要非交互式调用外部进程的应用。

**不适用场景**：
- 交互式命令行应用（需要用户输入的REPL工具）
- 图形界面应用的进程管理
- 分布式系统中的远程任务调度（需使用专用调度框架）

## 输入

- 待执行的命令行参数序列（字符串列表或字符串）
- 可选的环境变量映射
- 可选的工作目录路径
- 超时时间（秒）
- 输入数据（通过stdin传递）

## 输出

- 进程返回码（整数）
- 标准输出内容（字节或字符串）
- 标准错误内容（字节或字符串）
- 故障分类结果（成功/用户错误/系统错误/信号终止/超时）

## 流程节点

### Step 1：进程启动
- **操作**：使用subprocess.run()或Popen()启动外部命令
- **参数**：args=命令序列, shell=False（推荐）, cwd=工作目录
- **工具**：Python subprocess模块
- **质量门禁**：命令序列正确，避免shell注入风险

### Step 2：输出捕获
- **操作**：设置stdout=PIPE, stderr=PIPE或stderr=STDOUT
- **参数**：capture_output=True或分别指定
- **工具**：subprocess.PIPE, subprocess.DEVNULL
- **质量门禁**：管道缓冲区不溢出，使用communicate()避免死锁

### Step 3：超时控制
- **操作**：设置timeout参数，超时后终止进程
- **参数**：timeout=秒数, 超时后调用proc.kill()
- **工具**：subprocess.TimeoutExpired异常
- **质量门禁**：超时后正确清理进程资源

### Step 4：退出码分类
- **操作**：根据returncode进行故障分类
- **参数**：returncode值分析
- **工具**：条件判断逻辑
- **质量门禁**：正确区分正常退出、异常退出和信号终止

### Step 5：错误诊断
- **操作**：解析stderr内容，提取错误信息
- **参数**：stderr文本分析
- **工具**：正则表达式、关键字匹配
- **质量门禁**：错误信息完整，可追溯到具体故障原因

## 关键参数

### 退出码语义（通用判据）

| 退出码 | 含义 | 分类 | 来源 |
|--------|------|------|------|
| 0 | 成功执行 | SUCCESS | [D1] |
| 1-125 | 用户错误（参数错误、文件不存在等） | USER_ERROR | [D1] |
| 126 | 命令不可执行（权限问题） | PERMISSION_ERROR | [D1] |
| 127 | 命令未找到（路径错误） | COMMAND_NOT_FOUND | [D1] |
| 128+N | 被信号N终止 | SIGNAL_TERMINATED | [D1] |
| 130 | 被SIGINT终止（Ctrl+C） | INTERRUPTED | [D1] |
| 137 | 被SIGKILL终止（强制杀死） | FORCE_KILLED | [D1] |
| 143 | 被SIGTERM终止（优雅终止） | TERMINATED | [D1] |
| 负数 | 被信号N终止（POSIX） | SIGNAL_TERMINATED | [D1] |

### 超时处理策略（校准数值）

| 场景 | 推荐超时值 | 处理方式 | 说明 |
|------|-----------|----------|------|
| 简单CLI工具 | 60秒 | raise TimeoutExpired | 默认策略 |
| 数据处理任务 | 300-3600秒 | kill + 重试 | 根据数据量调整 |
| 长时间计算 | 无超时 | 监控进程状态 | 需外部监控机制 |

以下数值来自典型科学计算场景，供量级校准；其他场景需以自身证据重新锚定。

## 边界与分流

### 前提不成立时的改道方案

| 前提 | 不成立时的改道 |
|------|---------------|
| 命令可本地执行 | 改用远程执行框架（SSH、RPC） |
| 进程可正常终止 | 使用操作系统级强制终止（taskkill/kill -9） |
| 输出可被捕获 | 改用文件重定向而非管道 |
| 超时阈值已知 | 使用自适应超时或心跳检测 |

### 异常处理矩阵

| 异常类型 | 捕获方式 | 恢复策略 |
|---------|---------|---------|
| TimeoutExpired | try/except | kill进程后重试或降级 |
| CalledProcessError | check=True时自动抛出 | 检查returncode分类处理 |
| OSError | try/except | 检查命令路径和权限 |
| BrokenPipeError | 避免使用pipe | 使用communicate()替代直接读写 |

## 质量检查

1. **退出码校验**：每次执行后检查returncode，记录到日志
2. **超时监控**：对长时间运行的进程设置合理超时
3. **输出完整性**：验证stdout/stderr是否完整捕获
4. **资源清理**：确保子进程资源被正确释放
5. **错误分类**：将故障分类为预定义类别，便于自动化处理

## 回退策略

1. **重试策略**：对瞬态故障（网络超时、临时文件冲突）执行指数退避重试
2. **降级策略**：对不可恢复故障，记录错误并跳过当前任务
3. **替代方案**：当CLI工具不可用时，检查是否有等效的库API
4. **诊断证据**：保留完整的stdout/stderr和退出码，用于事后分析

## 资源召回建议

当以下场景出现时应召回本卡片：
- 需要在Python中调用外部命令行工具
- 需要处理CLI工具的非零退出码
- 需要为长时间运行的进程设置超时
- 需要区分不同类型的进程失败原因
- 需要在自动化流水线中集成CLI工具

配套资源：`general-json-schema-report-validation-contract`（报告格式验证）

## 批次补充（2026-09-22：任务45案例补充）

### 实际应用案例

基于归因分析任务（任务ID：45，多功能基序支架蛋白生成）的CLI执行故障案例：

#### CLI执行故障案例
- **故障类型**：归因分析智能体退出码为1
- **错误表现**：归因分析智能体未正常退出，未产生有效的结构化报告
- **诊断方法**：检查agent-events.log、agent-final.txt、agent-stderr.log、analysis-events.jsonl、analysis-stderr.log、blocked-run.log、preflight-evidence.json、report-agent-final.txt
- **修复建议**：检查CLI命令参数、认证、沙箱、超时配置；确保非交互执行环境正确设置

### 故障分类（任务45案例）
1. **退出码分类**：returncode=1 → USER_ERROR（用户错误）
2. **错误类型**：CLI生命周期失败或结构化输出契约失败
3. **错误传播**：CLI启动、超时或结构化输出契约失败，导致工作流逐步对照、领域知识缺口判断和下游优化建议均不可置信
4. **能力归因**：结果生成错误

### 关键发现
- CLI非交互执行失败会导致整个工作流中断
- 退出码为1通常表示用户错误（参数错误、配置错误等）
- 结构化输出契约失败（JSON Schema校验失败）会导致任务无法完成
- 需要保存完整的诊断证据（日志文件）用于事后分析

## 补充证据（开源文档）

[D1] "Python subprocess Module Documentation", Python Software Foundation, version 3.14.7, URL: https://docs.python.org/3/library/subprocess.html（accessed 2026-09-21，官方权威文档，交叉验证）

## 证据来源

[1] Python Software Foundation, "subprocess — Subprocess management", Python 3.14.7 Documentation, https://docs.python.org/3/library/subprocess.html
[2] 基于任务45归因报告中的CLI执行故障案例总结（新增）
