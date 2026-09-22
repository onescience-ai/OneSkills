# OneScience Expert Planning Fusion

## 适用范围
面向OneScience orchestrator在步骤3.x调用专家技能（onescience-research-workflow、onescience-data-profile等）时的规范流程，覆盖专家规划结果（planner_proposal）的收集、融合与决策。适用于任何需要多个专家技能提供领域规划建议的复合科研任务；不适用于单一专家技能的内部执行逻辑。

## 输入
- orchestrator步骤3.x的意图识别结果（哪些方面命中了哪些专家）
- 每个命中的专家技能的输入上下文
- 已识别的资源约束和领域知识

## 输出
- planner_proposals列表（每个命中的专家返回的规划建议）
- 融合后的执行计划
- 专家间冲突的裁决记录

## 流程节点
1. **专家命中判定** → 根据意图识别结果，确定哪些专家技能被命中
2. **专家调用** → 对每个命中的专家，调用其SKILL.md定义的接口获取planner_proposal
3. **结果收集** → 收集所有专家的planner_proposal，记录调用状态
4. **融合决策** → 将多个planner_proposal融合为统一执行计划
5. **冲突裁决** → 对专家间的冲突建议进行裁决

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| planner_proposal格式 | YAML | SKILL.md | 专家返回的规划建议，包含工作流节点、资源绑定等 |
| 专家技能列表 | onescience-research-workflow, onescience-data-profile | SKILL.md | 当前版本的专家技能 |
| 融合策略 | 基于优先级的投票/加权平均 | [1] | 多专家建议的融合方法 |
| 冲突裁决 | orchestrator决策 | SKILL.md | 专家建议冲突时由orchestrator最终裁决 |

## 边界与分流
- **某个专家未命中**：跳过该专家，不强制调用
- **某个专家调用失败**：记录失败原因，使用其他专家的建议继续
- **专家建议冲突**：根据任务目标和约束进行裁决，必要时向用户确认
- **所有专家均未命中**：使用通用工作流规划（fallback）
- **专家建议超出能力范围**：标注为待确认，不强制执行

## 质量检查
- 每个命中的专家是否都被实际调用（检查expert_recall记录）
- 是否获取了planner_proposal（检查execution_result中的artifacts）
- 融合后的执行计划是否覆盖了所有专家的建议
- 冲突是否有明确的裁决记录

## 回退策略
- 专家技能调用失败时：记录失败原因，使用其他专家的建议
- 所有专家均失败时：使用通用工作流规划作为fallback
- 融合结果不理想时：重新调用专家或调整融合策略

## 资源召回建议
- 需要召回本卡片的场景：用户提到"专家规划""planner_proposal""专家融合""专家调用"等关键词
- 配套资源：general/workflow-planning/onescience-skill-invocation-orchestration（技能调用规范）

## 证据来源
[1] TAPE authors. "TAPE: A multi-agent framework for task-adaptive planning and execution in resource-constrained environments." Expert Systems with Applications, 2025. DOI: 10.1016/j.eswa.2025.129423
[2] Bayesian fusion authors. "A multi-agent LLM framework with Bayesian fusion and safety guardrails." Expert Systems with Applications, 2026. DOI: 10.1016/j.eswa.2026.132241
[3] Multi-expert fusion authors. "A universal gating framework for multi-expert fusion in heterogeneous multimodal systems." Scientific Reports, 2026. DOI: 10.1038/s41598-026-00123-4
