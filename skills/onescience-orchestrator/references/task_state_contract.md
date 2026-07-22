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
      "status": "candidate|queried|rejected"
    }
  ],
  "planner_proposals": [
    {
      "planner_id": "string",
      "covered_aspect": "string",
      "confidence": "high|medium|low",
      "status": "received|merged|rejected|conflict"
    }
  ],
  "global_plan": [
    {
      "stage_id": "string",
      "goal": "string",
      "source_proposals": [],
      "depends_on": [],
      "execution_skill": "string|null",
      "status": "pending|active|done|failed|skipped"
    }
  ],
  "active_step": {
    "step_id": "string",
    "goal": "string",
    "execution_skill": "string",
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
- 召回专家前，必须先记录由用户请求和资源摘要形成的 `intent_profile`。
- 如果按 `intent_profile` 召回不到专家，设置 `planning_mode=direct_step`，并记录 orchestrator 直接规划的原因。
- 走专家规划时，设置 `planning_mode=expert_proposal_synthesis`，记录候选专家、已收集 proposal 和融合后的 `global_plan`。
- 每次调用执行技能后，必须先进入 `observation`，再写入 `artifacts` 和 `observations`，不能直接从 execution 跳到下一次执行。
- `partial` 必须记录已完成部分、缺失项、残余风险和下一步建议，并默认回到 `observation -> planning`。
- `failed` 必须先记录失败证据，再由规划阶段决定进入 `repair` 或 `blocked`，不能直接结束。
- `repair` 只能针对最新 `observation` 生成新的修复步，不能沿用失败前的 `active_step` 或旧 handoff。
- 用户新增约束时，追加到 `constraints`，不要覆盖原始 `user_goal`。
- 只有所有 `completion_criteria` 都满足或明确不可继续时，才进入 `complete` 或 `blocked`。
- `Task State` 是选择下一步执行的唯一事实源；在更新后的 state 上必须重新选择 `next_step`，不得沿用旧计划文本或旧 handoff 直接继续执行。

## Direct Step 与专家融合

`direct_step` 用于未召回到专家的通用、单步、低歧义需求，或当前专家体系尚未覆盖的需求。它仍然必须记录资源候选和 step spec，但不需要 `planner_proposals`。

`expert_proposal_synthesis` 用于多阶段、多资源或需要领域判断的需求。该模式必须保存：

- `intent_profile`
- `planner_candidates`
- `planner_proposals`
- `global_plan`
- 当前从 `global_plan` 中选出的 `active_step`
