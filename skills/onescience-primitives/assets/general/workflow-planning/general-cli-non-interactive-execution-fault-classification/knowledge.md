# CLI 非交互执行与故障分类

## 适用范围
面向需要在自动化或脚本环境中执行命令行工具的场景，覆盖参数解析、进程启动、退出码语义和标准错误输出的故障分类与诊断。适用于所有需要非交互式执行CLI工具的任务，包括科学计算流水线、CI/CD集成和批处理作业。

## 输入
- 命令行参数序列（字符串或列表）
- 环境变量配置
- 标准输入/输出/错误流配置
- 超时设置（秒）

## 输出
- 进程返回码（exit code）
- 标准输出内容（stdout）
- 标准错误内容（stderr）
- 结构化异常信息（如CalledProcessError、TimeoutExpired）

## 流程节点

### 1. 参数解析与校验
- **操作**：使用argparse或类似库解析命令行参数
- **关键参数**：
  - `exit_on_error`: 控制解析失败时是否自动退出（默认True）[D1]
  - `add_help`: 是否添加-h/--help选项（默认True）[D1]
  - `type`: 参数类型转换函数[1]
- **质量门禁**：解析成功后验证必填参数存在

### 2. 进程启动
- **操作**：使用subprocess.run()或Popen()启动子进程
- **关键参数**：
  - `shell`: 是否通过shell执行（默认False，推荐False以避免注入风险）[D2]
  - `cwd`: 工作目录设置[2]
  - `env`: 环境变量映射[2]
  - `timeout`: 超时秒数（None表示无限等待）[2]
- **质量门禁**：捕获OSError（如可执行文件不存在）和ValueError（参数无效）

### 3. 执行监控与超时处理
- **操作**：等待进程完成或超时终止
- **关键参数**：
  - `communicate()`: 交互式读写stdin/stdout/stderr[2]
  - `TimeoutExpired`: 超时异常，包含cmd、timeout、output属性[2]
- **质量门禁**：超时后必须kill()子进程并再次communicate()清理管道[2]

### 4. 退出码语义解析
- **操作**：根据返回码分类故障类型
- **关键参数**：
  - `returncode=0`: 成功执行[2]
  - `returncode>0`: 应用程序错误（具体含义由程序定义）[2]
  - `returncode<0`: 被信号终止（POSIX，-N表示信号N）[2]
  - `shell=True`时：返回码反映shell本身的退出状态（如128+N）[2]
- **质量门禁**：使用check=True时，非零返回码触发CalledProcessError[2]

## 关键参数

### 通用判据（方法层）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| exit_on_error | True/False | [D1] | 控制argparse解析失败时的行为 |
| shell | False（推荐） | [D2] | 避免shell注入，提高安全性 |
| check | True/False | [D2] | 控制非零返回码是否触发异常 |
| timeout | None/正整数 | [D2] | 超时秒数，None表示无限等待 |

### 故障分类判据
| 退出码范围 | 分类 | 来源 | 说明 |
|-----------|------|------|------|
| 0 | 成功 | [D2] | 进程正常完成 |
| 1-125 | 应用程序错误 | [D2] | 具体含义由程序定义 |
| 126 | 命令不可执行 | POSIX | 权限问题或非文件 |
| 127 | 命令未找到 | POSIX | PATH中无此命令 |
| 128+N | 被信号N终止 | [D2] | N为信号编号（如9=SIGKILL） |
| 负数 | 被信号终止（POSIX） | [D2] | -N表示信号N |

## 边界与分流

### 参数解析失败
- **症状**：argparse自动打印用法信息并退出（exit_on_error=True时）
- **分流**：设置exit_on_error=False，捕获argparse.ArgumentError进行自定义处理[D1]

### 进程启动失败
- **症状**：OSError（如FileNotFoundError）
- **分流**：检查可执行文件路径和权限，使用shutil.which()验证命令是否存在[2]

### 超时处理
- **症状**：TimeoutExpired异常
- **分流**：必须调用proc.kill()终止子进程，然后proc.communicate()清理管道[2]

### 输出管道死锁
- **症状**：使用stdout=PIPE或stderr=PIPE时进程挂起
- **分流**：使用communicate()而非直接读写管道，或使用异步IO[2]

## 质量检查

### 退出码验证
- 成功用例：returncode==0
- 失败用例：returncode!=0（需根据程序定义进一步分类）
- 信号终止用例：returncode<0（POSIX）

### 标准错误检查
- 捕获stderr输出用于错误诊断
- 注意：shell=True时stderr可能包含shell自身的错误信息[2]

### 异常处理
- CalledProcessError：非零返回码（check=True时）[2]
- TimeoutExpired：超时终止[2]
- OSError：启动失败（如文件不存在）[2]

## 回退策略

### 降级执行
- 当shell=True不可用时，使用shlex.split()解析命令字符串[2]
- 当timeout不支持时，使用轮询+手动超时机制

### 替代方案
- 使用asyncio.create_subprocess_exec()进行异步执行[2]
- 使用os.system()作为最后手段（不推荐，缺乏错误处理）

## 资源召回建议
- 当任务需要执行外部CLI工具时召回本卡片
- 配套资源：onescience-runtime（运行时管理）、onescience-installer（环境安装）
- 适用于归因报告中提到的CLI执行故障分类场景

## 应用动作与验证方式

### 应用动作
- 依据故障类别修正启动配置或恢复策略
- 在输出前按契约校验报告

### 验证方式
- 使用成功、非零退出和超时用例验证状态及日志
- 以 report-schema.json 校验最终输出并执行错配字段反例测试

## 批次补充 2026-09-18（onescience-knowledge-harvester）

### 补充证据：GNU C Library 退出码标准

本次补充引入 GNU C Library 手册作为退出码分类的权威交叉验证来源，与 POSIX 标准和 Python subprocess 文档形成多源互证。

**退出码语义补充**（基于 [D3]）：

| 退出码范围 | 分类 | 来源 | 说明 |
|-----------|------|------|------|
| 0 | 成功 | [D2][D3] | 进程正常完成（交叉验证） |
| 1-125 | 应用程序错误 | [D2][D3] | 程序自身定义的错误码（交叉验证） |
| 126 | 权限拒绝/不可执行 | [D3] | 命令不可执行（非文件或无执行权限） |
| 127 | 命令未找到 | [D3] | 路径错误或命令名不存在 |
| 128+N | 信号终止 | [D2][D3] | 被信号 N 终止，N 为信号编号（交叉验证） |

**跨平台差异补充**（基于 [D2]）：
- Windows 平台：kill() 等同于 terminate()，无 SIGKILL 语义
- Windows 平台：CREATE_NEW_PROCESS_GROUP 用于 Ctrl+C 信号隔离
- POSIX 平台：restore_signals=True（默认）恢复 SIG_IGN 为 SIG_DFL

**质量检查补充**：
- 超时检查：超时触发后必须 kill() 子进程，否则产生僵尸进程
- 输出完整性：使用 PIPE 捕获 stdout/stderr，避免死锁

## 证据来源
[D1] argparse — Parser for command-line options, arguments and subcommands, Python Software Foundation, Python 3.14.7, URL: https://docs.python.org/3/library/argparse.html (accessed 2026-09-17)
[D2] subprocess — Subprocess management, Python Software Foundation, Python 3.14.7, URL: https://docs.python.org/3/library/subprocess.html (accessed 2026-09-17)
[D3] The GNU C Library manual - Exit Status, Free Software Foundation, version 2.44, URL: https://www.gnu.org/software/libc/manual/html_node/Exit-Status.html (accessed 2026-09-18)