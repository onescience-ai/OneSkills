# Task State Contract

`Task State` 是 orchestrator 跨多轮规划和执行的唯一事实源。任何规划、执行、观察、重试和结束判断都应围绕它更新。

## 最小字段

```json
{
  "task_id": "string",
  "user_goal": "string",
  "current_phase": "intake|planning|execution|observation|repair|validation|complete|blocked",
  "planning_mode": "direct_step|expert_proposal_synthesis|null",
  "domain_hints": ["string"],
  "task_family": "string|null",
  "intent_profile": {
    "domain_hints": [],
    "intent_aspects": [],
    "artifact_targets": [],
    "operation_types": [],
    "resource_candidates": []
  },
  "planner_candidates": [
    {
      "planner_id": "string",
      "matched_aspect": "string",
      "match_reason": "string",
      "status": "candidate|queried|received|merged|rejected"
    }
  ],
  "planner_proposals": [
    {
      "planner_id": "string",
      "covered_aspect": "string",
      "confidence": "high|medium|low",
      "status": "received|merged|rejected|conflict",
      "source_proposal": "string"
    }
  ],
  "executor_inventory": {
    "all_executor_skills": ["string"],
    "read_executor_skills": ["string"],
    "missing_executor_skills": ["string"],
    "executor_inventory_complete": true,
    "user_visible_summary": "string"
  },
  "global_plan": [
    {
      "stage_id": "string",
      "goal": "string",
      "source_proposals": ["string"],
      "depends_on": [],
      "execution_skill": "string|null",
      "detail_bundle_id": "string|null",
      "status": "pending|active|done|failed|skipped"
    }
  ],
  "plan_detail_store": [
    {
      "detail_bundle_id": "string",
      "stage_id": "string",
      "execution_skill": "string|null",
      "detail_bundle": {},
      "detail_provenance": ["string"],
      "required_resources": [],
      "expected_artifacts": [],
      "completion_criteria": [],
      "fallback_detail": [],
      "risk_notes": []
    }
  ],
  "active_step": {
    "step_id": "string",
    "goal": "string",
    "execution_skill": "string",
    "detail_bundle_id": "string|null",
    "detail_bundle": {},
    "status": "pending|running|done|failed|blocked"
  },
  "resource_bindings": [
    {
      "resource_id": "string",
      "resource_type": "summary|knowledge|implementation_asset|contract|runtime|evaluation",
      "purpose": "string",
      "selected_by": "orchestrator|planner|executor",
      "status": "candidate|bound|rejected"
    }
  ],
  "artifacts": [
    {
      "artifact_id": "string",
      "path": "string|null",
      "kind": "spec|code|config|log|report|dataset|model|other",
      "produced_by": "string",
      "step_id": "string"
    }
  ],
  "observations": [
    {
      "step_id": "string",
      "source_skill": "string",
      "status": "success|failed|blocked|partial",
      "summary": "string",
      "missing": ["string"],
      "next_recommendation": "string|null"
    }
  ],
  "constraints": ["string"],
  "open_questions": ["string"],
  "completion_criteria": ["string"]
}
```

## 状态迁移

```text
intake -> planning
planning -> execution
execution -> observation
observation -> planning
observation -> repair
repair -> execution
observation -> validation
validation -> complete
any -> blocked
```

## 更新规则

- 每次调用专家规划技能前，先提供当前 `Task State` 摘要。
- 资源召回返回后回到 orchestrator 主循环，继续生成 `intent_profile`；`resource_retrieval_result` 是中间观察，不是终点。
- 召回专家前，必须先记录由用户请求和资源摘要形成的 `intent_profile`。
- 专家召回步骤本身要留下状态痕迹；即使没有命中任何专家，也记录“已召回、未命中”的结果。
- `intent_aspects` 中的 `aspect_key` 只是轻量追踪键；没有稳定键时可以只保留 `goal` 与 `evidence`。
- 如果按 `intent_profile` 召回不到专家，设置 `planning_mode=direct_step`，并记录 orchestrator 直接规划的原因。
- 走专家规划时，设置 `planning_mode=expert_proposal_synthesis`，记录候选专家、已收集 proposal、融合后的 `global_plan`，以及与各 stage 对应的 `plan_detail_store`。
- 在任何计划融合、`global_plan` 生成或 `next_step` 选择之前，必须先写入 `executor_inventory`：记录当前轮次发现的全部 executor、已完整读取并入账的 executor、差集 `missing_executor_skills`，并计算 `executor_inventory_complete`。
- `executor_inventory_complete=true` 的前提是 `set(all_executor_skills) == set(read_executor_skills)`，且每个已读 executor 都已写入证据化能力台账；若不满足，保持 `executor_inventory_complete=false`，不得继续规划推进。
- `user_visible_summary` 只保留面向用户的简短汇总，例如 `executor inventory: 13/13 complete`；完整列表默认只保存在 Task State 内部，只有 inventory 不完整或进入 blocked 时才向用户展开 `missing_executor_skills`。
- 只要 `intent_aspects` 命中多个专家，就默认按多专家 proposal synthesis 处理；不得在尚未收齐所有命中专家回执前提前定稿。
- proposal 融合后，不仅要写入 `global_plan` 骨架，还必须为每个 executor_step 写入按目标 executor 裁剪后的 detail bundle；不得只保留阶段 `goal`。
- 选择 `next_step` 时，必须同时选出对应的 `detail_bundle_id` 和 detail bundle 内容，写入 `active_step`。
- 若当前 `active_step.execution_skill` 非空，则该步骤视为 executor-owned；在收到对应 executor 的 `execution_result` 之前，orchestrator 不以自身 direct tool 结果替代该步骤，也不绕过该 owner 推进后续步骤。
- 每次调用执行技能后，先进入 `observation`，再写入 `artifacts` 和 `observations`；随后可在同一 orchestrator 循环中选择下一步继续执行。
- `partial` 记录已完成部分、缺失项、残余风险和下一步建议，并默认回到 `observation -> planning`。
- `failed` 记录失败证据，再由规划阶段决定进入 `repair` 或 `blocked` 分支。
- `repair` 针对最新 `observation` 生成新的修复步；若沿用原阶段骨架，也要重新核对对应 detail bundle 是否充分。
- 用户新增约束时，追加到 `constraints`，不要覆盖原始 `user_goal`。
- 当所有 `completion_criteria` 都满足时进入 `complete`；若暂时不可继续，则保持 `blocked` 直到条件变化或用户改写目标。
- `Task State` 是选择下一步执行的唯一事实源；在更新后的 state 上必须重新选择 `next_step`，不得沿用旧计划文本或旧 handoff 直接继续执行。

## Direct Step 与专家融合

`direct_step` 用于未召回到专家的通用、单步、低歧义需求，或当前专家体系尚未覆盖的需求。它仍然必须记录资源候选和 step spec，但不需要 `planner_proposals`。

`expert_proposal_synthesis` 用于多阶段、多资源或需要领域判断的需求。该模式必须保存：

- `intent_profile`
- `planner_candidates`
- `planner_proposals`
- `global_plan`
- `plan_detail_store`
- 当前从 `global_plan` 中选出的 `active_step`（含 detail bundle 引用或当前细节内容）
