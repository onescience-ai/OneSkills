# CLI 非交互执行与故障分类

## 适用范围

**触发条件**：
- 需要在无人值守环境下自动执行命令行工具
- 需要从进程退出状态中判断执行成功或失败原因
- 需要在超时或异常情况下安全终止进程

**适用场景**：
- 自动化流水线中的 CLI 工具调度（如数据处理、模型训练、仿真运行）
- 批量作业提交与状态监控（如 SLURM sbatch、PBS qsub）
- 远程 SSH 环境中的命令执行与结果收集
- CI/CD 系统中的构建与测试任务

**不适用场景**：
- 交互式命令行会话（需要用户输入的 REPL 环境）
- 图形界面应用程序的进程管理
- 实时流式数据处理（需要持续 I/O 的场景）

## 输入

- **命令字符串**：要执行的 CLI 命令及其参数
- **工作目录**：命令执行的工作目录路径
- **环境变量**：需要注入的环境变量（可选）
- **超时时间**：最大允许执行时间（秒）
- **输入数据**：通过 stdin 管道传递的数据（可选）

## 输出

- **exit_code**：进程退出码（整数）
- **stdout**：标准输出内容（字符串）
- **stderr**：标准错误输出内容（字符串）
- **timeout_flag**：是否因超时被终止（布尔值）
- **signal_flag**：是否因信号被终止（整数，0 表示正常退出）
- **fault_category**：故障分类标签（见关键参数表）

## 流程节点

### Step 1：进程启动
- **操作**：使用 subprocess.Popen 或等效接口启动子进程
- **参数**：shell=True/False, stdout=PIPE, stderr=PIPE, cwd=工作目录
- **工具**：Python subprocess, bash -c, exec 系统调用
- **质量门禁**：进程成功创建，PID 非空

### Step 2：等待与超时控制
- **操作**：使用 communicate(timeout=T) 或 waitpid + alarm 等待进程完成
- **参数**：timeout=超时秒数
- **工具**：subprocess.communicate(), signal.alarm(), select.select()
- **质量门禁**：超时后必须发送 SIGTERM（信号 15），等待 5 秒后若未终止则发送 SIGKILL（信号 9）

### Step 3：退出码解析
- **操作**：读取进程返回码，区分正常退出、异常退出、信号终止
- **参数**：无
- **工具**：os.WIFEXITED(), os.WEXITSTATUS(), os.WIFSIGNALED(), os.WTERMSIG()
- **质量门禁**：exit_code 已映射到 fault_category

### Step 4：输出捕获与清理
- **操作**：读取 stdout 和 stderr 内容，编码为 UTF-8（errors='replace'）
- **参数**：encoding='utf-8', errors='replace', max_bytes=1MB
- **工具**：subprocess.communicate(), io.TextIOWrapper
- **质量门禁**：输出内容已截断到 max_bytes，无编码异常

### Step 5：故障分类
- **操作**：根据退出码、信号、超时标志确定故障类别
- **参数**：见关键参数表
- **工具**：条件判断逻辑
- **质量门禁**：fault_category 为预定义类别之一

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 正常退出码 | 0 | [D1] | POSIX 标准：exit(0) 表示成功 |
| 一般错误码 | 1-125 | [D1] | 用户程序定义的错误 |
| 无效参数码 | 126 | [D1] | 命令不可执行（权限不足或非可执行文件） |
| 命令未找到码 | 127 | [D1] | shell 找不到指定命令 |
| 信号终止码 | 128+N | [D1] | 被信号 N 终止（如 SIGKILL=128+9=137） |
| SIGTERM | 15 | [D1] | 优雅终止信号，默认超时处理使用 |
| SIGKILL | 9 | [D1] | 强制终止信号，不可被捕获或忽略 |
| SIGALRM | 14 | [D1] | 定时器超时信号 |
| SLURM 超时 | 无特定码 | [D3] | SLURM 在 JobTimeout 时发送 SIGKILL |
| stderr 编码 | utf-8, errors='replace' | [D2] | Python subprocess 推荐编码方式 |

## 边界与分流

- **进程无响应（zombie process）**：超时后 SIGTERM 仍无响应 → 发送 SIGKILL；若仍为 zombie → 调用 waitpid() 回收
- **权限不足（exit_code=126）**：检查文件权限 chmod +x；若是容器环境 → 检查用户映射
- **命令未找到（exit_code=127）**：检查 PATH 环境变量；若是模块化环境 → 检查 module load / conda activate
- **沙箱限制**：容器内无 sudo 权限 → 使用 rootless 容器或调整 seccomp 配置
- **网络超时**：远程命令因网络断开 → 增加 keepalive 参数或使用 tmux/screen 复用

## 质量检查

| 检查点 | 阈值 | 失败处理 |
|--------|------|----------|
| 进程启动成功 | PID > 0 | 重新尝试或报告环境错误 |
| 超时检测 | 用户指定秒数 | 发送 SIGTERM → SIGKILL |
| 退出码解析 | exit_code ∈ 已知类别 | 记录为 "unknown_exit_code" |
| 输出完整性 | stdout/stderr 非空或 exit_code=0 | 截断后保留前 1MB |
| 僵尸进程回收 | waitpid 成功返回 | 强制 kill -9 并记录 |

## 回退策略

- **subprocess 不可用时**：使用 os.system() 或 os.popen()（功能受限）
- **无超时支持时**：使用 threading.Timer + process.kill() 模拟超时
- **无信号支持时**（Windows）：使用 process.terminate() + WaitForSingleObject()
- **远程执行失败时**：使用 SSH 重试或降级到本地执行

## 资源召回建议

- 当任务涉及 CLI 工具自动化执行时召回本卡片
- 配套资源：onescience-runtime（作业提交）、onescience-runsite（远程环境配置）
- 与 general-json-schema-report-validation-contract 卡片配合使用，确保 CLI 输出可被下游 Schema 校验

## 补充证据

[D1] "POSIX.1-2017 System Interfaces: exit()", IEEE/The Open Group, IEEE Std 1003.1-2017, URL: https://pubs.opengroup.org/onlinepubs/9699919799/functions/exit.html（accessed 2026-09-21，权威标准文档，交叉验证）

[D2] "Python subprocess module documentation", Python Software Foundation, Python 3.12, URL: https://docs.python.org/3/library/subprocess.html（accessed 2026-09-21，官方文档，交叉验证）

[D3] "SLURM sbatch documentation: Exit Codes and Signal Handling", SchedMD, 2024.01, URL: https://slurm.schedmd.com/sbatch.html（accessed 2026-09-21，官方文档，交叉验证）

## 证据来源

论文证据缺失。本卡片核心知识来自 POSIX 标准文档、Python 官方文档和 SLURM 官方文档，经交叉验证后作为权威参考级证据写入。

> 注：归因报告指出该知识缺口源于 CLI 执行阶段故障，属于基础设施层问题而非科学领域知识，文献数据库中缺少直接对应的学术论文。本卡片基于权威技术文档构建，证据层级为"权威文档（交叉验证）"。
