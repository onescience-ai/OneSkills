# CLI 非交互执行与故障分类

## 适用范围
适用于通过命令行接口执行自动化任务的场景，包括归因分析、数据处理、模型训练等需要非交互式运行的工具。本卡覆盖命令参数解析、认证处理、沙箱隔离、超时控制、退出码语义和标准错误判读。

## 输入
- 命令行工具的可执行路径或模块名
- 必要参数（输入文件路径、输出目录、配置选项等）
- 可选环境变量（认证凭证、超时设置、日志级别等）

## 输出
- 退出码（0=成功，非0=失败或警告）
- 标准输出（stdout）：正常结果或日志
- 标准错误（stderr）：错误信息、警告、诊断数据

## 流程节点

### 1. 命令构建与参数解析
- **操作**：拼接命令行参数，确保空格和特殊字符正确转义
- **工具**：Python subprocess.run()、shlex.quote()
- **质量门禁**：参数数量和顺序符合工具文档；特殊字符（空格、引号、通配符）已转义

### 2. 执行环境配置
- **操作**：设置工作目录、环境变量、超时限制
- **工具**：subprocess.run(cwd=..., env=..., timeout=...)
- **质量门禁**：必要环境变量已设置；超时值合理（默认300秒）；工作目录存在且可写

### 3. 进程执行与监控
- **操作**：启动子进程，等待完成或超时
- **工具**：subprocess.run() 或 subprocess.Popen()
- **质量门禁**：进程正常启动；未发生死锁（stdin/stdout/stderr 合理重定向）

### 4. 退出码解析
- **操作**：检查返回码，映射到故障类别
- **标准退出码**：
  - `0`：成功完成
  - `1`：通用错误（参数错误、运行时异常）
  - `2`：误用 shell 命令（POSIX 标准）
  - `126`：命令不可执行（权限不足）
  - `127`：命令未找到（PATH 错误）
  - `128+N`：被信号 N 终止（如 137=SIGKILL）
  - 自定义退出码：查阅工具文档

### 5. 标准错误判读
- **操作**：解析 stderr 输出，分类错误类型
- **常见错误模式**：
  - `FileNotFoundError`：输入文件不存在或路径错误
  - `PermissionError`：权限不足或文件被锁定
  - `TimeoutExpired`：执行超时
  - `CalledProcessError`：子进程返回非零退出码
  - JSON 解析错误：输出格式不符合预期

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| timeout | 300s（默认） | [D1] | 可根据任务复杂度调整 |
| check | True | [D1] | 非零退出码时抛出异常 |
| capture_output | True | [D1] | 捕获 stdout/stderr 用于后续解析 |
| encoding | utf-8 | [D1] | 避免编码问题 |
| shell | False | [D1] | 避免 shell 注入风险（除非需要 shell 特性） |

## 边界与分流
- **超时处理**：捕获 TimeoutExpired 异常，记录日志后决定重试或终止
- **权限问题**：检查文件权限、用户角色，必要时请求管理员权限
- **输出解析失败**：记录原始输出，降级为空结果或重试
- **沙箱隔离**：敏感操作应在容器或虚拟环境中执行，避免污染主系统

## 质量检查
- 退出码是否在预期范围内（0 或工具文档定义的成功码）
- stderr 是否包含可识别的错误模式
- 输出是否可解析（如 JSON 格式验证）
- 超时是否合理（不早于预期完成时间）

## 回退策略
- 重试：对于临时性错误（网络超时、资源锁），可自动重试 2-3 次
- 降级：对于部分失败，记录失败项并继续处理其他任务
- 人工干预：对于认证失败、权限不足等，记录诊断信息并通知用户

## 资源召回建议
- 当遇到 CLI 执行失败时召回本卡
- 配套资源：general-json-schema-report-delivery-contract（输出格式验证）

## 补充证据（权威文档）
[D1] Python subprocess Module Documentation, Python Software Foundation, v3.12, URL: https://docs.python.org/3/library/subprocess.html（交叉验证：广泛使用的官方文档）
[D2] POSIX Shell Command Language - Exit Status, IEEE/POSIX, IEEE Std 1003.1-2017, URL: https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html（权威标准）

## 证据来源
[1] A model for detecting faults in build specifications, T. Sotiropoulos et al., Proc. ACM Program. Lang., 2020, DOI: 10.1145/3428212