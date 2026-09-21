# Orchestrator 专家技能召回与融合规范

## 适用范围

面向任意使用 OneScience orchestrator 的科研计算任务，当 orchestrator 在步骤 3（专家召回）命中一个或多个专家技能（如 research-workflow、data-profile）时，本卡规范必须执行的实际调用流程、planner_proposal 收集和规划融合逻辑。适用于避免"专家召回命中但未实际调用"的违规行为。

## 输入

- 意图识别结果（workflow_planning / data_processing / 等）
- 命中的专家技能列表（expert_recall.hit 列表）
- 任务上下文（user_goal、constraints、relevant_artifacts）

## 输出

- 专家规划结果（planner_proposals 列表，每个含工作流节点、资源绑定、依赖关系、执行建议）
- 融合后的统一规划（merged_plan）
- expert_recall 日志（记录每个命中的专家的实际调用状态）

## 流程节点

1. 专家技能匹配 → 并行调用所有命中专家 → 收集 planner_proposal → 融合规划 → 输出 merged_plan
   - 每步含操作、参数、工具、质量门禁

## 关键参数

### 通用判据（方法层，同类体系可参考，逐条带证据编号）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 专家技能命中判定 | 意图向量与专家 SKILL.md description 语义匹配度超过阈值 | [1][3] | 由 orchestrator 步骤 3.2 完成 |
| planner_proposal 必须字段 | workflow_nodes、resource_bindings、dependencies、execution_suggestions | [2] | 缺少任何字段需回退专家重新生成 |
| 融合策略 | 多个专家方案按工作流阶段合并，冲突节点需人工裁决 | [1][3] | 不得因其他专家已返回而跳过未调用的专家 |
| 调用完整性约束 | 只要 expert_recall.hit 非空，必须执行所有命中专家的调用 | [2] | "简化执行"或"跳过"属于违规行为 |

### 校准数值（体系专属值，引语写明"以下数值来自特定体系，供量级校准；其他体系需以自身证据重新锚定"）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 典型命中专家数 | 2-4 个（workflow_planning + data_processing + domain-specific） | [1] | 视任务复杂度而定 |
| planner_proposal 生成超时 | 60s（单个专家） | [3] | 超时需重试或降级 |

## 边界与分流

- 若某个命中专家返回空 proposal（无法规划），记录 skip_reason 并继续其他专家
- 若多个专家方案存在不可调和冲突，提交人工裁决而非静默选择其一
- 若专家技能 SKILL.md 不可加载（文件缺失/格式错误），标记为 BLOCKED 并上报

## 质量检查

- expert_recall 日志中每个 hit 条目必须有对应的实际调用记录
- planner_proposals 列表长度必须等于 expert_recall.hit 列表长度
- merged_plan 必须包含所有命中的工作流阶段

## 回退策略

- 若专家调用失败，按 SKILL.md 的降级策略执行
- 若融合失败，退回单专家模式并记录降级原因

## 资源召回建议

- 当 orchestrator 处理涉及多领域交叉的任务时召回本卡
- 配套资源：技能调用规范卡、任务状态管理卡

## 证据来源

[1] Lakkarasu P. "Operationalizing Intelligence: A Unified Approach to MLOps and Scalable AI Workflows." International Journal of Engineering and Computer Science, 2022, DOI: 10.18535/ijecs.v11i12.4743
[2] Miller T. "Controlled Agentic AI Systems: A Governance-Driven Architecture for Auditable and Reproducible Decision Pipelines." Machine Learning and Knowledge Extraction, 2026, DOI: 10.3390/make8050125
[3] Zhang Z, Valeo C. "Agentic SWMM: Auditable and Reproducible Stormwater Modelling Workflow with Agent Skills and Model Context Protocol." AI for Engineering, 2026, DOI: 10.3390/aieng1010005
[4] Olariu F, Alboaie L. "A Skill-Mediated LLM Workflow for Migrating a.NET Monolith to Cloud-Deployed Microservices." IEEE Access, 2026, DOI: 10.1109/access.2026.3712587