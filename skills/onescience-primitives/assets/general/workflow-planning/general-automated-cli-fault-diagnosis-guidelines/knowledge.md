# 自动化分析工具CLI故障诊断与JSON Schema报告验证指南

## 适用范围
本卡片服务于自动化分析工具在非交互执行环境中的故障诊断与报告交付验证需求。当分析工具以CLI模式运行时，需要处理进程退出码、超时、认证、沙箱限制等故障分类，以及确保输出报告符合JSON Schema契约。适用于各类需要自动化执行和验证的分析工作流。

## 输入
- CLI执行命令及参数
- 预期的JSON Schema报告模板
- 执行环境配置（超时设置、认证信息、沙箱限制）
- 错误日志和退出码

## 输出
- 故障分类诊断报告
- JSON Schema验证结果
- 修复建议和恢复策略
- 诊断证据保留

## 流程节点
1. **CLI执行监控** → 2. **故障检测与分类** → 3. **错误日志分析** → 4. **JSON Schema验证** → 5. **修复策略生成** → 6. **证据保留与报告**

每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 超时时间 | 可配置（秒） | [D1] | 进程执行超时阈值，超时后触发TimeoutExpired异常 |
| 退出码 | 0=成功，非0=失败 | [D1] | 子进程退出状态码，负值表示被信号终止 |
| JSON Schema必填字段 | 依具体报告定义 | [D2] | 报告必须包含的字段列表 |
| 任务身份字段 | task_id, task | [D2] | 用于验证报告与任务匹配的字段 |

## 边界与分流
- **超时故障**：当进程执行超过设定时间，捕获TimeoutExpired异常，记录输出后终止进程
- **非零退出码**：检查CalledProcessError异常，分析退出码类别（环境错误、输入错误、运行时错误）
- **JSON验证失败**：使用JSON Schema校验报告结构，识别缺失字段、类型错误、约束违反
- **认证失败**：检查凭证有效性、权限设置、沙箱限制
- **资源不足**：监控内存、CPU使用，处理资源限制导致的失败

## 质量检查
- 退出码分类准确性验证
- JSON Schema验证完整性检查
- 诊断证据保留完整性
- 修复建议可执行性评估

## 回退策略
- CLI执行失败时：记录详细错误信息，提供替代执行方式建议
- JSON验证失败时：提供具体字段错误定位，建议修复方案
- 完全无法执行时：生成诊断报告，标记为待人工介入

## 资源召回建议
- 当遇到CLI执行异常时召回本卡片
- 当需要验证JSON报告格式时召回本卡片
- 当需要诊断自动化工具故障时召回本卡片
- 配套资源：具体领域的分析工具文档、执行环境配置指南

## 补充证据（开源文档/用户自有，可选）
[D1] subprocess — Subprocess management, Python Software Foundation, Python 3.14.7 documentation, URL: https://docs.python.org/3/library/subprocess.html（accessed_at 2026-09-17，权威文档，交叉验证）
[D2] json — JSON encoder and decoder, Python Software Foundation, Python 3.14.7 documentation, URL: https://docs.python.org/3/library/json.html（accessed_at 2026-09-17，权威文档，交叉验证）
[D3] JSON Schema reference, JSON Schema, 2026, URL: https://json-schema.org/understanding-json-schema/（accessed_at 2026-09-17，权威文档，单源参考）

## 证据来源
[1] subprocess — Subprocess management, Python Software Foundation, Python 3.14.7 documentation, URL: https://docs.python.org/3/library/subprocess.html
[2] json — JSON encoder and decoder, Python Software Foundation, Python 3.14.7 documentation, URL: https://docs.python.org/3/library/json.html
[3] JSON Schema reference, JSON Schema, 2026, URL: https://json-schema.org/understanding-json-schema/