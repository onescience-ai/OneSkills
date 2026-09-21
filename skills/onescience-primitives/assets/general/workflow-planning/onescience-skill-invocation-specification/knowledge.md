# OneScience 技能调用规范

## 适用范围

面向任意科研计算任务使用 OneScience/OneSkills 体系时，orchestrator 对 executor 技能的正确调用流程，涵盖输入输出契约遵循、技能选择、错误恢复和执行验证。适用于避免"模拟执行"或"跳过技能"等常见违规行为。

## 输入

- 任务目标与约束（来自用户请求或 orchestrator 步骤规划）
- step_handoff 结构（含 step_id、execution_skill、step_goal、inputs、expected_outputs）
- 技能目录（由 skills 目录自动发现并加载）

## 输出

- execution_result（含 status、artifacts、observation）
- 技能调用日志（skill_invocations 记录实际调用，非模拟）
- 产物文件（符合 expected_outputs.required_files 规范）

## 流程节点

1. 技能发现 → 输入构建 → 实际调用 → 输出验证 → 错误恢复 → 日志记录
   - 每步含操作、参数、工具、质量门禁

## 关键参数

### 通用判据（方法层，同类体系可参考，逐条带证据编号）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 技能调用方式 | 通过 skill tool 实际加载 SKILL.md 并执行，禁止 Python 脚本模拟 | [1][3] | 模拟执行无法获得技能的真实能力支持 |
| 输入契约 | step_handoff 必须包含所有 required_inputs 字段 | [2] | 缺失字段需先向 orchestrator 补问 |
| 输出契约 | execution_result 必须包含 status、artifacts、observation | [2] | status 仅允许 success/partial/failed |
| 错误恢复 | 技能执行失败时按 SKILL.md 的回退策略处理，不得静默跳过 | [1][3] | 跳过技能导致规划质量下降 |

### 校准数值（体系专属值，引语写明"以下数值来自特定体系，供量级校准；其他体系需以自身证据重新锚定"）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 技能发现路径 | .opencode/skills/<skill-name>/SKILL.md | [2] | 相对于工作区根目录 |
| 最大重试次数 | 3（含降级策略） | [1] | 超过 3 次标记为 failed |

## 边界与分流

- 若任务明确指定跳过某技能（如 "不使用 onescience-trainer"），需在 execution_manifest 中记录 skip_reason
- 若技能执行超时，按 SKILL.md 的超时处理策略执行降级
- 若技能输入缺少必要参数，向 orchestrator 报告 BLOCKED 状态并请求补问

## 质量检查

- skill_invocations 必须记录实际技能调用，而非 "模拟执行" 或 "简化执行"
- 每个 executor 技能的输出必须符合其 SKILL.md 定义的 output_contract
- 产物文件必须实际存在于文件系统中（非内存占位）

## 回退策略

- 若技能 API 不可用，按 SKILL.md 的降级链执行
- 若技能输出不符合契约，标记为 partial 并记录不合规字段

## 资源召回建议

- 当 orchestrator 规划涉及多步骤技能调用时召回本卡
- 配套资源：专家技能调用规范卡、任务状态管理卡

## 证据来源

[1] Lakkarasu P. "Operationalizing Intelligence: A Unified Approach to MLOps and Scalable AI Workflows." International Journal of Engineering and Computer Science, 2022, DOI: 10.18535/ijecs.v11i12.4743
[2] Semmelrock H, et al. "Reproducibility in machine-learning-based research: Overview, barriers, and drivers." AI Magazine, 2025, DOI: 10.1002/aaai.70002
[3] Zhang Z, Valeo C. "Agentic SWMM: Auditable and Reproducible Stormwater Modelling Workflow with Agent Skills and Model Context Protocol." AI for Engineering, 2026, DOI: 10.3390/aieng1010005
[4] Ristov S, et al. "AFCL: An Abstract Function Choreography Language for serverless workflow specification." Future Generation Computer Systems, 2021, DOI: 10.1016/j.future.2020.08.012