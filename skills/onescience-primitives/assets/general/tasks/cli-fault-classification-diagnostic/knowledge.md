# CLI 非交互执行故障分类与诊断

## 适用范围
适用于命令行接口（CLI）程序在非交互模式下执行时出现的各类故障诊断。覆盖进程退出码判读、超时检测、信号中断处理、标准错误输出解析等场景。适用于自动化流水线、CI/CD 集成、远程执行环境中的 CLI 工具故障排查。

## 输入
- CLI 进程的退出码（exit code）
- 标准错误（stderr）输出内容
- 进程运行日志（stdout/stderr 重定向文件）
- 超时配置与实际耗时
- 信号记录（SIGTERM/SIGKILL/SIGINT 等）

## 输出
- 故障分类结果（成功/参数错误/认证失败/超时/信号中断/运行时异常）
- 根因定位建议
- 恢复策略推荐

## 流程节点
1. **退出码收集** → 收集进程返回的退出码
2. **退出码分类** → 按 POSIX 惯例和应用约定进行分类
3. **stderr 解析** → 提取错误关键字和上下文
4. **超时检测** → 判断是否因超时被终止
5. **信号分析** → 识别信号中断类型
6. **综合诊断** → 结合多维度信息给出故障类型

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码 0 | 成功 | [D1] POSIX 标准 | 进程正常完成 |
| 退出码 1-2 | 通用错误 | [D1] POSIX 惯例 | 应用特定错误或误用 |
| 退出码 126 | 权限不足 | [D1] POSIX 标准 | 命令不可执行 |
| 退出码 127 | 命令未找到 | [D1] POSIX 标准 | PATH 中找不到命令 |
| 退出码 128+N | 信号终止 | [D1] POSIX 标准 | 被信号 N 终止（如 130=SIGINT, 137=SIGKILL） |
| 退出码 255 | 退出码越界 | [D1] POSIX 惯例 | 超出有效范围 |
| 超时退出码 | 124（timeout 命令） | [D1] GNU coreutils | 超时被终止 |
| SIGTERM | 15 | [D1] POSIX 标准 | 优雅终止请求 |
| SIGKILL | 9 | [D1] POSIX 标习 | 强制终止（不可捕获） |

## 边界与分流
- 退出码为 0 但 stderr 有输出 → 诊断为"警告级"（成功但有隐患）
- 退出码为 124 + stderr 含 timeout 关键字 → 确认为超时故障
- 退出码为 128+N → 信号中断，N 对应信号编号
- 退出码为空或无法获取 → 进程可能被 SIGKILL 强杀或系统级故障
- stderr 含认证/权限关键字 → 分流到认证故障子类

## 质量检查
- 退出码必须在 0-255 范围内（POSIX 规范）
- stderr 解析需过滤 ANSI 转义序列
- 超时检测需校验 timeout 配置与实际耗时
- 信号分析需区分应用层信号和系统层信号

## 回退策略
- 退出码不可获取时，检查进程是否存在（ps/kill -0）
- stderr 为空时，检查文件描述符重定向配置
- 超时判定不确定时，增加 10% 容差重新测试

## 资源召回建议
- 当任务涉及 CLI 工具执行、自动化流水线故障排查时召回本卡
- 配套资源：json-schema-report-contract-validation（报告格式校验）

## 证据来源
[1] Testing Error Handling Code With Software Fault Injection and Error-Coverage-Guided Fuzzing, Bai et al., IEEE TDSC, 2024, DOI: 10.1109/tdsc.2023.3288876
[2] Bumps in the Code: Error Handling During Software Development, Lopez et al., IEEE Software, 2021, DOI: 10.1109/ms.2020.3024981
[3] Detraque: Dynamic execution tracing techniques for automatic fault localization, Wu et al., PLOS ONE, 2022, DOI: 10.1371/journal.pone.0274515
[D1] The GNU C Library Manual - Exit Status, Free Software Foundation, v2.44, https://www.gnu.org/software/libc/manual/html_node/Exit-Status.html
