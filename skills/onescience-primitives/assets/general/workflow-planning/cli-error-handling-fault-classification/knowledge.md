# CLI非交互执行与故障分类

## 适用范围

面向需要在自动化流水线、批处理脚本或无监督环境中运行命令行工具的场景。适用于任何依赖退出码传递状态、标准错误流输出诊断信息的CLI工具，不适用于交互式会话或图形界面应用。

## 输入

- CLI命令及其参数
- 执行环境（shell类型、工作目录、环境变量）
- 预期的输出格式（stdout结构化或非结构化）

## 输出

- 退出码（exit code）语义解读
- 标准错误流（stderr）诊断信息分类
- 故障类别判定（成功/应用错误/运行时错误/信号终止）
- 恢复策略建议

## 流程节点

### 1. 退出码捕获与分类

执行CLI命令后，立即捕获退出码并按以下规则分类：

| 退出码范围 | 类别 | 语义 | 示例 |
|-----------|------|------|------|
| 0 | 成功 | 命令正常完成 | 正常退出 |
| 1-125 | 应用错误 | 工具内部逻辑错误、参数校验失败、业务规则违反 | 参数缺失、Schema校验失败 |
| 126 | 执行失败 | 命令不可执行（权限不足或非可执行文件） | 权限问题 |
| 127 | 命令未找到 | 命令不存在或PATH配置错误 | 命令拼写错误 |
| 128+N | 信号终止 | 被信号N终止（N=信号编号） | SIGKILL(9)=137, SIGTERM(15)=143 |
| 129-255 | 其他 | 特定工具自定义错误码 | 需查阅工具文档 |

[D1] GNU C Library Manual, Exit Status章节：退出码0表示成功，非0表示某种错误状态

### 2. 标准错误流解析

标准错误流（stderr）通常包含诊断信息，解析策略：

1. **错误模式匹配**：识别常见错误模式
   - "Error"/"ERROR"/"error" → 应用错误
   - "Permission denied" → 权限问题
   - "No such file" → 文件不存在
   - "Timeout"/"timed out" → 超时
   - "Connection refused" → 网络连接失败
   - "Authentication failed"/"401"/"403" → 认证/授权失败

2. **JSON Schema校验错误解析**：
   - "missing required property" → 缺少必填字段
   - "type mismatch"/"expected X, got Y" → 类型不匹配
   - "value not in enum" → 枚举值不合法

### 3. 超时故障处理

非交互执行中超时是常见故障：

| 超时类型 | 特征 | 恢复策略 |
|---------|------|---------|
| 连接超时 | 短时间内stderr输出连接相关错误 | 重试（指数退避） |
| 执行超时 | 进程运行时间超过阈值 | 检查资源限制、增加超时时间或优化命令 |
| 读取超时 | 进程挂起无输出 | 强制终止、检查死锁 |

### 4. 认证与权限故障

| 故障特征 | 可能原因 | 诊断方法 | 恢复策略 |
|---------|---------|---------|---------|
| HTTP 401 | Token过期或缺失 | 检查认证配置 | 刷新Token或重新认证 |
| HTTP 403 | 权限不足 | 检查用户角色/权限 | 申请授权或切换账号 |
| "Permission denied" | 文件系统权限 | 检查chmod/chown | 调整文件权限 |
| SSL/TLS错误 | 证书问题 | 检查系统时间/证书链 | 更新证书或配置信任 |

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 标准成功退出码 | 0 | [D1] | 所有Unix/Linux系统通用 |
| 信号终止偏移 | 128 | [D1] | 退出码 = 128 + 信号编号 |
| SIGTERM信号 | 15 | [D1] | 优雅终止请求 |
| SIGKILL信号 | 9 | [D1] | 强制终止（不可捕获） |

### 校准数值（Python argparse实现）
以下数值来自Python argparse实现，供量级校准；其他体系需以自身证据重新锚定：
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| argparse默认退出码 | 2 | [D2] | 参数错误时的默认退出码 |
| ArgumentError异常类 | argparse.ArgumentError | [D2] | 参数错误异常类 |
| exit_on_error参数 | True（默认） | [D2] | 控制是否在错误时退出 |
| suggest_on_error参数 | False（默认） | [D2] | 控制是否提供建议错误 |

## 边界与分流

1. **退出码为0但stderr有输出**：可能为警告信息，需判断是否影响后续流程
2. **退出码非0但业务逻辑应成功**：检查工具是否有自定义错误码定义
3. **信号终止（128+N）**：检查是否为系统资源限制（OOM Killer）或用户手动终止
4. **命令根本无法启动（126/127）**：优先检查PATH、环境变量、可执行权限
5. **沙箱环境执行**：在容器或沙箱环境中执行CLI命令时，需考虑：
   - 资源限制（内存、CPU、磁盘空间）可能导致命令执行失败
   - 网络隔离可能阻止外部连接
   - 文件系统挂载限制可能影响文件访问
   - 权限隔离可能阻止必要的系统调用
   - 容器退出码可能反映Docker守护进程错误（125）或容器命令问题（126/127）

## 质量检查

- 每次执行后立即检查退出码，不依赖stdout内容判断成功
- stderr输出必须记录到日志，即使退出码为0
- 对于关键路径命令，实现重试机制（最大重试次数、指数退避）
- 超时设置应基于历史执行时间的P95值

## 回退策略

1. **重试策略**：针对瞬时故障（网络超时、资源竞争）
2. **降级策略**：主路径失败时切换到备用方案（如本地缓存、简化处理）
3. **告警策略**：连续失败超过阈值时触发告警，人工介入

## 资源召回建议

当遇到以下情况时应召回本卡片：
- CLI工具在自动化脚本中执行失败
- 需要解读非零退出码的具体含义
- 标准错误流包含难以理解的错误信息
- 需要设计CLI工具的错误处理和重试逻辑

配套卡片：`json-schema-report-validation`（当CLI输出为JSON格式且需要校验时）

## 证据来源

[D1] The GNU C Library Manual - Exit Status, GNU Project, Free Software Foundation, v2.44, https://www.gnu.org/software/libc/manual/html_node/Exit-Status.html
[D2] Python argparse官方文档, Python Software Foundation, Python 3.14.7文档, https://docs.python.org/3/library/argparse.html
[D3] POSIX.1-2024 exit() - Open Group Base Specifications, IEEE / The Open Group, POSIX.1-2024, https://pubs.opengroup.org/onlinepubs/9799919799/functions/exit.html
[D4] Python sys.exit() Documentation, Python Software Foundation, Python 3.14.7文档, https://docs.python.org/3/library/sys.html#sys.exit
[D5] Python Built-in Exceptions - Exit Code Classification, Python Software Foundation, Python 3.14.7文档, https://docs.python.org/3/library/exceptions.html
[D6] errno(3) - Linux Manual Page, Linux man-pages project, Linux man-pages 6.11, https://man7.org/linux/man-pages/man3/errno.3.html
[D7] subprocess — Subprocess management, Python Software Foundation, Python 3.14.7文档, https://docs.python.org/3/library/subprocess.html