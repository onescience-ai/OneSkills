# CLI执行与JSON Schema验证通用故障诊断与报告交付契约

## 适用范围
面向命令行工具执行和JSON模式验证的通用问题类，涵盖非交互执行模式、退出码分类、标准错误解读以及JSON Schema验证的必填字段、任务身份、数组约束和输出格式规范。适用于需要自动化执行CLI工具并验证其输出是否符合JSON Schema规范的场景，如归因分析、数据处理、报告生成等自动化工作流。不适用于需要人工交互的CLI操作或非JSON格式的输出验证。

## 输入
- CLI命令行参数和选项
- 环境变量和配置文件
- JSON Schema定义文件
- 待验证的JSON数据或报告

## 输出
- 执行结果（成功/失败/超时）
- 退出码和标准错误信息
- JSON Schema验证结果（通过/失败及错误详情）
- 结构化报告（符合指定Schema）

## 流程节点
1. **CLI非交互执行配置** → 设置命令行参数、超时时间、沙箱环境
2. **执行监控** → 监控进程状态、捕获输出流、处理超时
3. **退出码分类** → 根据退出码判断执行状态（成功、失败、超时等）
4. **标准错误解读** → 解析stderr输出，识别错误类型和原因
5. **JSON Schema验证** → 使用验证器检查输出是否符合Schema
6. **报告生成** → 生成符合Schema的结构化报告
7. **故障诊断** → 结合退出码、错误信息和验证结果进行综合诊断

每步含：操作、参数、工具、质量门禁

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码范围 | 0-255 | [标准UNIX规范] | 0表示成功，非0表示各种错误状态 |
| 超时时间 | 可配置 | [用户设置] | 根据任务复杂度设置合理超时 |
| 沙箱级别 | 可选 | [安全要求] | 根据安全需求选择沙箱隔离级别 |
| Schema版本 | Draft 2019-09+ | [JSON Schema规范] | 支持现代JSON Schema特性 |
| 验证模式 | 严格/宽松 | [应用需求] | 严格模式要求所有字段，宽松模式允许可选字段 |

### 校准数值
以下数值来自CLI执行和JSON Schema验证实践，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 典型超时时间 | 30-300秒 | [CLI执行经验] | 根据任务复杂度调整 |
| 常见退出码 | 0,1,2,126,127,130 | [UNIX标准] | 0成功，1一般错误，2误用，126权限问题，127命令未找到，130中断 |
| JSON Schema复杂度 | PTIME到PSPACE | [论文[1]] | Classical JSON Schema验证是PTIME，Modern JSON Schema验证是PSPACE-complete |
| 验证性能提升 | 平均10倍 | [论文[3]] | 编译优化可显著提高验证速度 |

## 边界与分流
1. **CLI执行失败**：检查退出码和标准错误，常见原因包括命令不存在（127）、权限不足（126）、参数错误（2）等。
2. **JSON Schema验证失败**：检查验证错误详情，可能原因包括缺少必填字段、类型不匹配、格式错误等。
3. **超时处理**：设置合理超时，超时后终止进程并记录诊断信息。
4. **沙箱限制**：在沙箱环境中执行时，注意文件系统、网络等访问限制。
5. **Schema版本不兼容**：确保使用的JSON Schema版本与验证器支持版本匹配。

## 质量检查
1. CLI命令能够正确执行并返回预期退出码
2. 标准错误信息能够被正确捕获和解析
3. JSON Schema验证能够准确识别有效和无效数据
4. 生成的报告符合指定Schema要求
5. 故障诊断能够提供有用的错误信息和修复建议

## 回退策略
1. **CLI执行回退**：如果主要执行方式失败，尝试简化命令或使用替代工具
2. **验证回退**：如果严格验证失败，切换到宽松验证模式
3. **报告生成回退**：如果完整报告生成失败，生成简化报告或错误报告
4. **诊断回退**：如果自动诊断失败，提供原始错误信息供人工分析

## 资源召回建议
当遇到以下场景时应召回本卡片：
- 需要自动化执行CLI工具并验证其输出
- 需要处理CLI工具的退出码和错误信息
- 需要验证JSON数据是否符合特定Schema
- 需要生成符合Schema的结构化报告
- 需要进行CLI工具故障诊断

配套资源：CLI执行工具、JSON Schema验证器、错误日志分析工具

## 补充证据（开源文档/用户自有，可选）
（当前无补充证据）

## 证据来源
[1] Validation of Modern JSON Schema: Formalization and Complexity, Lyes Attouche et al., arXiv, 2024, DOI: 10.48550/arXiv.2307.10034
[2] Elimination of annotation dependencies in validation for Modern JSON Schema, Lyes Attouche et al., arXiv, 2025, DOI: 10.48550/arXiv.2503.11288
[3] Blaze: Compiling JSON Schema for 10x Faster Validation, Juan Cruz Viotti et al., arXiv, 2025, DOI: 10.48550/arXiv.2503.02770
[4] Negation-Closure for JSON Schema, Mohamed-Amine Baazizi et al., arXiv, 2022, DOI: 10.48550/arXiv.2202.13434
[5] Witness Generation for JSON Schema, Lyes Attouche et al., arXiv, 2022, DOI: 10.48550/arXiv.2202.12849
[6] Not Elimination and Witness Generation for JSON Schema, Mohamed-Amine Baazizi et al., arXiv, 2021, DOI: 10.48550/arXiv.2104.14828
[7] Synthesizing JSON Schema Transformers, Jack Stanek et al., arXiv, 2024, DOI: 10.48550/arXiv.2405.17681