# AI编排系统工具调用接口契约

## 适用范围

面向AI编排系统中type=expert技能的工具调用场景，解决调用时仅传name参数导致的无效调用问题。适用于所有需要结构化请求负载的工具调用接口，包括但不限于OneScience编排体系中的skill工具、多智能体系统中的专家技能调用、以及需要上下文传递的工具路由场景。

## 输入

- 调用方身份信息（from_skill）
- 任务状态摘要（task_state_summary）
- 意图分析结果（intent_profile）
- 已召回资源列表（matched_resources）
- 当前分配的方面（assigned_aspect）

## 输出

- 结构化的规划请求负载（planning_request）
- 专家技能的规划提案（planner_proposal）
- 工具调用的成功/失败状态

## 流程节点

1. **上下文收集** → 收集调用方身份、任务状态、意图分析、已召回资源等信息
2. **请求负载构建** → 将收集的信息组织成结构化的planning_request负载
3. **工具调用执行** → 将完整负载传递给目标专家技能
4. **响应解析** → 解析专家技能返回的planner_proposal
5. **状态更新** → 根据调用结果更新任务状态

每步含：操作、参数、工具、质量门禁

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| from_skill | string | 调用方 | 调用技能的标识符，必填 |
| task_state_summary | object | 任务状态 | 当前任务状态摘要，必填 |
| intent_profile | object | 意图分析 | 用户意图分析结果，必填 |
| matched_resources | array | 资源召回 | 已召回的资源列表，必填 |
| assigned_aspect | string | 规划分配 | 当前分配的规划方面，必填 |

### 校准数值

以下数值来自OneScience编排体系，供量级校准；其他体系需以自身证据重新锚定：

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 最小请求字段数 | 5 | 归因报告 | 至少包含5个必填字段 |
| 无效调用检测阈值 | 3次 | 归因报告 | 连续3次相同调用模式应触发降级 |

## 边界与分流

- **参数缺失**：当planning_request缺少必填字段时，工具应返回明确的参数校验错误，而非静默失败
- **重复调用检测**：当检测到连续N次相同调用模式时，应触发降级策略（见general-agent-error-recovery-strategy卡片）
- **专家技能不可用**：当专家技能无法处理请求时，应返回明确的错误码，调用方可切换到直接规划路径（见general-agent-fallback-execution-mode卡片）

## 质量检查

- 验证planning_request包含所有必填字段
- 验证字段类型符合接口规范
- 验证调用方身份与任务上下文一致
- 失败处理：参数校验失败时返回具体错误信息，不执行后续逻辑

## 回退策略

- 当专家技能调用失败时，可降级为直接规划模式
- 当工具返回非预期响应时，记录日志并触发异常恢复流程
- 当连续调用失败超过阈值时，自动切换到替代执行路径

## 资源召回建议

- 何时应召回本卡片：当编排智能体需要调用type=expert技能时
- 配套资源：general-agent-error-recovery-strategy（异常恢复）、general-agent-fallback-execution-mode（降级路径）

## 证据来源

[1] AI Agent Systems: Architectures, Applications, and Evaluation, Bin Xu, arXiv, 2026, DOI: 10.48550/arXiv.2601.01743
[2] SLM-Based Agentic AI with P-C-G: Optimized for Korean Tool Use, Changhyun Jeon et al., arXiv, 2025, DOI: 10.48550/arXiv.2509.19369
[3] Establishing Guardrails for AI Tool Use: Formal Safety Constraints Using MCP Schemas, Gaurav Rohatgi, IJIRMPS, 2025, DOI: 10.37082/ijirmps.v13.i6.232848
