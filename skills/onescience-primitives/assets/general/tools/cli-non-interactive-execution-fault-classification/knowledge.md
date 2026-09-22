# CLI非交互执行与故障分类知识

## 适用范围
本卡片覆盖CLI工具在非交互环境下的执行与故障诊断，适用于自动化脚本、CI/CD流水线、批量任务处理等场景。当CLI进程异常退出、超时或输出格式不符合预期时，可按本卡片的分类框架定位故障原因。

## 输入
- CLI命令及参数
- 执行环境（操作系统、shell类型、权限）
- 预期输出格式（JSON、文本等）

## 输出
- 进程退出码（exit code）
- 标准输出（stdout）
- 标准错误（stderr）
- 执行时长

## 流程节点
1. 命令解析 → 参数校验 → 权限检查
2. 进程启动 → 子进程创建 → 执行监控
3. 超时检测 → 信号发送 → 资源清理
4. 退出码收集 → 错误分类 → 恢复策略

每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| timeout | 30-300s | 通用实践 | 超时阈值，视任务复杂度调整 |
| exit_code_0 | 成功 | POSIX标准 | 正常退出 |
| exit_code_1 | 一般错误 | POSIX标准 | 命令执行失败 |
| exit_code_2 | 参数错误 | POSIX标准 | 命令行参数问题 |
| exit_code_126 | 权限错误 | POSIX标准 | 无法执行命令 |
| exit_code_127 | 命令未找到 | POSIX标准 | 命令不存在 |
| exit_code_130 | SIGINT | POSIX标准 | Ctrl+C中断 |
| exit_code_137 | SIGKILL | POSIX标准 | 被强制终止（OOM等） |
| exit_code_143 | SIGTERM | POSIX标准 | 被正常终止信号终止 |

## 边界与分流
- **超时处理**：超时后发送SIGTERM，等待宽限期后发送SIGKILL
- **输出缓冲**：非交互模式下建议关闭输出缓冲（PYTHONUNBUFFERED=1）
- **沙箱环境**：在容器/沙箱中执行时需注意权限和资源限制
- **认证失败**：检查环境变量、配置文件、密钥路径

## 质量检查
- 退出码是否在预期范围内
- stderr内容是否包含错误线索
- 执行时长是否超限
- 输出格式是否符合契约

## 回退策略
- 超时：增加超时值或优化命令参数
- 权限错误：检查执行环境权限配置
- 命令未找到：检查PATH环境变量或使用绝对路径

## 资源召回建议
当遇到以下情况时应召回本卡片：
- CLI进程异常退出
- 自动化脚本超时
- CI/CD流水线失败诊断
- 结构化输出校验失败

## 证据来源
[1] Testing Error Handling Code With Software Fault Injection and Error-Coverage-Guided Fuzzing, IEEE TDSC, 2024, DOI: 10.1109/tdsc.2023.3288876
[2] Bumps in the Code: Error Handling During Software Development, IEEE Software, 2021, DOI: 10.1109/ms.2020.3024981