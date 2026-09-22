# OneScience Skill Invocation Orchestration

## 适用范围
面向需要调用多个OneScience executor技能（如onescience-data-standardizer、onescience-trainer、onescience-coder、onescience-data-analyzer等）的复合科研任务，提供规范化的技能调用流程、输入输出契约验证、调用时序编排和异常恢复方法论。适用于任何涉及技能调度的OneScience工作流；不适用于单一技能的内部执行逻辑。

## 输入
- 任务描述与目标
- 步骤分解与技能映射（哪些步骤调用哪个技能）
- 每个技能的step_handoff参数
- 上下文产物路径（前序技能的输出）

## 输出
- 各技能的实际执行结果（execution_result）
- 技能调用日志（调用时间、状态、输出摘要）
- 异常处理记录
- 最终任务状态汇总

## 流程节点
1. **步骤分解** → 将任务分解为可由单个executor技能执行的原子步骤
2. **技能匹配** → 为每个步骤选择合适的executor技能
3. **契约验证** → 确认每个技能的输入参数符合其SKILL.md定义的输入契约
4. **调用执行** → 按依赖顺序调用技能，传递step_handoff
5. **结果归集** → 收集各技能的execution_result，检查状态
6. **异常恢复** → 对失败/阻塞的技能执行重试或降级策略

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| step_handoff格式 | YAML | SKILL.md | 包含step_id, execution_skill, inputs, expected_outputs |
| execution_result格式 | YAML | SKILL.md | 包含skill, status, artifacts, observation |
| 状态枚举 | success/partial/failed | SKILL.md | 技能执行结果状态码 |
| 最大重试次数 | 2-3次 | [1] | 异常恢复的最大重试次数 |
| 超时时间 | 300-600秒 | [1] | 单个技能调用的超时限制 |

## 边界与分流
- **技能调用失败**：检查输入契约是否满足，修正后重试
- **技能输出不完整**：检查execution_result中的artifacts字段，必要时补充执行
- **技能间依赖冲突**：调整调用顺序或并行执行独立步骤
- **环境未就绪**：先调用onescience-installer进行环境准备
- **运行站点未配置**：先调用onescience-runsite补齐配置
- **模拟执行检测**：必须确认skill_invocations记录的是实际技能调用，而非Python脚本模拟

## 质量检查
- 每个技能调用是否记录在execution-manifest.json的skill_invocations中
- execution_result的status是否为success或partial（非failed）
- 技能输出是否符合其SKILL.md定义的输出契约
- 无模拟执行：确认是通过skill工具实际调用，而非手动Python脚本

## 回退策略
- 技能调用失败时：检查环境配置、数据依赖、参数格式
- 多次重试仍失败：记录失败原因，标记为partial状态，继续执行后续步骤
- 关键技能阻塞：降级为简化执行方案，但必须明确标注降级

## 资源召回建议
- 需要召回本卡片的场景：用户提到"技能调用""executor""skill invocation""工作流编排"等关键词
- 配套资源：general/workflow-planning/onescience-expert-planning-fusion（专家规划融合）

## 证据来源
[1] DIVE-to-design authors. "DIVE-to-design: how a multi-agent workflow converts figure-centric literature into materials design data." AI Agent, 2026. DOI: 10.20517/aiagent.2026.07
[2] Catalyst design workflow authors. "A closed-loop universal catalyst design workflow ready for AI agents." AI Agent, 2026. DOI: 10.20517/aiagent.2026.12
[3] Multi-agent orchestration authors. "A Multi-Agent Workflow Orchestration System for Complex Long-Cycle Tasks." International Journal of AI and Emerging Markets, 2026.
