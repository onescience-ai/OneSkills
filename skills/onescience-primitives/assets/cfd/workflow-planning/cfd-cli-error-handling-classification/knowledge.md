# CLI 非交互执行与故障分类规范

## 适用范围
本卡面向科学计算流水线中 CLI 进程的自动化执行场景，规范非交互环境下的退出码语义、超时管理、信号处理与错误传播机制。适用于 CFD 仿真脚本调用、后处理工具链执行、归因分析 CLI 运行等需要程序化启动外部进程的环节。不适用于交互式终端会话或 GUI 应用。

## 输入
- **目标命令**：待执行的 CLI 命令及参数列表
- **执行环境**：工作目录、环境变量、conda/虚拟环境激活状态
- **超时配置**：最大允许执行时间（秒）
- **重试策略**：可重试错误类别与最大重试次数

## 输出
- **退出码**：进程结束状态码（0=成功，非0=失败）
- **stdout/stderr**：标准输出与标准错误内容
- **超时标志**：是否因超时被终止
- **信号信息**：是否被信号杀死及信号编号

## 流程节点
1. 进程创建 → 使用 `subprocess.run()` 或 `subprocess.Popen()` 启动目标命令
2. 输出捕获 → 设置 `capture_output=True` 分离 stdout/stderr
3. 超时监控 → 设置 `timeout` 参数，超时触发 `TimeoutExpired` 异常
4. 退出码分类 → 根据退出码范围判定错误类别
5. 错误传播 → 根据错误类别决定重试、降级或中止

每步含：操作、参数、工具、质量门禁

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码 0 | 成功 | POSIX.1-2017 [D1] | 命令正常完成 |
| 退出码 1 | 通用错误 | POSIX.1-2017 [D1] | 未分类的应用错误 |
| 退出码 2 | Shell 用法错误 | POSIX.1-2017 [D1] | 内建命令误用或参数缺失 |
| 退出码 64-113 | 用户自定义 | POSIX.1-2017 [D1] | 预留给应用程序定义具体错误类型 |
| 退出码 126 | 无法执行 | POSIX.1-2017 [D1] | 权限问题或非可执行文件 |
| 退出码 127 | 命令未找到 | POSIX.1-2017 [D1] | PATH 中不存在该命令 |
| 退出码 128+N | 致命信号 N | POSIX.1-2017 [D1] | 进程被信号 N 杀死（如 137=SIGKILL） |
| 退出码 130 | SIGINT 中断 | POSIX.1-2017 [D1] | 用户按 Ctrl-C（128+2=130） |
| 退出码 255 | 范围外 | Bash [D2] | exit 参数超出 0-255 范围 |

### 校准数值（Python subprocess 行为）
以下数值来自 Python 3.14 subprocess 模块文档 [D3]，供量级校准；其他语言运行时需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| `timeout` 参数 | 秒数（int/float） | Python [D3] | 超时后抛出 `TimeoutExpired` |
| `timeoutExpired.stdout` | bytes/str | Python [D3] | 超时前已捕获的部分输出 |
| `proc.kill()` | 发送 SIGKILL | Python [D3] | Windows 上等同于 `terminate()` |
| `check=True` | 抛出 CalledProcessError | Python [D3] | 非零退出码触发异常 |

## 边界与分流

| 前提条件 | 不成立时的转向方案 |
|----------|-------------------|
| 目标命令存在于 PATH | 转向：检查 conda 环境是否激活、PATH 是否正确设置 |
| 进程在超时内完成 | 转向：增加超时值或优化命令性能 |
| 退出码在 0-255 范围 | 转向：检查脚本 exit 语句，确保参数为正整数 |
| stderr 可被捕获 | 转向：重定向 stderr 到文件后读取 |

## 质量检查

| 验证点 | 阈值 | 失败处理 |
|--------|------|----------|
| 进程成功启动 | 无 FileNotFoundError/PermissionError | 记录异常，标记为配置错误 |
| 退出码分类正确 | 对照退出码表 | 重新审查分类规则 |
| 超时后资源清理 | 进程已终止、管道已关闭 | 强制 kill 并等待回收 |
| stderr 有效捕获 | 非空时记录 | 无 stderr 不阻塞流程 |

## 回退策略
- 命令不存在 → 检查环境配置，提供安装指引
- 超时 → 重试一次并加倍超时值，仍超时则中止并报告
- 权限拒绝 → 检查文件权限，必要时使用 sudo 或修改 chmod
- 信号杀死 → 记录信号编号，排查 OOM 或段错误原因

## 资源召回建议
当任务涉及以下场景时应召回本卡片：
- 调用外部 CLI 工具（如 OpenFOAM 求解器、ParaView 后处理）
- 执行归因分析脚本或自动化测试
- 构建 CI/CD 流水线中的科学计算步骤
- 需要程序化处理 CLI 进程失败的情况

配套卡片：`cfd-json-schema-report-validation`（报告交付契约校验）

## 证据来源
[1] Watchdog – A Workflow Management System for the Distributed Analysis of Large-Scale Experimental Data, Kluge & Friedel, BMC Bioinformatics, 2018, DOI: 10.1186/s12859-018-2355-5
[2] A Framework for Automated API Fuzzing at Enterprise Scale, Mahmood et al., IEEE ICST, 2022, DOI: 10.1109/ICST53961.2022.00015
[3] Heptapod: Orchestrating High Energy Physics Workflows Towards Autonomous Agency, Menzo et al., arXiv, 2025, DOI: arXiv:2502.15431
[4] Common Workflow Language, v1.0, Amstutz et al., CWL Specification, 2016, DOI: 10.6084/m9.figshare.4641112
[5] Scientific Workflows: Moving Across Paradigms, Liew et al., ACM Computing Surveys, 2016, DOI: 10.1145/2921618

[D1] POSIX.1-2017 Shell Command Language Standard, IEEE/The Open Group
[D2] GNU Bash Reference Manual, Appendix E: Exit Codes, Free Software Foundation
[D3] Python 3.14 subprocess Module Documentation, Python Software Foundation

## 补充证据（开源文档）
[D4] Linux man-pages: exit(3), Linux man-pages project, version 6.19, URL: https://man7.org/linux/man-pages/man3/exit.3.html（accessed_at 2026-09-18，交叉验证）