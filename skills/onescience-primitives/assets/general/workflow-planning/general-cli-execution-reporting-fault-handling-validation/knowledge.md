# General CLI Execution Reporting Fault Handling Validation

## 适用范围
本卡片服务于确保命令行接口（CLI）工具在非交互环境下稳定执行并生成符合结构化契约的报告。适用于任何需要 CLI 工具自动执行、故障诊断和报告验证的场景，例如科学计算任务调度、数据处理流水线、自动化测试等。不适用于交互式 CLI 工具或图形用户界面（GUI）应用。

## 输入
- CLI 命令字符串或参数列表
- 执行环境配置（如沙箱、认证、超时设置）
- 报告生成契约（如 JSON Schema 定义）
- 任务身份标识（如 task_id、task_name）

## 输出
- 执行状态码（退出码）
- 结构化报告（如 JSON 格式）
- 错误日志和诊断信息
- 验证结果（是否符合契约）

## 流程节点
1. **命令解析与验证**：解析 CLI 命令，验证参数格式和认证信息。
2. **环境准备**：配置沙箱、超时、资源限制等执行环境。
3. **执行监控**：监控进程状态、资源使用和超时情况。
4. **故障分类**：根据退出码、错误日志和异常类型进行分类。
5. **报告生成**：按照契约生成结构化报告，包含任务身份和字段完整性。
6. **契约验证**：使用 JSON Schema 或其他验证机制检查报告格式。
7. **诊断与恢复**：基于故障类型提供恢复策略或回退方案。

## 关键参数
### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码 0 | 成功 | [D2] POSIX.1-2017 | 表示命令成功执行 |
| 退出码 1-255 | 失败 | [D2] POSIX.1-2017 | 表示命令执行失败，具体含义由命令定义 |
| 负退出码 -N | 信号终止 | [D3] Python subprocess | 子进程被信号 N 终止（仅 POSIX） |
| 超时设置 | ≥30秒 | [D1] JSON Schema Specification | 避免无限期执行，推荐合理超时值 |
| 沙箱隔离 | 启用 | 安全最佳实践 | 防止命令影响主机系统 |
| subprocess.run timeout | 秒数 | [D3] Python subprocess | 超时后抛出 TimeoutExpired 异常 |
| subprocess.run check | True/False | [D3] Python subprocess | 非零退出码时抛出 CalledProcessError |

### 校准数值
以下数值来自特定任务实例，供量级校准；其他体系需以自身证据重新锚定。
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 任务身份字段 | task_id, task | 归因报告要求 | 报告必须包含顶层任务身份字段 |
| 必填字段 | issues, summary, task, task_id | 归因报告要求 | JSON 报告必须包含这些字段 |
| 数组约束 | issues 必须是数组 | 归因报告要求 | 避免字段类型错误 |
| JSON Schema type | string/number/boolean/array/object/null | [D4] JSON Schema type keywords | 定义数据类型的基本关键字 |
| required 字段 | 数组 | [D4] JSON Schema type keywords | 定义对象必须包含的属性 |

## 边界与分流
- **认证失败**：检查认证令牌是否有效，是否需要刷新或重新获取。
- **超时执行**：根据超时设置终止进程，记录超时原因并尝试恢复。Python subprocess 中超时抛出 TimeoutExpired 异常，需捕获并调用 kill() 清理子进程。
- **沙箱限制**：如果沙箱限制导致命令失败，调整沙箱配置或使用替代方案。
- **报告验证失败**：根据验证错误修复报告生成逻辑，确保字段完整性和类型正确。JSON Schema 验证器应报告具体不匹配字段。
- **退出码非零**：根据退出码分类故障类型（如参数错误、资源不足、依赖缺失），采取相应恢复措施。
- **CalledProcessError**：Python subprocess check=True 时非零退出码抛出此异常，包含 returncode、cmd、output/stdout/stderr 属性。
- **TimeoutExpired**：超时异常包含 cmd、timeout、output/stdout/stderr 属性，捕获后应 kill() 子进程并再次 communicate() 获取剩余输出。

## 质量检查
- 验证退出码是否符合 POSIX 标准或命令特定约定。
- 检查报告是否包含所有必填字段（如 issues, summary, task, task_id）。
- 验证字段类型是否正确（如 issues 必须是数组，summary 必须是非空字符串）。
- 确保任务身份字段与任务索引一致。
- 检查是否有额外顶层字段（应避免）。
- 使用 subprocess.CompletedProcess 检查 returncode 属性判断执行状态。
- 使用 JSON Schema validate() 函数验证报告符合 schema 定义。
- 确保 type 关键字正确指定数据类型（string/number/boolean/array/object/null）。

## 回退策略
- 如果 CLI 命令无法执行，尝试简化命令或使用替代工具。
- 如果报告生成失败，使用模板或默认值填充字段。
- 如果契约验证失败，回退到更宽松的验证规则或手动修复。
- 如果故障分类不确定，记录所有可用信息供人工分析。

## 资源召回建议
当遇到以下情况时召回本卡片：
- CLI 工具在非交互环境下执行失败或超时。
- 结构化报告缺少必填字段或字段类型错误。
- 需要诊断 CLI 执行故障并恢复。
- 需要确保报告符合 JSON Schema 或其他契约。
- 需要设计 CLI 工具的错误处理和报告生成机制。

## 补充证据（开源文档/用户自有，可选）
[D1] JSON Schema Specification, JSON Schema Organization, 版本 2020-12, URL: https://json-schema.org/specification（accessed_at 2026-09-16，权威文档）
[D2] POSIX.1-2017: Exit status, The Open Group, 版本 POSIX.1-2017, URL: https://pubs.opengroup.org/onlinepubs/9699919799/functions/exit.html（accessed_at 2026-09-16，权威文档）
[D3] Python subprocess Module Documentation, Python Software Foundation, 版本 Python 3.14.7, URL: https://docs.python.org/3/library/subprocess.html（accessed_at 2026-09-17，权威文档）覆盖 subprocess.run()、CompletedProcess、TimeoutExpired、CalledProcessError、returncode 语义
[D4] JSON Schema Type-specific Keywords, JSON Schema Organization, 版本 2020-12, URL: https://json-schema.org/understanding-json-schema/reference/type（accessed_at 2026-09-17，权威文档）覆盖 type 关键字定义、数据类型映射、required 属性

## 证据来源
无论文证据。本卡片基于权威文档和最佳实践生成。