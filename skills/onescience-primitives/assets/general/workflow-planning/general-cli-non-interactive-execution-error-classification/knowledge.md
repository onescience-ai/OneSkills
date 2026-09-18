# CLI 非交互执行与故障分类

## 适用范围
适用于需要在非交互式环境（如脚本、自动化流水线、CI/CD）中执行命令行接口（CLI）的场景，覆盖命令参数解析、认证、沙箱、超时、退出码判读和标准错误分析，确保进程稳定完成并保留诊断证据。不适用于交互式会话或图形界面应用。

## 输入
- CLI 命令字符串及其参数
- 执行环境配置（如沙箱、超时设置）
- 预期输出格式（如 JSON、文本）

## 输出
- 进程退出码（0 表示成功，非零表示失败）
- 标准输出（stdout）和标准错误（stderr）内容
- 结构化错误报告（如 JSON 格式）

## 流程节点
1. **命令构建**：根据任务需求构造 CLI 命令，确保参数正确、路径已转义。
2. **执行环境准备**：设置沙箱、超时、工作目录等环境变量。
3. **进程启动**：使用非交互模式启动 CLI 进程，重定向 stdout 和 stderr。
4. **监控与超时处理**：监控进程状态，超时后强制终止并记录超时错误。
5. **退出码分类**：根据退出码判断故障类别（如配置错误、权限不足、资源不可用）。
6. **日志分析**：解析 stdout 和 stderr，提取关键错误信息。
7. **报告生成**：生成结构化错误报告，包含退出码、错误消息、日志片段。

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码 0 | 成功 | [D1][D2] | 进程正常完成 |
| 退出码 1 | 通用错误 | [D1][D2] | 命令执行失败 |
| 退出码 2 | 用法错误 | [D1] | Shell 内置命令误用 |
| 退出码 124 | 超时 | [D3] | timeout 命令超时且未使用 --preserve-status |
| 退出码 125 | timeout 失败 | [D3] | timeout 命令本身失败 |
| 退出码 126 | 权限问题 | [D1][D3] | 命令找到但无法执行 |
| 退出码 127 | 命令未找到 | [D1][D3] | 命令不存在 |
| 退出码 128+n | 致命信号 n | [D1][D2] | 进程被信号 n 终止 |
| 退出码 137 | SIGKILL 终止 | [D1][D3] | 资源超限或手动终止（128+9） |
| 退出码 64-78 | 标准错误 | [D1] | 符合 sysexits.h 标准 |
| 超时默认值 | 30 秒 | [用户自有] | 可根据任务调整 |

### 校准数值

以下数值来自权威文档，供量级校准；其他环境需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码范围 | 0-255 | [D1][D2] | 大多数系统要求在此范围内 |
| 信号终止码 | 128+信号编号 | [D1][D2] | SIGTERM=143, SIGKILL=137 |
| timeout 前台模式 | --foreground | [D3] | 允许命令从 TTY 读取输入 |

## 边界与分流
- **超时处理**：进程超时后强制终止，记录超时错误，报告中标注“超时”。
- **沙箱限制**：沙箱环境可能导致权限不足，需在报告中标注“沙箱限制”。
- **认证失败**：认证错误（如无效凭证）应分类为“认证错误”，并提示检查凭证。
- **资源不可用**：如文件不存在、端口占用，分类为“资源错误”，并提供具体资源路径。

## 质量检查
- 验证退出码是否在预期范围内（如 0-255）。
- 检查 stderr 是否包含关键错误关键词（如 “error”、 “failed”、 “permission denied”）。
- 确保报告包含所有必要字段（退出码、错误消息、日志片段）。

## 回退策略
- 若 CLI 进程无法启动，检查环境变量和依赖项。
- 若退出码无法解析，记录原始退出码和 stderr 内容，转交人工分析。
- 若超时频繁，考虑增加超时时间或优化命令性能。

## 资源召回建议
当任务涉及 CLI 执行、自动化脚本、CI/CD 流水线或故障诊断时召回本卡片。配套资源可能包括：JSON Schema 报告交付契约卡片（general-json-schema-report-delivery-contract）。

## 补充证据（开源权威文档）

[D1] Exit Codes With Special Meanings - Advanced Bash-Scripting Guide, The Linux Documentation Project, 2024, URL: https://tldp.org/LDP/abs/html/exitcodes.html（accessed 2026-09-18，Linux 退出码标准规范）

[D2] sys.exit() - Python官方文档, Python Software Foundation, 3.14.7, URL: https://docs.python.org/3/library/sys.html#sys.exit（accessed 2026-09-18，Python 进程退出机制）

[D3] timeout(1) - Linux manual page, man7.org - Linux man-pages project, 2024, URL: https://man7.org/linux/man-pages/man1/timeout.1.html（accessed 2026-09-18，超时执行与退出码）

## 补充证据（用户自有）

[U1] 归因报告中 CLI 非交互执行与故障分类知识缺口描述，provided_at: 2026-09-17（用户自有, 未经公开源验证）

## 证据来源

[1] Exit Codes With Special Meanings, The Linux Documentation Project, 2024
[2] Python sys.exit() 官方文档, Python Software Foundation, 3.14.7
[3] timeout(1) Linux man page, man7.org, 2024