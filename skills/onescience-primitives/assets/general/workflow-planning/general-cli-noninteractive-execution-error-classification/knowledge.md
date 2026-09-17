# CLI 非交互执行与故障分类

## 适用范围

面向命令行工具在自动化流水线、批处理任务和远程执行环境中的非交互运行场景，提供进程启动、执行监控、退出码解读、超时处理和标准错误诊断的系统化方法。适用于需要通过程序调用外部 CLI 工具并根据其执行结果做出决策的任何软件系统，不适用于交互式终端会话或图形界面应用。

## 输入

- **CLI 命令**：完整的命令行字符串或参数序列
- **执行环境**：操作系统类型（POSIX/Windows）、shell 类型、环境变量
- **超时配置**：可选的执行时间限制（秒）
- **输入数据**：通过 stdin 传递的标准输入（可选）

## 输出

- **退出码（returncode）**：进程终止状态码
- **标准输出（stdout）**：正常执行结果
- **标准错误（stderr）**：错误诊断信息
- **异常对象**：结构化的错误信息（含 cmd、timeout、output 属性）

## 流程节点

### 1. 进程启动与参数构建

操作：使用 `subprocess.run()` 或 `subprocess.Popen()` 构建并启动子进程

参数规范：
- 推荐以列表形式传递参数（避免 shell 注入风险）
- `shell=True` 时需确保所有元字符已正确转义
- Windows 平台需注意 `CreateProcess()` 的字符串转换规则

工具：Python `subprocess` 模块、POSIX `execvpe()` 系统调用

质量门禁：验证命令路径有效性（使用 `shutil.which()` 搜索）

### 2. 执行监控与超时控制

操作：设置超时阈值，监控进程状态

参数：
- `timeout`：超时秒数（内部传递给 `Popen.communicate()`）
- 超时到期时子进程将被终止并等待

工具：`Popen.communicate(timeout=N)`、`Popen.poll()`

质量门禁：超时异常后需调用 `proc.kill()` 清理子进程，再调用 `communicate()` 读取输出

### 3. 退出码语义分类

操作：根据退出码值判定进程终止原因

| 退出码 | 含义 | 诊断动作 |
|--------|------|----------|
| 0 | 正常退出 | 执行成功，读取 stdout |
| 1-125 | 应用错误 | 检查 stderr，按应用语义分类 |
| 126 | 命令不可执行 | 检查文件权限 |
| 127 | 命令未找到 | 检查 PATH 环境变量 |
| 128+N | 被信号 N 终止 | 检查系统资源限制 |
| 负值 -N | POSIX 信号终止 | 信号 N 导致终止（仅 POSIX） |

工具：`CompletedProcess.returncode`、`CalledProcessError.returncode`

质量门禁：负退出码仅在 POSIX 系统有效，Windows 平台需使用其他机制

### 4. 标准错误诊断

操作：捕获并分析 stderr 输出

| 异常类型 | 触发条件 | 诊断要点 |
|----------|----------|----------|
| `TimeoutExpired` | 超时到期 | 检查 timeout 值是否合理，子进程是否阻塞 |
| `CalledProcessError` | 非零退出码（check=True） | 检查 returncode 和 stderr 内容 |
| `OSError` | 命令不存在或权限不足 | 检查文件路径和执行权限 |
| `ValueError` | 参数无效 | 检查 Popen 构造参数 |

工具：异常对象的 `cmd`、`output`、`stderr` 属性

质量门禁：超时后必须清理子进程（`proc.kill()` + `communicate()`）避免僵尸进程

### 5. 输出捕获与流管理

操作：配置 stdin/stdout/stderr 重定向

| 参数值 | 行为 |
|--------|------|
| `None` | 继承父进程文件描述符 |
| `PIPE` | 创建管道，通过 `communicate()` 读写 |
| `DEVNULL` | 丢弃输出 |
| `STDOUT` | stderr 合并到 stdout |

工具：`subprocess.PIPE`、`subprocess.DEVNULL`、`subprocess.STDOUT`

质量门禁：使用 `PIPE` 时必须通过 `communicate()` 读取，避免管道缓冲区满导致死锁

## 关键参数

### 通用判据（方法层）

| 参数 | 判据 | 来源 | 说明 |
|------|------|------|------|
| 退出码 0 | 成功 | [D1][D2] | POSIX 标准，C11/POSIX.1-2008 |
| 退出码 1-125 | 应用错误 | [D2] | BSD/GNU 标准化约定 |
| 退出码 126 | 不可执行 | [D1] | shell 标准行为 |
| 退出码 127 | 未找到 | [D1] | shell 标准行为 |
| 退出码 128+N | 信号终止 | [D1][D2] | Bash 退出状态约定 |
| 负退出码 -N | POSIX 信号 | [D1][D2] | 仅 POSIX 系统 |
| 超时参数 | 秒数 | [D1] | 内部传递给 communicate() |

### 校准数值（实例级）

> 以下数值来自 Python subprocess 实现，供量级校准；其他语言/运行时需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认 bufsize | -1 (系统默认) | [D1] | io.DEFAULT_BUFFER_SIZE |
| 超时精度 | 平台相关 | [D1] | 进程创建时间不可中断 |

## 边界与分流

### 退出码 126/127 的处理
- 退出码 126：命令存在但不可执行 → 检查文件权限位（chmod +x）
- 退出码 127：命令不存在 → 检查 PATH 环境变量，使用绝对路径

### 超时场景分流
- 子进程可终止：发送 SIGTERM（POSIX）或 TerminateProcess（Windows）
- 子进程不可终止：发送 SIGKILL（POSIX）或升级权限
- 资源受限环境：降低 timeout 值，增加重试次数

### Windows 特殊处理
- `shell=True` 时使用 `%COMSPEC%` 和 `%SystemRoot%\System32\cmd.exe`
- 批文件（.bat/.cmd）需使用 `shell=True`
- 进程创建标志：`CREATE_NEW_PROCESS_GROUP`、`DETACHED_PROCESS`

## 质量检查

| 检查点 | 阈值 | 失败处理 |
|--------|------|----------|
| 进程启动 | OSError | 检查命令路径和权限 |
| 超时检测 | TimeoutExpired | 清理子进程，记录超时前输出 |
| 退出码检查 | returncode != 0 | 分类错误类型，检查 stderr |
| 管道缓冲 | 死锁风险 | 使用 communicate() 而非 read() |

## 回退策略

1. **命令不存在**：使用 `shutil.which()` 搜索，提供安装建议
2. **权限不足**：检查文件权限位，提示 sudo 或 chmod
3. **超时频繁**：增加 timeout 值，或优化子进程性能
4. **输出过大**：使用 `DEVNULL` 丢弃不必要输出，或限制输出大小

## 资源召回建议

当遇到以下场景时应召回本卡片：
- 自动化脚本中调用外部 CLI 工具
- CI/CD 流水线中执行命令行任务
- 远程执行环境（SSH/容器）中的进程管理
- 需要根据 CLI 退出码做分支决策的场景

配套资源：
- `general-json-schema-report-contract-validation`：结构化输出验证
- `onescience-runtime`：远程执行与作业提交

## 补充证据（权威文档）

[D1] Python subprocess documentation, Python Software Foundation, v3.14.7, URL: https://docs.python.org/3/library/subprocess.html (accessed_at: 2026-09-16, 交叉验证：官方文档)
[D2] exit(3) - Linux manual page, Linux man-pages project, v6.19, URL: https://www.man7.org/linux/man-pages/man3/exit.3.html (accessed_at: 2026-09-16, 交叉验证：POSIX 标准文档)

## 补充证据（批次补充）

### 批次补充 2026-09-17（CLI故障分类与JSON Schema验证）

**补充内容**：CLI非交互执行的退出码语义分类与JSON Schema验证的Python实现细节

**新增知识**：

#### CLI退出码语义分类（扩展）
- 退出码 1-125：应用错误，需检查 stderr 按应用语义分类
- 退出码 126：命令存在但不可执行，检查文件权限位（chmod +x）
- 退出码 127：命令不存在，检查 PATH 环境变量，使用绝对路径
- 退出码 128+N：被信号 N 终止（Bash 退出状态约定）
- 负退出码 -N：POSIX 信号终止（仅 POSIX 系统有效）

#### JSON验证的Python实现
- `json.loads()` 解析 JSON 字符串，失败时抛出 JSONDecodeError
- `json.load()` 从文件解析 JSON，支持 binary file（UTF-8/UTF-16/UTF-32）
- `json.dumps()` 序列化为 JSON 字符串，控制 ensure_ascii/indent/sort_keys
- `json.dump()` 序列化到文件，确保 fp.write() 支持 str 输入

#### 异常处理增强
- TimeoutExpired：超时后必须调用 proc.kill() + communicate() 避免僵尸进程
- CalledProcessError：检查 returncode 和 stderr 内容
- OSError：检查文件路径和执行权限
- ValueError：检查 Popen 构造参数

**来源**：
- Python subprocess 文档（3.14.7）
- Python json 模块文档（3.14.7）
- JSON Schema 参考文档（2020-12）

## 证据来源

[1] Python subprocess documentation, Python Software Foundation, v3.14.7, URL: https://docs.python.org/3/library/subprocess.html
[2] exit(3) - Linux manual page, Linux man-pages project, v6.19, URL: https://www.man7.org/linux/man-pages/man3/exit.3.html
[3] Python json module documentation, Python Software Foundation, v3.14.7, URL: https://docs.python.org/3/library/json.html
