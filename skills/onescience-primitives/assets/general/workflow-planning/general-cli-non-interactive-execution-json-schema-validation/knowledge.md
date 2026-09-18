# CLI非交互执行与JSON Schema结构化输出验证

## 适用范围

本卡片面向需要非交互式执行命令行程序并产生结构化输出的任务，提供命令参数设计、退出码处理、超时控制和JSON Schema输出验证的通用方法论。适用于自动化流水线、CI/CD管道、批量处理脚本、科学计算工作流等需要可靠执行外部程序并解析其输出的场景。不适用于需要交互式会话或图形界面的程序。

## 输入

- 待执行的CLI程序路径或命令
- 命令行参数列表
- 标准输入数据（可选）
- JSON Schema验证规范（可选）
- 超时时间设置（可选）
- 环境变量配置（可选）

## 输出

- 程序执行返回码（exit code）
- 标准输出内容（stdout）
- 标准错误内容（stderr）
- 结构化输出数据（如果启用JSON Schema验证）
- 执行状态信息（成功/失败/超时）

## 流程节点

### 1. 命令构建与参数验证

**操作**：使用argparse或类似库构建命令行参数，确保参数格式正确、类型匹配。

**参数**：
- 程序路径：使用绝对路径确保可靠性
- 参数列表：使用列表形式传递，避免shell注入风险
- 工作目录：设置cwd参数确保程序在正确位置执行

**工具**：Python subprocess模块、argparse库

**质量门禁**：
- 参数类型验证通过
- 必需参数检查
- 参数值范围验证

### 2. 子进程执行控制

**操作**：使用subprocess.run()执行命令，配置适当的I/O管道和超时控制。

**参数**：
- stdin：标准输入配置（PIPE/DEVNULL/文件）
- stdout/stderr：输出捕获配置
- timeout：超时时间（秒）
- check：是否检查返回码
- shell：是否使用shell执行（谨慎使用）

**工具**：Python subprocess.Popen

**质量门禁**：
- 进程正常启动
- 无死锁风险（使用communicate()而非直接读写管道）
- 资源正确释放（使用上下文管理器）

### 3. 退出码处理与故障分类

**操作**：根据返回码判断执行状态，分类处理不同类型的故障。

**退出码分类**：
- 0：成功执行
- 1-125：程序错误（具体含义由程序定义）
- 126：命令不可执行
- 127：命令未找到
- 128+N：被信号N终止（N=1-128）
- 130：被Ctrl+C终止（SIGINT）
- 143：被SIGTERM终止

**工具**：Python subprocess.CompletedProcess

**质量门禁**：
- 退出码正确解析
- 故障类型准确分类
- 错误信息完整记录

### 4. 超时控制与资源管理

**操作**：设置合理的超时时间，防止程序无限挂起，确保资源及时释放。

**参数**：
- 超时时间：根据任务复杂度设置合理值
- 信号处理：超时后发送SIGTERM，必要时发送SIGKILL
- 进程组管理：使用process_group隔离子进程

**工具**：Python subprocess.TimeoutExpired

**质量门禁**：
- 超时检测准确
- 资源正确清理
- 避免僵尸进程

### 5. 输出捕获与处理

**操作**：捕获stdout和stderr，进行编码转换和内容解析。

**参数**：
- 编码：设置正确的字符编码（默认UTF-8）
- 换行符：统一换行符格式
- 缓冲区：处理管道缓冲区满的情况

**工具**：Python subprocess.PIPE

**质量门禁**：
- 输出完整捕获
- 编码正确转换
- 无数据丢失

### 6. JSON Schema验证

**操作**：对程序输出的JSON数据进行Schema验证，确保结构符合预期。

**参数**：
- Schema定义：JSON Schema文件或字典
- 验证模式：严格/宽松模式
- 错误处理：详细错误信息收集

**工具**：Python jsonschema库

**质量门禁**：
- Schema验证通过
- 必填字段检查
- 类型约束验证
- 格式约束验证

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码0 | 成功 | [D1] | 程序正常完成，无错误 |
| 退出码1-125 | 程序错误 | [D1] | 具体含义由程序定义 |
| 退出码126 | 不可执行 | [D1] | 命令存在但无执行权限 |
| 退出码127 | 未找到 | [D1] | 命令不存在或PATH错误 |
| 退出码128+N | 信号终止 | [D1] | 被信号N终止（POSIX） |
| timeout参数 | 秒 | [D1] | 超时时间，防止无限挂起 |
| check参数 | 布尔 | [D1] | 是否在非零退出码时抛出异常 |
| shell参数 | 布尔 | [D1] | 是否通过shell执行（安全风险） |

### 校准数值

以下数值来自Python标准库实现，供量级校准；其他系统需以自身证据重新锚定：

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| PIPE缓冲区 | 系统默认 | [D1] | 避免使用read()/write()，改用communicate() |
| 默认编码 | UTF-8 | [D2] | JSON标准编码 |
| Schema验证 | 严格模式 | [D4] | 确保输出符合契约 |
| 信号SIGTERM | 15 | [D1] | 默认终止信号 |
| 信号SIGKILL | 9 | [D1] | 强制终止信号（无法捕获） |

## 边界与分流

### 1. 程序不存在或不可执行

**前提**：命令路径正确、权限足够。

**不成立时转向**：
- 使用shutil.which()查找程序路径
- 检查文件权限（os.access）
- 验证PATH环境变量

### 2. 超时时间不足

**前提**：任务复杂度已知，超时设置合理。

**不成立时转向**：
- 动态调整超时时间
- 实现进度监控机制
- 分阶段执行长任务

### 3. 输出编码不匹配

**前提**：程序输出使用预期编码。

**不成立时转向**：
- 尝试多种编码（UTF-8, GBK, Latin-1）
- 使用errors='replace'或'ignore'
- 记录编码警告但继续处理

### 4. JSON Schema验证失败

**前提**：输出格式符合Schema定义。

**不成立时转向**：
- 记录详细验证错误
- 尝试宽松解析模式
- 输出部分有效数据并标记异常

### 5. 内存不足

**前提**：系统资源充足。

**不成立时转向**：
- 使用流式处理替代全量加载
- 设置输出大小限制
- 分批处理大数据

## 质量检查

### 验证点

1. **返回码验证**：检查退出码是否在预期范围内
2. **输出完整性**：确认stdout/stderr完整捕获
3. **编码正确性**：验证字符编码转换无误
4. **Schema合规性**：JSON输出通过Schema验证
5. **资源清理**：进程正确终止，无残留资源
6. **错误处理**：异常情况有明确处理路径

### 阈值

- 返回码：0为成功，非0需分析原因
- 超时：根据任务设定合理阈值（默认300秒）
- 输出大小：设置合理上限防止内存溢出
- 验证失败率：目标<1%

### 失败处理

- 返回码异常：记录错误详情，尝试重试或降级
- 超时：强制终止进程，记录超时信息
- 编码错误：使用宽松模式，记录警告
- Schema失败：输出原始数据，标记验证失败

## 回退策略

1. **重试机制**：临时性错误自动重试（最多3次）
2. **降级处理**：主要方案失败时使用备选方案
3. **部分成功**：允许部分数据有效，标记异常部分
4. **手动干预**：复杂错误记录详细日志供人工分析
5. **资源释放**：确保异常情况下仍能正确清理资源

## 资源召回建议

**何时应召回本卡片**：
- 需要非交互式执行外部CLI程序
- 程序输出需要结构化验证
- 需要可靠的错误处理和超时控制
- 自动化流水线中的程序执行
- CI/CD管道中的命令执行

**配套资源**：
- `general-json-schema-validation`: JSON Schema验证详细方法
- `general-process-management`: 进程管理和资源清理
- `general-error-handling-patterns`: 错误处理模式库

## 补充证据（开源权威文档）

[D1] Python subprocess module documentation, Python Software Foundation, v3.14.7, URL: https://docs.python.org/3/library/subprocess.html (accessed_at 2026-09-17, 官方文档)

[D2] Python json module documentation, Python Software Foundation, v3.14.7, URL: https://docs.python.org/3/library/json.html (accessed_at 2026-09-17, 官方文档)

[D3] Python argparse module documentation, Python Software Foundation, v3.14.7, URL: https://docs.python.org/3/library/argparse.html (accessed_at 2026-09-17, 官方文档)

[D4] JSON Schema Understanding JSON Schema, JSON Schema Organization, v2020-12, URL: https://json-schema.org/understanding-json-schema/ (accessed_at 2026-09-17, 官方文档)

## 批次补充 2026-09-17（归因分析任务311案例：CLI执行与JSON Schema报告契约故障）

### 案例描述

任务311（集合数值预报的日内至日前太阳辐照度概率后处理）的归因分析智能体未能交付有效的结构化报告，故障模式与任务274、任务395、任务75、任务281、任务292高度相似：

- **故障现象**：CLI进程退出码为1，报告校验错误：缺少顶层字段 `['issues', 'summary', 'task', 'task_id']`；包含额外顶层字段 `['error', 'sessionID', 'timestamp', 'type']`；task_id与任务索引不一致；task与任务name不一致。
- **故障分类**：CLI非交互执行失败 + JSON Schema报告交付契约违反
- **根因分析**：
  1. CLI进程未正常退出（退出码1），可能由参数错误、认证失败、沙箱隔离或超时引起
  2. 输出报告不符合预定义Schema，缺少必填字段且包含未声明字段
- **修复方法**：
  1. 修正CLI启动配置，确保命令参数、认证、沙箱设置正确
  2. 在输出前使用JSON Schema校验报告，确保字段完整性和身份一致性
- **验证方式**：使用成功、非零退出和超时用例验证状态及日志；以report-schema.json校验最终输出并执行错配字段反例测试

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 缺失必填字段 | 4 | 任务311案例 | issues, summary, task, task_id |
| 额外字段数 | 4 | 任务311案例 | error, sessionID, timestamp, type |
| 身份校验失败项 | 2 | 任务311案例 | task_id不匹配、task不匹配 |
| 退出码 | 1 | 任务311案例 | 通用错误，catchall for general errors |

## 批次补充 2026-09-17（归因分析任务264案例：CLI执行与JSON Schema报告契约故障）

### 案例描述

任务264（天气与人口变化驱动的城市月日用水需求预测）的归因分析智能体未能交付有效的结构化报告，故障模式与任务274、任务292、任务311高度相似：

- **故障现象**：CLI进程退出码为1，报告校验错误：报告根节点不是JSON对象；JSON语法错误：Unterminated string starting at: line 49 column 37 (char 4820)；报告缺少顶层字段 `['issues', 'summary', 'task', 'task_id']`。
- **故障分类**：CLI非交互执行失败 + JSON Schema报告交付契约违反
- **根因分析**：
  1. CLI进程未正常退出（退出码1），输出报告JSON解析失败，可能是输出流被截断或格式错误
  2. 输出报告不符合预定义Schema，缺少必填字段
- **修复方法**：
  1. 修正CLI启动配置，确保命令参数、认证、沙箱设置正确
  2. 增加输出缓冲区和完整性检查，确保JSON输出完整
  3. 在输出前使用JSON Schema校验报告，确保字段完整性和身份一致性
- **验证方式**：使用成功、非零退出和超时用例验证状态及日志；以report-schema.json校验最终输出并执行错配字段反例测试

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 缺失必填字段 | 4 | 任务264案例 | issues, summary, task, task_id |
| JSON解析错误位置 | line 49 column 37 | 任务264案例 | Unterminated string |
| 退出码 | 1 | 任务264案例 | 通用错误，catchall for general errors |

## 批次补充 2026-09-18（归因分析任务232案例：CLI执行与JSON Schema报告契约故障）

### 案例描述

任务232（全球航空危险云微物理要素1—7天预报）的归因分析智能体未能交付有效的结构化报告，故障模式与任务311、任务264、任务274、任务292、任务75、任务281高度相似：

- **故障现象**：CLI进程退出码为1，报告校验错误：缺少顶层字段 `['issues', 'summary', 'task', 'task_id']`；包含额外顶层字段 `['error', 'sessionID', 'timestamp', 'type']`；task_id与任务索引不一致；task与任务name不一致；summary必须是非空字符串；issues必须是数组。
- **故障分类**：CLI非交互执行失败 + JSON Schema报告交付契约违反
- **根因分析**：
  1. CLI进程未正常退出（退出码1），可能由参数错误、认证失败、沙箱隔离或超时引起
  2. 输出报告不符合预定义Schema，缺少必填字段且包含未声明字段，身份字段与任务索引/名称不匹配
- **修复方法**：
  1. 修正CLI启动配置，确保命令参数、认证、沙箱设置正确
  2. 在输出前使用JSON Schema校验报告，确保字段完整性和身份一致性
  3. 确保task_id与任务索引一致、task与任务name一致
- **验证方式**：使用成功、非零退出和超时用例验证状态及日志；以report-schema.json校验最终输出并执行错配字段反例测试

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 缺失必填字段 | 4 | 任务232案例 | issues, summary, task, task_id |
| 额外字段数 | 4 | 任务232案例 | error, sessionID, timestamp, type |
| 身份校验失败项 | 2 | 任务232案例 | task_id不匹配、task不匹配 |
| 退出码 | 1 | 任务232案例 | 通用错误，catchall for general errors |

## 证据来源

[1] Python subprocess module documentation, Python Software Foundation, 2026, https://docs.python.org/3/library/subprocess.html
[2] Python json module documentation, Python Software Foundation, 2026, https://docs.python.org/3/library/json.html
[3] Python argparse module documentation, Python Software Foundation, 2026, https://docs.python.org/3/library/argparse.html
[4] JSON Schema Understanding JSON Schema, JSON Schema Organization, 2026, https://json-schema.org/understanding-json-schema/