# CLI 非交互执行与故障分类

## 适用范围
适用于 CLI 工具在非交互模式（batch/non-interactive）下的故障诊断、分类与恢复。覆盖归因分析 CLI、数据处理管线、自动化脚本等场景。不适用于交互式 REPL 或 GUI 应用。

## 输入
- CLI 进程的退出码（exit code）
- 标准错误（stderr）输出内容
- 超时配置与实际耗时
- 命令参数与环境变量
- 认证凭证与沙箱配置

## 输出
- 故障类别分类（参数错误/认证失败/沙箱限制/超时/内部错误）
- 结构化诊断报告
- 恢复建议

## 流程节点

### 1. 退出码捕获与分类
```bash
# 标准退出码语义（POSIX）
# 0: 成功
# 1-125: 用户定义错误（应用层）
# 126: 命令不可执行（权限问题）
# 127: 命令未找到（PATH问题）
# 128+N: 被信号N终止（如130=SIGINT=2, 143=SIGTERM=15）
# 255: 退出码超出范围
```
质量门禁：记录 exit_code + signal_name（如有）

### 2. 标准错误解析
- 识别错误关键词：`timeout`, `permission denied`, `authentication failed`, `schema validation error`
- 提取错误位置与行号
- 识别 JSON 语法错误（如 `Expecting property name enclosed in double quotes`）
质量门禁：stderr 非空且包含可解析错误信息

### 3. 超时检测
- 比较实际运行时间与配置超时阈值
- 超时分类：网络超时 / 计算超时 / I/O 超时
- 检查是否存在死锁或无限循环迹象
质量门禁：timeout 发生时记录 elapsed_time 与 threshold

### 4. 认证与沙箱诊断
- 检查 API Key / Token 有效性
- 验证沙箱环境隔离性
- 确认网络可达性（DNS/TCP/HTTPS）
质量门禁：auth_failure 时记录 failure_reason

### 5. 恢复策略生成
| 故障类别 | 恢复动作 |
|---------|---------|
| 参数错误 | 校正参数格式，重试 |
| 认证失败 | 刷新凭证，重试 |
| 沙箱限制 | 调整沙箱配置或申请权限 |
| 超时 | 增加超时阈值或优化负载 |
| 内部错误 | 收集诊断信息，上报 |

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| exit_code | 0-255 | POSIX 标准 | 进程退出状态码 |
| timeout_default | 300s | 工程实践 | 默认超时阈值 |
| max_retries | 3 | 工程实践 | 最大重试次数 |
| stderr_max_size | 1MB | 工程实践 | stderr 捕获上限 |

## 边界与分流
- 退出码 126/127 优先检查 PATH 与文件权限
- 退出码 128+N 优先检查信号来源（SIGTERM/SIGKILL）
- JSON 解析错误优先检查输出格式与编码
- 认证错误优先检查凭证有效期

## 质量检查
- 退出码分类准确性：人工标注 100 条测试用例
- 错误信息提取率：stderr 关键信息覆盖率 > 90%
- 恢复建议采纳率：用户反馈 > 80%

## 回退策略
- 无法分类时标记为 `UNKNOWN` 并保留完整诊断信息
- 超时场景提供 `-v` 详细模式输出
- 认证失败提供凭证刷新指引

## 资源召回建议
- 当检测到 CLI 进程异常退出时召回本卡片
- 当归因分析报告校验失败时召回本卡片
- 配合 `json-schema-report-contract` 卡片使用

## 证据来源
[1] Modern Approaches to Unix Automation: Shell Scripting, Configuration Management, and Security, IJRASET, 2025, DOI: 10.22214/ijraset.2025.72773
[2] ROBOT: A Tool for Automating Ontology Workflows, BMC Bioinformatics, 2019, DOI: 10.1186/s12859-019-3002-3
