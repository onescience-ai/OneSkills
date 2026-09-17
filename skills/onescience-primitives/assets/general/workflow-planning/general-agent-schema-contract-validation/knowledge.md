# 自动化智能体结构化输出 Schema 契约验证

## 适用范围

自动化智能体生成的结构化输出（JSON 格式报告、API 调用参数、任务状态对象）需要符合预定义的 JSON Schema 契约。本卡覆盖 schema 校验的正确性保障、运行时解码控制、语义层验证以及报告交付的完整性检查。适用于任何需要保证 agent 输出符合结构化契约的场景，包括科研报告生成、自动化测试报告、API 交互和数据管道。不适用于非结构化文本输出或二进制格式。

## 输入

- JSON Schema 定义文件（必填字段、类型约束、嵌套结构）
- Agent 生成的 JSON 输出
- 领域验证规则（语义层约束，超出 schema 表达能力）
- 任务身份元数据（task_id、task name，用于一致性校验）

## 输出

- Schema 合规性判定（pass/fail + 违规字段列表）
- 语义合规性判定（领域规则通过率）
- 修复建议（针对违规字段）
- 验证证据报告

## 流程节点

### 1. Schema 静态校验（Schema Validation）

操作：使用 JSON Schema validator 对 agent 输出进行结构校验。

关键发现 [1]：JSON Schema 提供的结构校验是"必要的接口层，但不是领域验证和失败关闭执行的替代品"（"structured output is a necessary interface layer, not a substitute for domain verification and fail-closed execution"）。

工具：jsonschema（Python）、Ajv（JavaScript）、Blaze [4]（高性能编译器）

质量门禁：
- 所有必填字段必须存在
- 字段类型必须匹配 schema 定义
- 嵌套结构必须符合嵌套 schema
- 数组约束（minItems、maxItems、uniqueItems）必须满足

### 2. 任务身份一致性校验（Identity Consistency）

操作：校验报告中的 task_id 和 task name 与任务索引一致。

常见违规：
- task_id 缺失或与任务索引不匹配
- task name 与任务定义不一致
- 顶层字段不符合预期 schema（多余字段、缺失字段）

工具：字段级对比器

质量门禁：task_id 和 task name 必须与任务定义精确匹配

### 3. 运行时解码控制（Runtime Decoding Control）

操作：在 LLM 生成过程中实时监控输出，检测偏离契约的倾向。

关键发现 [2]：ATLAS-RTC 在解码每一步监控生成过程，使用轻量信号检测偏离，并在错误物化之前应用干预（偏置、遮蔽、回滚）。首次尝试成功率提升 20 至 37.8 个百分点，失败主导场景下延迟降低最高 88%。

关键发现 [2]：许多失败源于解码伪影（decoding artifacts）而非任务误解，表明运行时控制应作为 LLM 系统的独立层。

方法：
- 逐步解码监控
- 输出契约偏离检测
- 定向干预（biasing、masking、rollback）

工具：ATLAS-RTC、constrained decoding 框架

质量门禁：运行时控制不得引入超过 10% 的额外延迟

### 4. 语义层验证（Semantic Verification）

操作：在 schema 校验之上，进行领域语义验证。

关键发现 [1]：在 OrderBench 基准测试中，即使最强模型达到 100% schema 合规性，语义成功率仍仅约 80%；较弱模型的 schema 合规但语义错误的不安全接受率达到两位数。

这意味着 schema 校验只能保证语法正确性，不能保证语义正确性。需要额外的领域验证层。

方法：
- 领域规则引擎（检查业务逻辑约束）
- 交叉引用验证（检查字段间一致性）
- 失败关闭策略（语义验证失败时拒绝输出）

工具：领域验证器、规则引擎

质量门禁：语义验证必须覆盖所有关键业务规则

### 5. 报告交付契约保障（Report Delivery Contract）

操作：确保最终报告符合预定义的交付契约。

常见契约要求：
- 顶层字段完整性（必填字段全部存在）
- 数组类型字段为数组（非 null、非字符串）
- 字段类型一致性（如 issues 必须是数组，summary 必须是非空字符串）
- 任务身份与索引一致

工具：契约校验器、JSON Schema validator

质量门禁：交付前必须通过 schema 校验 + 任务身份一致性校验

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Schema 合规 ≠ 语义正确 | 是 | [1] | 最强模型 100% schema 合规但语义成功率仅 ~80% |
| 运行时控制成功率提升 | 20~37.8 pp | [2] | ATLAS-RTC 相比后验校验的提升幅度 |
| 运行时控制延迟降低 | 最高 88% | [2] | 在失败主导场景下的延迟优化 |
| 现代 JSON Schema 复杂度 | PSPACE-complete | [3] | 含动态引用的 schema 验证复杂度 |
| Blaze 加速比 | ~10× | [4] | 编译后 schema 验证相比传统验证器 |

### 校准数值

以下数值来自具体 benchmark 体系，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| OrderBench 调用数 | 2,400 | [1] | 四个开放模型 × prompt-only 和 JSON-schema 模式 |
| OrderBench 语义成功率上限 | ~80% | [1] | 最强模型在两种模式下的语义成功率 |
| 不安全接受率 | 两位数 | [1] | 较弱模型在 schema 合规模式下的语义错误率 |

## 边界与分流

1. **Schema 定义不完整**：当 schema 无法表达所有业务约束时，必须补充语义验证层。schema 校验是必要条件而非充分条件。
2. **动态 schema 变更**：当 schema 在运行时被修改时，验证器必须重新加载或重新编译。建议 schema 变更走版本管理。
3. **验证性能瓶颈**：当 schema 复杂度导致验证延迟不可接受时，考虑使用编译型验证器（如 Blaze [4]）或缓存验证结果。
4. **语义验证规则缺失**：当领域规则未被形式化时，降级为 schema 校验 + 人工审核。
5. **LLM 输出漂移**：当运行时检测到输出持续偏离契约时，触发重新生成或回退到更保守的 prompting 策略。

## 质量检查

- 所有 agent 输出在交付前必须通过 JSON Schema 校验
- 报告的 task_id 和 task name 必须与任务定义一致
- schema 校验通过后必须进行语义层验证
- 验证失败的输出不得交付给下游
- 验证过程本身不得引入不可接受的延迟

## 回退策略

1. Schema 校验失败 → 返回具体违规字段和修复建议
2. 语义验证失败 → 拒绝输出，请求重新生成
3. 验证器性能不足 → 降级为简化 schema 或采样验证
4. 动态 schema 无缓存 → 使用实时编译验证器

## 资源召回建议

当遇到以下场景时召回本卡片：
- agent 输出的 JSON 报告字段校验失败
- 需要设计结构化输出的交付契约
- LLM 生成的 JSON 不符合预期 schema
- 需要在 agent 工作流中实现输出验证层
- 报告中的 task_id/task name 与任务索引不一致

配套资源：general-agent-cli-fault-classification-recovery（执行层故障分类与恢复）

## 证据来源

[1] Yin Li, "When JSON Is Not Enough: Semantic Reliability of Schema-Constrained LLM Ordering Agents", arXiv, 2026, DOI: 10.48550/arXiv.2607.18261
[2] Christopher Cruz, "ATLAS-RTC: Closing the Loop on LLM Agent Output with Token-Level Runtime Control", arXiv, 2026, DOI: 10.48550/arXiv.2603.27905
[3] Lyes Attouche et al., "Validation of Modern JSON Schema: Formalization and Complexity", arXiv, 2023, DOI: 10.48550/arXiv.2307.10034
[4] Juan Cruz Viotti et al., "Blaze: Compiling JSON Schema for 10x Faster Validation", arXiv, 2025, DOI: 10.48550/arXiv.2503.02770
