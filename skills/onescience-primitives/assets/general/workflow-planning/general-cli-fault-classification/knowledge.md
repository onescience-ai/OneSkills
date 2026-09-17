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

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码 0 | 成功 | [1] | 进程正常完成 |
| 退出码 1-2 | 用法错误 | [1] | 参数错误或缺少必要输入 |
| 退出码 126 | 不可执行 | [1] | 命令存在但无执行权限 |
| 退出码 127 | 命令未找到 | [1] | 命令不存在或 PATH 未包含 |
| 退出码 128+N | 信号终止 | [1] | 进程被信号 N 终止（如 SIGKILL=137） |
| 负退出码 -N | 信号终止（POSIX） | [1] | 进程被信号 N 直接终止 |
| 超时异常 | TimeoutExpired | [1] | 进程超过 timeout 未完成 |
| 沙箱错误 | PermissionError | [1] | 沙箱环境权限不足 |
| 认证失败 | 非零退出+auth 关键词 | [1] | API Key/证书无效或过期 |

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

## 质量检查

- **退出码解析准确性**：所有退出码均按 POSIX/Windows 规范解释
- **stderr 关键词覆盖**：至少覆盖 timeout、permission、auth、memory、not found
- **故障分类唯一性**：每个退出码+stderr 组合映射到唯一故障类别
- **恢复策略可执行性**：每个故障类别有明确的恢复动作

## 回退策略

- 当退出码不在已知分类中时，标记为"未知故障"并记录原始退出码和 stderr
- 当 subprocess 本身启动失败（OSError）时，记录环境问题并跳过
- 当多次重试仍失败时，记录最终状态并通知上游

## 资源召回建议

- 当任务涉及 CLI 工具调用且出现非零退出码时召回本卡片
- 配合 `general-json-schema-report-contract` 卡片使用，确保 CLI 输出符合契约
- 适用于 onescience-runtime、onescience-installer 等涉及外部命令执行的技能

## 证据来源

[1] "subprocess — Subprocess management", Python 3.14.7 Documentation, https://docs.python.org/3/library/subprocess.html
[2] "The Open Group Base Specifications Issue 7 - exit", IEEE Std 1003.1-2017, https://pubs.opengroup.org/onlinepubs/9699919799/functions/exit.html
