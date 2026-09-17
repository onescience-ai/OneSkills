# CLI 非交互执行与故障分类

## 适用范围

面向需要在自动化流水线、CI/CD 系统或后台服务中以非交互方式执行命令行程序的场景，提供进程生命周期管理、超时控制、退出状态分类和错误处理的通用方法。适用于 Python subprocess、Shell 脚本、系统调用等各类 CLI 执行环境。

## 输入

- 命令字符串或参数序列
- 工作目录（可选）
- 环境变量配置（可选）
- 超时时间设置（可选）
- 输入数据（通过 stdin 管道）

## 输出

- 进程退出码（returncode）
- 标准输出（stdout）
- 标准错误（stderr）
- 异常信息（TimeoutExpired、CalledProcessError 等）

## 流程节点

### 1. 进程启动配置

选择合适的执行方式：
- `subprocess.run()` - 简单场景推荐，阻塞等待完成
- `subprocess.Popen()` - 需要细粒度控制时使用
- 参数设置：`shell=True/False`、`cwd`、`env`、`stdin/stdout/stderr` 管道

### 2. 超时控制

使用 `timeout` 参数设置最大执行时间：
- 超时到期后进程被终止（SIGKILL/SIGTERM）
- 抛出 `TimeoutExpired` 异常
- 异常对象包含 `cmd`、`timeout`、`output`、`stdout`、`stderr` 属性

### 3. 退出码分类

| 退出码 | 含义 | 处理策略 |
|--------|------|----------|
| 0 | 成功执行 | 正常流程继续 |
| 1-255 | 应用程序错误 | 根据错误码分类处理 |
| 负值 -N | 被信号 N 终止（POSIX） | 检查信号来源（SIGTERM=15, SIGKILL=9） |
| None | 进程尚未终止 | 调用 poll() 或 wait() 等待 |

### 4. 异常处理

- `CalledProcessError`：`check=True` 时非零退出码触发，包含 returncode、cmd、output、stderr
- `TimeoutExpired`：超时触发，需要手动 kill() 进程并 communicate() 收集输出
- `SubprocessError`：所有子进程异常的基类

### 5. 输出捕获

- `capture_output=True`：同时捕获 stdout 和 stderr
- `stdout=PIPE, stderr=STDOUT`：合并输出到 stdout
- 文本模式：`text=True` 或 `encoding='utf-8'`

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| timeout | 按需设置 | [D1] | 秒为单位，超时后进程被终止 |
| check | True/False | [D1] | True 时非零退出码抛出 CalledProcessError |
| capture_output | True/False | [D1] | True 时捕获 stdout 和 stderr |
| shell | True/False | [D1] | True 时通过 shell 执行，注意注入风险 |

### 校准数值

以下数值来自 Python subprocess 模块实践，供量级校准；其他语言/环境需以自身证据重新锚定：

| 参数 | 典型值 | 来源 | 说明 |
|------|--------|------|------|
| 默认超时 | None（无超时） | [D1] | 不设置则无限等待 |
| 常见错误码 | 1（通用错误）、2（误用命令）、126（权限不足）、127（命令未找到）、128+N（信号N终止） | [D1] | POSIX 标准约定 |
| 管道缓冲 | io.DEFAULT_BUFFER_SIZE | [D1] | 避免死锁应使用 communicate() |

## 边界与分流

### 超时场景

- 进程创建本身不可中断，超时异常可能延迟触发
- 超时后进程未终止时需手动 kill() 并 communicate() 清理
- 使用 Popen 时避免在 stdout/stderr=PIPE 上使用 wait() 导致死锁

### 认证与沙箱

- 涉及敏感操作时使用 env 参数隔离环境变量
- shell=True 时注意 shell 注入风险，使用 shlex.quote() 转义
- Windows 平台 batch 文件可能绕过参数转义

### 平台差异

- POSIX：负退出码表示信号终止，支持 start_new_session
- Windows：使用 creationflags 控制进程创建行为，kill() 等同于 terminate()

## 质量检查

- 验证退出码是否符合预期分类
- 检查 stderr 内容是否包含错误信息
- 确认超时设置是否覆盖所有可能的阻塞场景
- 验证输出捕获是否完整（无缓冲区溢出）

## 回退策略

- 超时失败：增加超时时间或优化程序性能
- 权限不足：检查执行权限或使用 sudo/提升权限
- 命令未找到：检查 PATH 环境变量或使用绝对路径
- 管道死锁：改用 communicate() 替代逐步读写

## 资源召回建议

当任务涉及以下场景时召回本卡片：
- 自动化测试框架执行外部命令
- CI/CD 流水线中的构建/部署步骤
- 后台服务的子进程管理
- 科学计算工作流的任务调度
- 任何需要非交互执行 CLI 程序并处理其退出状态的场景

配套资源：
- general-json-schema-report-delivery-contract（报告格式验证）

## 补充证据（权威文档）

[D1] Python subprocess Module Documentation, Python Software Foundation, Python 3.14.7, URL: https://docs.python.org/3/library/subprocess.html（accessed_at 2026-09-16，交叉验证：官方文档）

## 证据来源

[1] Python subprocess Module Documentation, Python Software Foundation, Python 3.14.7, URL: https://docs.python.org/3/library/subprocess.html

## 批次补充（2026-09-17：基于论文证据的CLI最佳实践）

### 论文证据补充

从最新检索的论文中抽取以下知识，丰富CLI非交互执行与故障分类体系：

**[1] Bionitio: demonstrating and facilitating best practices for bioinformatics command-line software (PMID: 31544213)**

| 概念 | 描述 | 来源 | 说明 |
|------|------|------|------|
| 命令行最佳实践 | 自动化启动新项目，遵循推荐的最佳实践 | [1] | 包括命令行参数解析、错误处理、进度日志、退出状态值定义 |
| 退出状态值定义 | 定义明确的退出状态值，用于指示执行结果 | [1] | 关键特征包括命令行参数解析、错误处理、进度日志、退出状态值定义 |
| 项目模板 | 提供工作示例和模板，用于构建新工具 | [1] | 包括命令行参数解析、错误处理、进度日志、退出状态值定义、测试套件 |
| 跨平台支持 | 支持多种编程语言和操作系统 | [1] | 12种编程语言，跨平台操作 |

### 补充边界与分流

- **CLI最佳实践实施**：当设计新的CLI工具时，应遵循命令行最佳实践，包括退出状态值定义、错误处理、进度日志等[1]
- **跨平台兼容性**：当CLI工具需要跨平台支持时，应使用12种编程语言支持的跨平台方案[1]
- **项目模板使用**：当启动新的CLI项目时，应使用项目模板，包括命令行参数解析、错误处理、进度日志、退出状态值定义、测试套件等[1]

### 补充质量检查

- 验证CLI工具是否遵循命令行最佳实践，包括退出状态值定义、错误处理、进度日志等
- 检查退出状态值定义是否明确，用于指示执行结果
- 验证项目模板是否包括命令行参数解析、错误处理、进度日志、退出状态值定义、测试套件等
- 确保跨平台支持是否包括多种编程语言和操作系统

### 补充回退策略

- **CLI最佳实践未遵循**：当CLI工具未遵循最佳实践时，应逐步实施退出状态值定义、错误处理、进度日志等
- **跨平台兼容性问题**：当跨平台兼容性出现问题时，应使用更通用的跨平台方案
- **项目模板不适用**：当项目模板不适用时，应根据具体需求调整模板
