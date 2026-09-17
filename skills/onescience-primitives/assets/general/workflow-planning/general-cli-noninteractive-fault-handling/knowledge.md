# CLI非交互执行与故障分类

## 适用范围

面向需要在自动化流水线、后台任务或无用户干预环境中调用命令行工具的场景，提供进程创建、执行监控、退出码解析与故障恢复的通用方法。适用于需要批量调用外部程序、构建自动化工作流或处理CLI工具异常退出的情况。

## 输入

- 待执行的命令及其参数
- 可选的环境变量配置
- 可选的超时时间设置
- 可选的输入数据（stdin）

## 输出

- 进程执行结果（stdout、stderr）
- 退出码（returncode）
- 异常信息（TimeoutExpired、CalledProcessError等）

## 流程节点

1. **命令构建** → 构建参数列表，避免shell注入风险
2. **进程创建** → 使用subprocess.run()或Popen()启动子进程
3. **输入输出管理** → 配置stdin/stdout/stderr管道重定向
4. **超时控制** → 设置timeout参数防止进程挂起
5. **退出码检查** → 分类解析退出码，识别故障类型
6. **异常处理** → 捕获并处理TimeoutExpired、CalledProcessError等异常

每步含：操作、参数、工具、质量门禁

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| check | True/False | [D1] | 是否在非零退出码时抛出CalledProcessError |
| timeout | 秒数 | [D1] | 超时后自动终止进程 |
| capture_output | True/False | [D1] | 是否捕获stdout和stderr |
| shell | True/False | [D1] | 是否通过shell执行命令 |
| stdin | PIPE/DEVNULL/None | [D1] | 标准输入重定向方式 |
| stdout | PIPE/DEVNULL/STDOUT/None | [D1] | 标准输出重定向方式 |
| stderr | PIPE/DEVNULL/STDOUT/None | [D1] | 标准错误重定向方式 |

## 退出码分类

| 退出码 | 含义 | 来源 | 说明 |
|--------|------|------|------|
| 0 | 成功 | [D2] | 进程正常执行完成 |
| 1 | 一般错误 | [D2] | 捕获类通用错误 |
| 2 | Shell内置命令误用 | [D2] | 缺少关键字或权限问题 |
| 126 | 命令不可执行 | [D2] | 权限问题或非可执行文件 |
| 127 | 命令未找到 | [D2] | PATH问题或拼写错误 |
| 128 | exit参数无效 | [D2] | exit参数超出0-255范围 |
| 128+n | 致命信号n | [D2] | 进程被信号n终止 |
| 130 | Ctrl+C终止 | [D2] | 用户中断（信号2） |

## 边界与分流

- **超时处理**：当timeout参数指定且进程未在指定时间内完成时，抛出TimeoutExpired异常，需捕获后调用kill()终止进程并调用communicate()清理管道
- **非零退出码**：当check=True时抛出CalledProcessError，需捕获并根据returncode分类诊断
- **shell=True风险**：通过shell执行时存在命令注入风险，应优先使用参数列表形式
- **管道死锁**：使用stdout=PIPE时，若子进程输出量大可能阻塞，应使用communicate()而非直接read()

## 质量检查

- 验证点：进程是否在超时时间内完成
- 验证点：退出码是否为0或预期值
- 验证点：stdout/stderr是否成功捕获
- 失败处理：根据退出码分类采取相应恢复策略

## 回退策略

- 进程创建失败：检查命令路径、权限、环境变量
- 超时失败：增加timeout值或优化子进程性能
- 非零退出：根据退出码分类诊断，修正参数或环境后重试
- 管道死锁：使用communicate()替代直接管道读写

## 资源召回建议

当任务涉及以下场景时召回本卡片：
- 需要调用外部CLI工具执行计算或处理任务
- 需要处理CLI工具的异常退出或超时
- 需要构建自动化测试或部署流水线
- 需要批量处理多个外部程序调用

配套资源：general-json-schema-report-contract（输出格式校验）

## 补充证据（开源权威文档）

[D1] subprocess - Subprocess management, Python Software Foundation, Python 3.14.7, URL: https://docs.python.org/3/library/subprocess.html (accessed 2026-09-17, 官方权威文档)

[D2] Exit Codes With Special Meanings, The Linux Documentation Project, Advanced Bash-Scripting Guide Appendix E, URL: https://tldp.org/LDP/abs/html/exitcodes.html (accessed 2026-09-17, 官方权威文档)

## 证据来源

[D1] subprocess - Subprocess management, Python Software Foundation, https://docs.python.org/3/library/subprocess.html
[D2] Exit Codes With Special Meanings, The Linux Documentation Project, https://tldp.org/LDP/abs/html/exitcodes.html
