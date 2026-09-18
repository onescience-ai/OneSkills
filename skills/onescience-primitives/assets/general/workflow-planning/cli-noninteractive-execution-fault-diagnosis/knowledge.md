# CLI 非交互执行与故障分类知识

## 适用范围
面向命令行工具在非交互环境下的执行与故障诊断，提供退出码分类、错误处理和超时管理的最佳实践。适用于自动化脚本、CI/CD流水线、批处理作业等场景。

## 输入
- 命令行工具的执行命令
- 执行环境参数（操作系统、shell类型、权限级别）
- 预期输出格式和超时时间

## 输出
- 退出码分析结果
- 故障分类诊断
- 恢复策略建议

## 流程节点
1. **命令执行** → 使用subprocess模块或直接调用执行命令
2. **退出码捕获** → 获取进程退出码并分类
3. **错误分析** → 根据退出码范围判断错误类型
4. **故障诊断** → 结合sysexits.h标准进行详细分类
5. **恢复策略** → 根据错误类型制定修复方案

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码0 | 成功 | [D1] POSIX标准 | 命令执行成功 |
| 退出码1-125 | 应用程序错误 | [D1] POSIX标准 | 应用程序定义的错误 |
| 退出码126 | 命令不可执行 | [D1] POSIX标准 | 权限问题或非可执行文件 |
| 退出码127 | 命令未找到 | [D1] POSIX标准 | 路径问题或命令不存在 |
| 退出码128+N | 信号终止 | [D1] POSIX标准 | 被信号N终止（N为信号编号） |

### 校准数值（BSD sysexits.h标准）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| EX_OK (0) | 成功退出 | [D3] FreeBSD手册 | 标准成功退出码 |
| EX_USAGE (64) | 命令使用错误 | [D3] FreeBSD手册 | 参数数量、标志、语法错误 |
| EX_DATAERR (65) | 输入数据错误 | [D3] FreeBSD手册 | 输入格式或内容错误 |
| EX_NOINPUT (66) | 输入文件不存在 | [D3] FreeBSD手册 | 输入文件不可读或不存在 |
| EX_UNAVAILABLE (69) | 服务不可用 | [D3] FreeBSD手册 | 依赖服务不可用 |
| EX_SOFTWARE (70) | 内部软件错误 | [D3] FreeBSD手册 | 程序内部错误 |
| EX_OSERR (71) | 操作系统错误 | [D3] FreeBSD手册 | fork、pipe等系统调用失败 |
| EX_TEMPFAIL (75) | 临时失败 | [D3] FreeBSD手册 | 可重试的临时错误 |
| EX_NOPERM (77) | 权限不足 | [D3] FreeBSD手册 | 权限问题 |
| EX_CONFIG (78) | 配置错误 | [D3] FreeBSD手册 | 配置文件或参数错误 |

## 边界与分流
- **退出码范围判断**：1-125为应用错误，126-127为系统错误，128+为信号终止
- **超时处理**：使用POSIX alarm()或Python subprocess.run(timeout=...)
- **沙箱执行**：使用setuid()/setgid()降权，unshare()/setns()隔离资源
- **异步执行**：使用asyncio.subprocess进行并发进程管理

## 质量检查
- 验证退出码是否在预期范围内
- 检查错误日志是否包含足够诊断信息
- 确认恢复策略是否针对具体错误类型

## 回退策略
- 当退出码无法识别时，记录完整执行上下文
- 当标准错误分类不适用时，使用通用错误处理流程
- 当超时时，记录执行时间和资源使用情况

## 资源召回建议
- 当遇到CLI工具执行失败时召回本卡片
- 当需要诊断自动化脚本错误时召回本卡片
- 当需要设计健壮的错误处理机制时召回本卡片

## 补充证据（用户自有）
[U1] cli_error_handling_references.md文件，包含POSIX标准、Python文档、FreeBSD手册等权威参考（2026-09-17提供）

## 证据来源
[D1] The Open Group Base Specifications Issue 7, 2018 edition - exit, IEEE/The Open Group (POSIX.1-2017), URL: https://pubs.opengroup.org/onlinepubs/9699919799/functions/exit.html
[D2] subprocess — Subprocess management, Python Software Foundation, Python 3.14.7 Documentation, URL: https://docs.python.org/3/library/subprocess.html
[D3] sysexits(3) - FreeBSD Manual Pages, FreeBSD Project, FreeBSD 15.1 Manual Pages, URL: https://www.freebsd.org/cgi/man.cgi?query=sysexits&sektion=3