# CLI非交互执行与故障分类知识

## 适用范围

适用于所有需要在非交互模式下执行命令行接口（CLI）工具的场景，包括自动化测试、CI/CD流水线、批处理作业和无人值守执行。覆盖故障检测、退出码分类、错误恢复和日志诊断。

## 输入

- CLI命令及其参数
- 执行环境（Windows/Linux/macOS）
- 预期退出码和错误输出格式
- 超时设置和资源限制

## 输出

- 结构化执行结果（退出码、标准输出、标准错误）
- 故障分类（成功/警告/错误/致命）
- 诊断信息和恢复建议

## 流程节点

### 1. 命令解析与验证
- 操作：验证命令参数格式、检查依赖工具是否存在
- 参数：命令字符串、参数列表
- 工具：argparse、shlex
- 质量门禁：参数解析无异常

### 2. 进程创建与执行
- 操作：创建子进程、设置标准流重定向
- 参数：stdin/stdout/stderr管道配置
- 工具：subprocess.Popen、subprocess.run
- 质量门禁：进程成功启动

### 3. 输出捕获与监控
- 操作：读取标准输出和标准错误、监控执行时间
- 参数：超时设置、缓冲区大小
- 工具：communicate()、poll()
- 质量门禁：输出完整捕获、无死锁

### 4. 退出码分类
- 操作：解析返回码、映射到故障类别
- 参数：退出码值、信号信息
- 工具：returncode属性、os.WIFEXITED()
- 质量门禁：退出码正确解析

### 5. 错误恢复与重试
- 操作：根据故障类型执行恢复策略
- 参数：重试次数、退避策略
- 工具：异常处理、日志记录
- 质量门禁：恢复策略有效执行

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码0 | 成功 | [D1] | 命令正常完成 |
| 退出码1-125 | 应用错误 | [D1] | 命令执行失败，具体含义由应用程序定义 |
| 退出码126 | 无法执行 | [D1] | 命令不可执行（权限问题） |
| 退出码127 | 命令未找到 | [D1] | 命令不存在或路径错误 |
| 退出码128+N | 信号终止 | [D1] | 命令被信号N终止（如130=SIGINT） |
| 退出码130 | 用户中断 | [D1] | Ctrl+C终止（SIGINT=2） |
| 退出码137 | 资源限制 | [D1] | 内存不足或超时（SIGKILL=9） |
| 退出码255 | 退出码溢出 | [D1] | 退出码超过255范围 |

### 校准数值（Python特定）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| argparse exit_on_error=True | 默认行为 | [D2] | 参数错误时自动退出并返回状态码2 |
| argparse exit_on_error=False | 异常模式 | [D2] | 参数错误时抛出ArgumentError异常 |
| subprocess.run check=True | 严格模式 | [D3] | 非零退出码抛出CalledProcessError |
| subprocess.run check=False | 宽松模式 | [D3] | 非零退出码不抛出异常 |
| subprocess.TimeoutExpired | 超时异常 | [D3] | 执行超时触发，需手动处理 |
| subprocess.PIPE | 管道捕获 | [D3] | 捕获标准流输出 |
| subprocess.DEVNULL | 丢弃输出 | [D3] | 丢弃标准流输出 |

## 边界与分流

### 参数解析失败
- 症状：argparse抛出ArgumentError或SystemExit(2)
- 处理：检查命令行参数格式、缺失必填参数
- 恢复：修正参数后重试或返回错误码

### 进程启动失败
- 症状：OSError或FileNotFoundError
- 处理：验证命令路径、检查执行权限
- 恢复：使用绝对路径、检查PATH环境变量

### 执行超时
- 症状：TimeoutExpired异常
- 处理：强制终止进程、收集部分输出
- 恢复：增加超时时间或优化命令性能

### 输出管道死锁
- 症状：进程挂起、无响应
- 处理：使用communicate()替代直接读写
- 恢复：设置管道缓冲区大小、异步读取

### 退出码异常
- 症状：退出码不在预期范围
- 处理：检查应用程序日志、分析标准错误
- 恢复：根据错误类型选择重试或跳过

## 质量检查

1. **退出码验证**：确认退出码在0-255范围内
2. **输出完整性**：验证标准输出和标准错误完整捕获
3. **超时控制**：确保执行时间不超过预设限制
4. **资源清理**：确认子进程资源正确释放
5. **日志记录**：记录完整的执行上下文和错误信息

## 回退策略

1. **重试机制**：对于瞬时故障（网络波动、资源竞争），自动重试3次
2. **降级执行**：对于非关键命令，失败时跳过并记录警告
3. **备选方案**：对于不可用命令，提供替代工具或手动步骤
4. **人工干预**：对于致命错误，暂停执行并等待人工处理

## 资源召回建议

当遇到以下场景时召回本卡片：
- CLI工具在自动化流水线中执行失败
- 需要解析和分类命令行退出码
- 需要处理非交互模式下的错误恢复
- 需要诊断CLI执行问题的根本原因

配套资源：
- onescience-runtime：执行环境配置和作业提交
- onescience-installer：环境安装和依赖验证
- onescience-runsite：运行站点配置和验证

## 补充证据（开源权威文档）

[D1] The GNU C Library Manual - Exit Status, Free Software Foundation, v2.44, https://www.gnu.org/software/libc/manual/html_node/Exit-Status.html (accessed_at: 2026-09-16, 单源参考)

[D2] Python argparse Documentation, Python Software Foundation, v3.14.7, https://docs.python.org/3/library/argparse.html (accessed_at: 2026-09-16, 单源参考)

[D3] Python subprocess Documentation, Python Software Foundation, v3.14.7, https://docs.python.org/3/library/subprocess.html (accessed_at: 2026-09-16, 单源参考)

## 证据来源

本文档基于以下权威来源整理：
- Python官方文档（argparse、subprocess模块）
- GNU C库手册（退出状态标准）
- 行业最佳实践（CLI错误处理模式）

## 批次补充（2026-09-17：任务70案例补充）

### 实际应用案例

基于归因分析任务（任务ID：70，深度突变扫描监督的蛋白变异效应预测）的CLI非交互执行故障分类案例：

#### CLI非交互执行故障分类案例
- **故障现象**：归因分析智能体退出码为1，未返回符合Schema的JSON
- **故障分类**：应用错误（退出码1-125），具体含义由应用程序定义
- **错误详情**：CLI启动、超时或结构化输出契约失败，导致工作流逐步对照、领域知识缺口判断和下游优化建议均不可置信
- **修复方法**：依据故障类别修正启动配置或恢复策略；使用成功、非零退出和超时用例验证状态及日志
- **诊断证据**：目录内文件：agent-events.log、agent-final.txt、agent-stderr.log、analysis-events.jsonl、analysis-stderr.log、blocked-run.log、preflight-evidence.json、report-agent-final.txt

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码 | 1 | 任务70案例 | 应用错误，具体含义由应用程序定义 |
| 故障类型 | 应用错误 | 任务70案例 | 退出码1-125范围 |
| 退出码范围 | 1-125 | 任务70案例 | 应用错误，具体含义由应用程序定义 |

## 批次补充（2026-09-17：任务274案例补充）

### 实际应用案例

基于归因分析任务（任务ID：274，干雪雪崩危险等级日尺度预报）的CLI非交互执行故障分类案例：

#### CLI非交互执行故障分类案例
- **故障现象**：归因分析智能体退出码为1，报告校验错误
- **故障分类**：应用错误（退出码1-125），具体含义由应用程序定义
- **错误详情**：
  - 缺少顶层字段：`['issues', 'summary', 'task', 'task_id']`
  - 包含额外顶层字段：`['error', 'sessionID', 'timestamp', 'type']`
  - task_id与任务索引不一致
  - task与任务name不一致
  - summary必须是非空字符串
  - issues必须是数组
- **错误传播**：CLI启动、超时或结构化输出契约失败，导致工作流逐步对照、领域知识缺口判断和下游优化建议均不可置信
- **修复方法**：依据故障类别修正启动配置或恢复策略；使用成功、非零退出和超时用例验证状态及日志
- **诊断证据**：目录内文件：agent-events.log、agent-final.txt、agent-stderr.log、analysis-events.jsonl、analysis-stderr.log、blocked-run.log、preflight-evidence.json、report-agent-final.txt

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码 | 1 | 任务274案例 | 应用错误，具体含义由应用程序定义 |
| 故障类型 | 应用错误 | 任务274案例 | 退出码1-125范围 |
| 缺失字段数 | 4 | 任务274案例 | issues, summary, task, task_id |
| 额外字段数 | 4 | 任务274案例 | error, sessionID, timestamp, type |

## 批次补充（2026-09-17：任务75案例补充）

### 实际应用案例

基于归因分析任务（任务ID：75，空间转录组与蛋白组图基础表征）的CLI非交互执行故障分类案例：

#### CLI非交互执行故障分类案例
- **故障现象**：归因分析智能体退出码为1，报告校验错误
- **故障分类**：应用错误（退出码1-125），具体含义由应用程序定义
- **错误详情**：
  - 缺少顶层字段：`['issues', 'summary', 'task', 'task_id']`
  - 包含额外顶层字段：`['error', 'sessionID', 'timestamp', 'type']`
  - task_id与任务索引不一致
  - task与任务name不一致
  - summary必须是非空字符串
  - issues必须是数组
- **错误传播**：CLI启动、超时或结构化输出契约失败，导致工作流逐步对照、领域知识缺口判断和下游优化建议均不可置信
- **修复方法**：依据故障类别修正启动配置或恢复策略；使用成功、非零退出和超时用例验证状态及日志
- **诊断证据**：目录内文件：agent-events.log、agent-final.txt、agent-stderr.log、analysis-events.jsonl、analysis-stderr.log、blocked-run.log、preflight-evidence.json、report-agent-final.txt

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码 | 1 | 任务75案例 | 应用错误，具体含义由应用程序定义 |
| 故障类型 | 应用错误 | 任务75案例 | 退出码1-125范围 |
| 缺失字段数 | 4 | 任务75案例 | issues, summary, task, task_id |
| 额外字段数 | 4 | 任务75案例 | error, sessionID, timestamp, type |

## 批次补充（2026-09-18：任务CFD_S045案例补充）

### 实际应用案例

基于归因分析任务（任务ID：CFD_S045，符号与稀疏物理学习控制方程发现）的CLI非交互执行故障分类案例：

#### CLI非交互执行故障分类案例
- **故障现象**：归因分析智能体未返回符合Schema的JSON，退出码为1
- **故障分类**：应用错误（退出码1-125），具体含义由应用程序定义
- **错误详情**：
  - 报告根节点不是 JSON 对象
  - JSON 语法错误：Expecting ',' delimiter: line 1 column 6273 (char 6272)
  - 报告校验错误：报告根节点不是 JSON 对象；JSON 语法错误
- **错误传播**：CLI 启动、超时或结构化输出契约失败，导致工作流逐步对照、领域知识缺口判断和下游优化建议均不可置信
- **修复方法**：依据故障类别修正启动配置或恢复策略；使用成功、非零退出和超时用例验证状态及日志
- **诊断证据**：目录内文件：agent-events.log、agent-final.txt、agent-stderr.log、analysis-events.jsonl、analysis-stderr.log、knowledge-agent-final.txt、knowledge-events.jsonl、knowledge-stderr.log、preflight-evidence.json、report-agent-final.txt、report.json

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码 | 1 | CFD_S045案例 | 应用错误，具体含义由应用程序定义 |
| 故障类型 | 应用错误 | CFD_S045案例 | 退出码1-125范围 |
| 错误子类型 | JSON语法错误 | CFD_S045案例 | 非Schema验证，而是JSON解析阶段失败 |
| 错误位置 | line 1 column 6273 | CFD_S045案例 | 字符级定位 |