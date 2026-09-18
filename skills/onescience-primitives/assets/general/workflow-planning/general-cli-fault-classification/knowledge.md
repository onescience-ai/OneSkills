# CLI 非交互执行与故障分类

## 适用范围

**触发条件**：
- 自动化流水线需要通过 CLI 启动外部工具进程
- CLI 进程未正常退出或未产生有效响应
- 需要分类故障原因以指导恢复策略

**适用场景**：
- 归因分析 CLI 执行失败诊断
- 数据处理/模型推理 CLI 超时或崩溃分析
- 自动化测试中外部工具调用的错误处理
- SLURM/SSH 远程环境中非交互式命令执行

**不适用场景**：
- 交互式终端会话（用户直接操作的命令行）
- 纯 Python 函数调用（无需子进程）
- 图形界面应用的故障诊断

## 输入

- **CLI 命令**：待执行的命令字符串或参数列表
- **执行环境**：本地/远程 SSH/SLURM/沙箱
- **超时设置**：最大允许执行时间（秒）
- **认证凭据**：API Key、证书、令牌等（如需）

## 输出

- **退出码**：整数，表示进程结束状态
- **stdout**：标准输出内容
- **stderr**：标准错误内容
- **故障类别**：结构化标签（见故障分类表）
- **诊断日志**：包含退出码、stderr 摘要、耗时

## 流程节点

### Step 1：进程启动
- **操作**：使用 Python subprocess.run() 或 Popen() 启动 CLI
- **参数**：args（命令参数列表）、shell=False（安全）、capture_output=True、text=True
- **工具**：Python subprocess 模块
- **质量门禁**：进程成功创建，无 OSError

### Step 2：执行监控
- **操作**：设置超时，等待进程完成
- **参数**：timeout（秒），建议根据任务类型设置（轻量级 30s，普通 300s，计算级 3600s）
- **工具**：subprocess.run(timeout=N) 或 Popen.communicate(timeout=N)
- **质量门禁**：无 TimeoutExpired 异常

### Step 3：退出码解析
- **操作**：检查 returncode 语义
- **参数**：returncode 值
- **工具**：Python int 比较
- **质量门禁**：退出码属于已知分类

### Step 4：stderr 判读
- **操作**：分析标准错误内容，提取关键错误信息
- **参数**：stderr 文本
- **工具**：正则表达式匹配、关键词检测
- **质量门禁**：错误信息可追溯到具体原因

### Step 5：故障分类
- **操作**：根据退出码 + stderr 组合判定故障类别
- **参数**：退出码、stderr 内容、执行耗时
- **工具**：故障分类规则表（见下文）
- **质量门禁**：分类结果唯一且可操作

### Step 6：恢复策略执行
- **操作**：根据故障类别选择恢复动作
- **参数**：故障类别、重试次数
- **工具**：重试逻辑、配置修正、降级策略
- **质量门禁**：恢复动作可执行

## 关键参数

### 通用判据（方法层）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码 0 | 成功 | [1][D1][D2] | 进程正常完成 |
| 退出码 1-2 | 用法错误 | [1][D1][D2] | 参数错误或缺少必要输入 |
| 退出码 126 | 不可执行 | [1][D1][D2] | 命令存在但无执行权限 |
| 退出码 127 | 命令未找到 | [1][D1][D2] | 命令不存在或 PATH 未包含 |
| 退出码 128+N | 信号终止 | [1][D1][D2] | 进程被信号 N 终止（如 SIGKILL=137） |
| 负退出码 -N | 信号终止（POSIX） | [1][D1] | 进程被信号 N 直接终止 |
| 超时异常 | TimeoutExpired | [1][D2] | 进程超过 timeout 未完成 |
| 认证失败 | 非零退出+auth 关键词 | [1][D2] | API Key/证书无效或过期 |
| 沙箱错误 | PermissionError | [1][D2] | 沙箱环境权限不足 |
| 用户定义退出码范围 | 64-113 | [D1] | 建议用户定义的退出码限制在此范围内 |
| 退出码模 256 | exit 3809 → 225 | [D1] | 大于 255 的退出值返回模 256 的结果 |

### 校准数值（实例参考值）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| SIGKILL 退出码 | 128+9=137 | [D1][D2] | kill -9 的典型退出码 |
| SIGTERM 退出码 | 128+15=143 | [D1][D2] | kill -15 的典型退出码 |
| SIGINT 退出码 | 128+2=130 | [D1][D2] | Ctrl+C 的典型退出码 |

## 边界与分流

### 故障分类规则表

| 退出码 | stderr 关键词 | 故障类别 | 恢复策略 |
|--------|---------------|----------|----------|
| 0 | 无 | 成功 | 无需恢复 |
| 1 | 参数/usage/invalid | 参数错误 | 检查命令参数格式 |
| 1 | auth/unauthorized/401/403 | 认证失败 | 刷新凭据或检查权限 |
| 1 | permission/denied/access | 权限不足 | 检查文件/目录权限或沙箱配置 |
| 1 | memory/OOM/allocat | 资源不足 | 增加内存或减少并发 |
| 126 | permission | 不可执行 | chmod +x 或检查路径 |
| 127 | not found | 命令未找到 | 安装工具或修正 PATH |
| 128+9 | SIGKILL | 强制终止（OOM） | 增加内存或限制输入规模 |
| 128+15 | SIGTERM | 正常终止 | 检查是否主动终止或超时 |
| TimeoutExpired | 无 | 超时 | 增加 timeout 或优化任务 |
| OSError | No such file | 启动失败 | 检查命令路径或环境 |

### 降级策略
- 超时 → 重试 1 次（timeout × 2）→ 失败则记录并跳过
- OOM → 减少并发数或输入规模 → 重试
- 认证失败 → 不重试，记录并告警
- 命令未找到 → 不重试，记录并报告环境问题
- 沙箱限制 → 检查权限配置或申请资源配额 → 重试

## 质量检查

- **退出码解析准确性**：所有退出码均按 POSIX/Windows 规范解释
- **stderr 关键词覆盖**：至少覆盖 timeout、permission、auth、memory、not found
- **故障分类唯一性**：每个退出码+stderr 组合映射到唯一故障类别
- **恢复策略可执行性**：每个故障类别有明确的恢复动作
- **认证失败检测**：检查 stderr 中的 auth/unauthorized/401/403 关键词
- **沙箱限制诊断**：检查 stderr 中的 permission/denied/access/sandbox 关键词

## 回退策略

- 当退出码不在已知分类中时，标记为"未知故障"并记录原始退出码和 stderr
- 当 subprocess 本身启动失败（OSError）时，记录环境问题并跳过
- 当多次重试仍失败时，记录最终状态并通知上游

## 资源召回建议

- 当任务涉及 CLI 工具调用且出现非零退出码时召回本卡片
- 配合 `general-json-schema-report-contract` 卡片使用，确保 CLI 输出符合契约
- 适用于 onescience-runtime、onescience-installer 等涉及外部命令执行的技能

## 补充证据

[D1] Exit Codes With Special Meanings, The Linux Documentation Project, Advanced Bash-Scripting Guide, URL: https://tldp.org/LDP/abs/html/exitcodes.html (accessed 2026-09-17, 权威文档)
[D2] Python subprocess - Subprocess management, Python Software Foundation, Python 3.14.7, URL: https://docs.python.org/3/library/subprocess.html (accessed 2026-09-17, 权威文档)

## 证据来源

[1] "subprocess — Subprocess management", Python 3.14.7 Documentation, https://docs.python.org/3/library/subprocess.html
[2] "The Open Group Base Specifications Issue 7 - exit", IEEE Std 1003.1-2017, https://pubs.opengroup.org/onlinepubs/9699919799/functions/exit.html
[D1] Exit Codes With Special Meanings, The Linux Documentation Project, Advanced Bash-Scripting Guide, https://tldp.org/LDP/abs/html/exitcodes.html
[D2] Python subprocess - Subprocess management, Python Software Foundation, Python 3.14.7, https://docs.python.org/3/library/subprocess.html

## 批次补充 2026-09-17（归因分析任务271案例：CLI非交互执行故障）

### 案例描述

任务271（山区近实时雪水当量估计与网格订正）的归因分析智能体未能交付有效的结构化报告，故障模式与任务255、任务362等高度相似：

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
| 缺失必填字段 | 4 | 任务271案例 | issues, summary, task, task_id |
| 额外字段数 | 4 | 任务271案例 | error, sessionID, timestamp, type |
| 身份校验失败项 | 2 | 任务271案例 | task_id不匹配、task不匹配 |
| 退出码 | 1 | 任务271案例 | 通用错误，catchall for general errors |

## 批次补充 2026-09-18（归因分析任务277案例：CLI非交互执行故障）

### 案例描述

任务277（有限气象变量驱动的未来7天参考蒸散发预报）的归因分析智能体未能交付有效的结构化报告，故障模式与任务271高度相似：

- **故障现象**：CLI进程退出码为1，报告校验错误：缺少顶层字段 `['issues', 'summary', 'task', 'task_id']`；包含额外顶层字段 `['error', 'sessionID', 'timestamp', 'type']`；task_id与任务索引不一致；task与任务name不一致；summary必须是非空字符串；issues必须是数组。
- **故障分类**：CLI非交互执行失败 + JSON Schema报告交付契约违反
- **根因分析**：
  1. CLI进程未正常退出（退出码1），可能由参数错误、认证失败、沙箱隔离或超时引起
  2. 输出报告不符合预定义Schema，缺少必填字段且包含未声明字段
  3. 归因分析阶段未满足CLI生命周期或结构化报告契约，无法形成可信归因结论
- **修复方法**：
  1. 修正CLI启动配置，确保命令参数、认证、沙箱设置正确
  2. 在输出前使用JSON Schema校验报告，确保字段完整性和身份一致性
  3. 确保归因分析智能体正常退出并产生有效响应
- **验证方式**：使用成功、非零退出和超时用例验证状态及日志；以report-schema.json校验最终输出并执行错配字段反例测试；验证归因分析进程稳定完成并保留诊断证据

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 缺失必填字段 | 4 | 任务277案例 | issues, summary, task, task_id |
| 额外字段数 | 4 | 任务277案例 | error, sessionID, timestamp, type |
| 身份校验失败项 | 2 | 任务277案例 | task_id不匹配、task不匹配 |
| 退出码 | 1 | 任务277案例 | 通用错误，catchall for general errors |
| 额外校验失败项 | 2 | 任务277案例 | summary必须是非空字符串、issues必须是数组 |

### 案例对比分析

任务277与任务271的故障模式高度一致，表明这是归因分析CLI的系统性故障模式：
- **相同点**：退出码1、缺少相同必填字段、包含相同额外字段、身份校验失败
- **不同点**：任务277额外指出了summary和issues的格式约束要求
- **系统性问题**：多个任务出现相同故障，表明CLI启动配置或输出契约存在共性问题
- **修复策略**：需要统一修复CLI启动配置和输出校验逻辑，而非逐个任务单独处理
