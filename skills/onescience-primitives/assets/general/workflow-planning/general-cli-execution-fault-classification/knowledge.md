# CLI 非交互执行与故障分类

## 适用范围

面向需要在自动化流水线中可靠执行外部命令行工具的场景，提供进程生命周期管理、退出码分类与故障诊断的通用方法框架。适用于所有需要非交互方式启动、监控和诊断 CLI 进程的任务，包括科学计算工具调用、数据处理脚本执行、归因分析进程管理等。

**不适用场景**：
- 需要交互式终端输入的场景（如 REPL 调试）
- 内部函数调用而非外部进程启动
- 已有成熟封装库的特定工具链

## 输入

- **命令参数**：要执行的命令行指令（字符串或参数列表）
- **执行环境**：工作目录、环境变量、用户权限
- **超时约束**：预期的最大执行时间
- **资源限制**：内存、CPU、沙箱要求

## 输出

- **进程状态**：成功退出（exit code 0）、非零退出码、超时终止、信号终止
- **标准输出/错误**：捕获的 stdout 和 stderr 内容
- **故障分类**：根据退出码和错误模式确定的故障类别
- **恢复建议**：基于故障类型的修复或重试策略

## 流程节点

### Step 1：进程启动配置
- **操作**：配置 subprocess 参数（args、stdin/stdout/stderr、timeout、check）
- **参数**：args 应为序列类型（列表）而非单字符串；使用 capture_output=True 捕获输出
- **工具**：Python subprocess.run() 或 subprocess.Popen
- **质量门禁**：参数列表正确传递，避免 shell 注入风险

### Step 2：退出码分类
- **操作**：根据 returncode 值分类进程终止原因
- **参数**：
  - returncode = 0：正常退出
  - returncode > 0：应用级错误（具体含义由程序定义）
  - returncode < 0：被信号终止（POSIX，-N 表示信号 N）
  - returncode = None：进程尚未终止
- **工具**：subprocess.CompletedProcess.returncode
- **质量门禁**：记录完整退出码和对应的标准错误输出

### Step 3：异常捕获与分类
- **操作**：捕获并分类 subprocess 异常
- **参数**：
  - CalledProcessError：check=True 时非零退出码触发
  - TimeoutExpired：timeout 到期触发
  - SubprocessError：所有 subprocess 异常基类
  - OSError：命令不存在或权限不足
- **工具**：try-except 异常处理
- **质量门禁**：异常信息包含 cmd、returncode、output、stderr

### Step 4：故障诊断与恢复
- **操作**：根据异常类型和退出码确定故障原因和恢复策略
- **参数**：
  - 退出码 1-125：应用错误，检查参数和输入
  - 退出码 126：命令不可执行，检查权限
  - 退出码 127：命令未找到，检查 PATH
  - 退出码 128+N：被信号 N 终止
  - TimeoutExpired：增加超时或优化性能
- **工具**：诊断日志和错误模式分析
- **质量门禁**：故障分类准确，恢复建议可执行

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 进程启动方式 | subprocess.run() 或 Popen | [D1] | run() 适用于简单场景，Popen 适用于高级控制 |
| 参数传递 | 序列类型（列表）优先 | [D1] | 避免 shell 注入，支持空格文件名 |
| 输出捕获 | capture_output=True 或 stdout=PIPE | [D1] | 同时捕获 stdout 和 stderr |
| 超时设置 | timeout 参数（秒） | [D1] | 到期后触发 TimeoutExpired 异常 |
| 退出码检查 | check=True 或手动检查 returncode | [D1] | check=True 时非零退出码自动触发 CalledProcessError |
| shell 模式 | 默认 False，仅在需要 shell 特性时启用 | [D1] | shell=True 存在安全风险，需谨慎使用 |

### 校准数值

以下数值来自 Python subprocess 实现，供量级校准；其他运行时环境需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码 0 | 成功 | [D1] | POSIX 标准 |
| 退出码 1-125 | 应用错误 | [D1] | 程序自定义 |
| 退出码 126 | 不可执行 | [D1] | 权限问题 |
| 退出码 127 | 未找到 | [D1] | PATH 问题 |
| 退出码 128+N | 信号终止 | [D1] | N 为信号编号 |
| 负退出码 -N | 信号 N 终止 | [D1] | POSIX 专用 |

## 边界与分流

### 前提：命令存在且可执行
- **不成立时**：捕获 OSError，检查命令路径和 PATH 环境变量
- **改道方案**：使用 shutil.which() 验证命令存在性，提供安装指引

### 前提：进程在超时内完成
- **不成立时**：捕获 TimeoutExpired，检查进程是否挂起
- **改道方案**：增加超时值、优化命令参数、使用异步执行模式

### 前提：标准输出/错误不阻塞
- **不成立时**：管道缓冲区满导致死锁
- **改道方案**：使用 communicate() 而非直接读写管道，或使用 DEVNULL 丢弃不需要的输出

### 前提：权限充足
- **不成立时**：PermissionError 或非零退出码 126
- **改道方案**：检查文件权限、使用 sudo（需安全评估）、调整进程用户

## 质量检查

- **退出码记录**：每次执行必须记录 returncode
- **异常捕获**：必须处理 CalledProcessError、TimeoutExpired、OSError
- **输出保存**：stdout 和 stderr 必须捕获并保存用于诊断
- **超时处理**：必须设置合理的 timeout 值并处理超时异常
- **安全审计**：使用 shell=True 时必须评估注入风险

## 回退策略

- **命令不存在**：提供安装命令或替代工具
- **权限不足**：调整文件权限或使用虚拟环境
- **超时**：增加 timeout、拆分任务、使用后台执行
- **资源耗尽**：监控内存/CPU 使用，添加资源限制
- **信号终止**：检查系统日志，调整进程优先级

## 资源召回建议

- **何时召回**：需要在自动化流水线中可靠执行外部 CLI 工具时
- **配套资源**：
  - general-json-schema-report-validation：结构化输出验证
  - 领域特定的工具执行规范（如 onescience-runtime）
  - 系统监控和日志分析工具

## 证据来源

[D1] "subprocess — Subprocess management", Python 3.14.7 Documentation, Python Software Foundation, URL: https://docs.python.org/3/library/subprocess.html (accessed 2026-09-17, 官方权威文档)
