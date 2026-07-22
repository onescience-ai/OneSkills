# Expert Planner Contract

专家规划技能是某一类任务或某个意图方面的专业规划器。它不直接执行代码、运行任务或安装环境，而是向 orchestrator 返回局部规划 proposal。

orchestrator 可以同时召回多个专家规划技能，收集它们的 proposal，再融合成一个全局计划。专家不是主控，主控始终是 orchestrator。

## Intent Profile

orchestrator 在召回专家前，先基于用户请求和资源摘要形成意图画像：

```json
{
  "user_goal": "string",
  "domain_hints": ["earth", "biology", "cfd", "materials", "general"],
  "intent_aspects": [
    {
      "aspect_id": "paper_reproduction",
      "goal": "extract method and generate reproduction spec",
      "evidence": ["paper resource summary", "user says reproduce"]
    }
  ],
  "artifact_targets": ["spec", "code", "config", "runtime_result", "evaluation_report"],
  "operation_types": ["create", "adapt", "run", "diagnose", "evaluate"],
  "resource_candidates": []
}
```

`intent_aspects` 是专家召回的基本单位。一个复杂任务可以有多个方面，例如 paper reproduction、model codegen、runtime validation。

## Planner 召回输入

```json
{
  "task_state": {},
  "intent_profile": {},
  "assigned_aspect": {
    "aspect_id": "string",
    "goal": "string",
    "evidence": []
  },
  "available_resource_summaries": [],
  "available_execution_skills": [
    {
      "skill_name": "string",
      "source_of_truth": "<executor SKILL.md>",
      "accepted_inputs": [],
      "produced_outputs": [],
      "owns_responsibilities": [],
      "explicit_non_responsibilities": [],
      "downstream_handoffs": [],
      "specialized_atomic_actions_covered": [],
      "gating_conditions_or_prerequisites": [],
      "evidence_sections_or_lines": []
    }
  ],
  "latest_observation": {}
}
```

`available_execution_skills` 不是技能名称列表；它必须来自 orchestrator 对当前所有 `type=executor` 技能完整读取各自权威 `SKILL.md` 后形成的证据化能力台账。frontmatter `description`、技能名称或其他摘要只能帮助列举候选 executor，不能替代该台账作为职责边界依据。

## Planner Proposal 输出

```json
{
  "planner_id": "string",
  "covered_aspect": "string",
  "confidence": "high|medium|low",
  "plan_fragment": [
    {
      "stage_id": "string",
      "goal": "string",
      "depends_on": [],
      "execution_skill": "string|null",
      "required_resources": [
        {
          "resource_type": "summary|knowledge|implementation_asset|contract|runtime|evaluation",
          "query": "string",
          "required": true
        }
      ],
      "expected_artifacts": [],
      "completion_criteria": [],
      "fallback": "string"
    }
  ],
  "resource_preferences": [],
  "risks": [],
  "conflicts": [],
  "blocked_reason": null
}
```

## 计划融合规则

orchestrator 对多个 proposal 做融合和优化：

- 保留覆盖用户目标所需的最小阶段集合。
- 按 `depends_on`、资源前置条件和 artifact 流向排序。
- 合并重复 stage。
- 在合并后、生成最终 `global_plan` 前，必须先完整查询当前所有可用的 `type=executor` 技能，并逐个完整读取其权威 `SKILL.md`，形成 executor 能力视图。
- executor 能力视图至少应覆盖：`skill_name`、`source_of_truth`、输入要求、输出产物、职责边界、明确不负责事项、下游交接对象、覆盖的专门原子动作、前置条件，以及对应证据段落。
- 若 executor 能力视图不完整、任一台账字段缺失，或只基于技能名称 / frontmatter `description` / 简写摘要而未完成完整 `SKILL.md` 阅读，则不得继续计划融合或选择 `next_step`。
- 在合并后、生成最终 `global_plan` 前，必须按可调用 `type=executor` 技能做能力覆盖拆分。
- 如果一个阶段可由宽泛 executor 一次性完成，但阶段内部包含已有专门 executor 可执行的子动作，必须拆成多个阶段，并用 `depends_on` 串接 artifact 流。
- 原子动作拆分时，必须同时检查 executor 在完整 `SKILL.md` 中声明的负责事项与明确不负责事项，不能根据技能名称或 handoff 简写职责直接推断。
- 宽泛 executor 只负责生成或修改代码、入口、配置、脚本等前置产物；训练、推理、评估、运行、安装、数据构建等已有专门 executor 覆盖的动作必须交给对应专门 executor。
- trainer/coder 规范性示例：若 trainer 的完整 `SKILL.md` 已明确训练策略、完整训练脚本内容生成与训练执行组织归 trainer，而 coder 只负责把已定义内容写入仓库或项目结构，则训练核心决策和执行组织必须交给 trainer，coder 只承担落盘子动作。
- 示例：`生成模型并完成训练和推理` 不应作为一个宽泛 executor 的单阶段；应先查询当前可用的 `type=executor` 技能，再按职责边界拆成“前置产物生成阶段 + 训练阶段 + 推理阶段”等多个阶段，并用 artifact 依赖串接。
- 如果两个 proposal 对同一资源契约冲突，先标记冲突，再选择更高置信度或要求进一步确认。
- 如果一个 proposal 的阶段只在失败路径需要，放入 fallback，不进入主路径。
- 每轮只选一个当前 `next_step` 执行，避免把完整链路一次性压给执行技能；在选择前必须基于最新 `Task State`、`observations` 和 `artifacts` 重新评估，而不是沿用旧计划文本。

## 无专家召回时的 direct step

orchestrator 不应在召回前先判断“是否需要专家”。标准流程是：

```text
intent_profile -> 按 intent_aspects 召回专家 -> 收集 proposal
```

如果没有召回到任何专家，才进入 `direct_step`。这表示当前任务是通用任务、单步任务，或当前专家体系尚未覆盖。

进入 `direct_step` 后，orchestrator 应直接生成当前步骤：

```json
{
  "planning_mode": "direct_step",
  "planner_candidates": [],
  "next_step": {
    "goal": "string",
    "execution_skill": "string",
    "required_resources": [],
    "completion_criteria": []
  }
}
```

direct step 仍必须使用 `intent_profile` 和资源摘要，不允许丢失 Task State。

## Planner 禁止事项

- 不要直接写代码、执行命令、提交任务或安装依赖。
- 不要绕过 `Task State` 自行延续上下文。
- 不要假设自己是唯一主规划者；只规划 `assigned_aspect`。
- 不要把未来所有步骤都写成必须立即执行的技能链。
- 不要在没有资源契约时猜测关键 shape、路径、参数或硬件事实。
