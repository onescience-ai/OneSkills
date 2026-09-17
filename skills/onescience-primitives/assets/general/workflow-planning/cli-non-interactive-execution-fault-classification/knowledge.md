# CLI 非交互执行与故障分类知识

## 适用范围

本卡片服务于命令行接口（CLI）在非交互式环境中的执行与故障诊断任务。适用于自动化脚本、CI/CD流水线、批量任务执行、远程服务器调度等场景，帮助开发者和运维人员理解CLI进程的退出状态、异常分类、超时处理与恢复策略。适用于Python subprocess模块、Shell脚本、批处理文件等各类CLI执行环境。

## 输入

- CLI命令与参数
- 执行环境信息（操作系统、Shell类型、环境变量）
- 超时设置（秒）
- 输入数据流（stdin）
- 输出捕获配置（stdout/stderr重定向）

## 输出

- 进程退出码（returncode）
- 标准输出（stdout）
- 标准错误（stderr）
- 异常信息（如发生错误）
- 执行状态报告（成功/失败/超时）

## 流程节点

1. **命令构建与参数化** → 构建CLI命令序列，处理参数转义与引号
2. **进程创建与执行** → 使用subprocess.Popen或run()启动子进程
3. **输入输出管理** → 通过管道重定向stdin/stdout/stderr
4. **超时监控与强制终止** → 设置timeout参数，超时后kill子进程
5. **退出码收集与解读** → 获取returncode，分类故障类型
6. **异常处理与恢复** → 捕获TimeoutExpired、CalledProcessError等异常

每步含：操作、参数、工具、质量门禁

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码0 | 成功 | [D1] | 进程正常退出，无错误 |
| 退出码非0 | 失败 | [D1] | 进程异常退出，需诊断具体原因 |
| 退出码- N | 被信号终止 | [D1] | 进程被信号N终止（仅POSIX） |
| timeout参数 | 秒数 | [D1] | 设置进程最大执行时间 |
| check=True | 启用 | [D1] | 非零退出码自动抛出CalledProcessError |
| capture_output | True/False | [D1] | 是否捕获stdout/stderr |

### 校准数值

以下数值来自Python subprocess模块文档，供量级校准；其他编程语言或Shell环境需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认shell | /bin/sh（POSIX）| [D1] | shell=True时使用的默认Shell |
| 默认shell | %COMSPEC%（Windows）| [D1] | Windows上shell=True时使用的默认Shell |
| 超时异常 | TimeoutExpired | [D1] | 超时后抛出的异常类型 |
| 非零退出异常 | CalledProcessError | [D1] | check=True时非零退出码抛出的异常 |
| 进程组创建 | CREATE_NEW_PROCESS_GROUP | [D1] | Windows上创建新进程组的标志 |

## 边界与分流

- **退出码0但有错误输出**：进程可能部分成功，需检查stderr内容
- **超时但进程未终止**：需手动调用proc.kill()强制终止
- **Shell注入风险**：避免使用shell=True处理不可信输入，使用参数列表而非字符串
- **管道死锁**：避免直接读写stdin/stdout/stderr管道，使用communicate()方法
- **信号处理差异**：POSIX与Windows信号处理机制不同，需平台适配

## 质量检查

- 验证退出码是否在预期范围内（0表示成功）
- 检查stderr是否有错误信息
- 验证超时设置是否合理（避免过短导致误判）
- 检查进程是否完全终止（避免僵尸进程）
- 验证输出编码是否正确（避免乱码）

## 回退策略

- 退出码异常时，尝试使用不同参数重新执行
- 超时后，增加超时时间或优化命令性能
- Shell环境不兼容时，使用绝对路径或容器化执行
- 权限不足时，使用sudo或调整文件权限

## 资源召回建议

- 当需要诊断CLI执行失败时召回本卡片
- 当需要处理自动化脚本的错误恢复时召回本卡片
- 当需要理解进程退出码含义时召回本卡片
- 配套资源：Python subprocess模块文档、操作系统进程管理文档

## 补充证据（开源文档）

[D1] subprocess — Subprocess management, Python Software Foundation, 3.14.7, URL: https://docs.python.org/3/library/subprocess.html（accessed_at 2026-09-17，交叉验证）
[D2] Built-in Exceptions, Python Software Foundation, 3.14.7, URL: https://docs.python.org/3/library/exceptions.html（accessed_at 2026-09-17，交叉验证）

## 证据来源

[1] Python subprocess模块官方文档
[2] Python内置异常官方文档