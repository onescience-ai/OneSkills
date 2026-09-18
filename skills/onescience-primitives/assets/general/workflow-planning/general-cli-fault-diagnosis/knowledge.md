# CLI非交互执行与故障分类诊断

## 适用范围

面向需要在自动化工作流中执行命令行程序的场景，提供进程生命周期管理、退出状态判读、超时处理与故障分类的系统化诊断方法。适用于归因分析CLI、数据处理脚本、模型训练入口等命令行工具的非交互执行环境。不适用于交互式shell会话或图形界面应用。

## 输入

- 命令行程序路径及参数
- 执行环境配置（工作目录、环境变量、超时限制）
- 预期退出码和输出格式

## 输出

- 执行结果状态（成功/失败/超时）
- 标准输出和标准错误内容
- 故障分类和诊断信息

## 流程节点

### 1. 进程启动与参数构建

**操作**：使用subprocess.run()或Popen启动子进程

**参数**：
- `args`：命令参数序列（推荐）或字符串
- `shell`：是否通过shell执行（默认False，安全考虑）
- `cwd`：工作目录
- `env`：环境变量映射
- `timeout`：超时秒数

**工具**：Python subprocess模块

**质量门禁**：
- 优先使用序列形式传递参数，避免shell注入风险
- 使用完整路径指定可执行文件，避免PATH解析歧义
- 禁用`shell=True`除非必须使用shell特性

[D1] Python subprocess官方文档, Python Software Foundation, 3.14.7, URL: https://docs.python.org/3/library/subprocess.html（accessed_at 2026-09-17）

### 2. 输出捕获与管道管理

**操作**：配置标准流重定向

**参数**：
- `stdin`：标准输入（PIPE/DEVNULL/None）
- `stdout`：标准输出（PIPE/DEVNULL/None）
- `stderr`：标准错误（PIPE/STDOUT/None）
- `capture_output`：同时捕获stdout和stderr

**工具**：subprocess.PIPE, subprocess.DEVNULL, subprocess.STDOUT

**质量门禁**：
- 使用communicate()避免管道死锁
- 大数据量输出时避免使用PIPE（内存缓冲）
- 文本模式需指定encoding参数

### 3. 退出码判读与故障分类

**操作**：根据returncode分类故障类型

**关键参数**：

| returncode | 故障类型 | 说明 | 处理建议 |
|------------|----------|------|----------|
| 0 | 成功 | 正常退出 | 继续后续流程 |
| 1 | 通用错误 | 未分类错误 | 检查stderr输出 |
| 2 | 用法错误 | 命令行参数错误 | 检查参数格式 |
| 126 | 权限错误 | 无法执行 | 检查文件权限 |
| 127 | 命令未找到 | 程序不存在 | 检查PATH和程序路径 |
| 128+N | 信号终止 | 被信号N终止 | 检查资源限制 |
| -N | 信号终止 | POSIX信号N | 检查内存/超时 |

[D1] Python subprocess官方文档, Python Software Foundation, 3.14.7（accessed_at 2026-09-17）

### 4. 超时处理与资源清理

**操作**：捕获TimeoutExpired异常并清理资源

**参数**：
- timeout：超时秒数
- kill_timeout：强制终止后等待时间

**工具**：subprocess.TimeoutExpired, Popen.kill(), Popen.terminate()

**质量门禁**：
- 捕获TimeoutExpired后必须调用kill()或terminate()
- 使用communicate()完成管道读取
- Windows上kill()是terminate()的别名

[D1] Python subprocess官方文档, Python Software Foundation, 3.14.7（accessed_at 2026-09-17）

### 5. 异常捕获与诊断信息收集

**操作**：捕获并分类SubprocessError及其子类

**关键参数**：

| 异常类型 | 触发条件 | 诊断要点 |
|----------|----------|----------|
| CalledProcessError | check=True且returncode≠0 | 检查cmd、returncode、output |
| TimeoutExpired | 超时未退出 | 检查timeout、output、stderr |
| OSError | 程序不存在或权限不足 | 检查文件路径和权限 |
| ValueError | 参数无效 | 检查参数类型和组合 |

**工具**：try-except结构, exception attributes

## 关键参数

### 通用判据（方法层）

| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| shell | False | [D1] | 避免shell注入，除非必须使用shell特性 |
| args形式 | 序列 | [D1] | 优先序列，避免手动转义 |
| timeout | 30-300秒 | [D1] | 根据任务复杂度设置 |
| encoding | utf-8 | [D1] | 文本模式统一编码 |
| check | 按需 | [D1] | 需要失败时抛异常 |

### 校准数值（典型场景）

| 场景 | timeout建议 | 说明 |
|------|-------------|------|
| 简单命令 | 10-30秒 | 文件操作、简单计算 |
| 数据处理 | 60-300秒 | 批量转换、格式处理 |
| 模型训练 | 3600+秒 | 训练任务需更长超时 |
| 归因分析 | 60-600秒 | 分析任务复杂度不一 |

## 边界与分流

### 前提条件不成立时的替代方案

| 前提 | 不成立场景 | 替代方案 |
|------|------------|----------|
| shell=False | 必须使用shell管道/通配符 | 使用shlex.quote()转义参数 |
| 完整路径 | 程序在PATH中 | 使用shutil.which()验证路径 |
| 超时足够 | 程序执行时间不确定 | 分阶段超时或进度监控 |
| 内存充足 | 大输出数据 | 使用文件重定向而非PIPE |

### 降级策略

1. **通信失败**：回退到文件I/O模式
2. **超时频繁**：增加超时或分步执行
3. **权限问题**：使用sudo或修改文件权限

## 质量检查

### 验证点

1. 进程成功启动（pid非None）
2. 退出码在预期范围内
3. stdout/stderr内容符合预期格式
4. 无未处理的异常
5. 资源正确清理（管道关闭、进程回收）

### 阈值

- 退出码0视为成功（除非任务明确要求其他值）
- 超时不应超过任务SLA
- stderr不应包含致命错误关键词

### 失败处理

- 非零退出码：记录并分类
- 超时：终止并记录超时信息
- 异常：捕获并转换为结构化错误

## 回退策略

1. **CLI执行失败**：回退到Python API直接调用
2. **环境问题**：回退到容器化执行
3. **资源限制**：回退到分批处理

## 资源召回建议

当遇到以下场景时应召回本卡片：
- 归因分析CLI未正常退出
- 数据处理脚本执行超时
- 模型训练入口返回非零退出码
- 自动化工作流中命令行工具故障

配套资源：
- `json_schema_report_contract`：结构化报告输出规范
- `general-cli-fault-diagnosis`：故障分类参考

## 补充证据

[D1] Python subprocess官方文档, Python Software Foundation, 3.14.7, URL: https://docs.python.org/3/library/subprocess.html（accessed_at 2026-09-17）

## 证据来源

[D1] Python subprocess官方文档, Python Software Foundation, 3.14.7, URL: https://docs.python.org/3/library/subprocess.html