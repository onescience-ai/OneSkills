# Task State Contract

`Task State` 是 orchestrator 跨多轮规划和执行的唯一事实源。任何规划、执行、观察、重试和结束判断都应围绕它更新。

## 最小字段

```json
{
  "task_id": "string",
  "user_goal": "string",
  "current_phase": "intake|planning|execution|observation|repair|tier_check|tier_escalate|step_timeout|validation|complete|blocked|partial",
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
  "global_plan_version": 1,
  "global_plan_revision_history": [
    {
      "version": 1,
      "revised_at": "ISO8601",
      "revision_reason": "initial_plan|replan_after_failure|observation_driven|expert_replan|tier_escalate",
      "previous_version": null,
      "changed_stage_ids": [],
      "summary": "string"
    }
  ],
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
    "attempt": 1,
    "goal": "string",
    "execution_skill": "string",
    "detail_bundle_id": "string|null",
    "detail_bundle": {},
    "status": "pending|running|done|failed|blocked",
    "step_wallclock_budget_seconds": 3600,
    "step_started_at": "ISO8601|null"
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
      "attempt": 1,
      "source_skill": "string",
      "status": "success|failed|blocked|partial|step_timeout",
      "failure_category": "transient|environment|dependency|data|code|scientific|platform|unknown|null",
      "summary": "string",
      "missing": ["string"],
      "next_recommendation": "string|null"
    }
  ],
  "events": [
    {
      "event_id": "string",
      "timestamp": "ISO8601",
      "step_id": "string",
      "attempt": 1,
      "event_type": "step_started|step_completed|step_failed|step_timed_out|repair_attempted|retry_started|diagnosis_completed|tier_escalated|tier_fallback|plan_revised|decision_auto_made|observation_recorded|blocked",
      "source_skill": "string",
      "description": "string",
      "evidence": {}
    }
  ],
  "constraints": ["string"],
  "open_questions": ["string"],
  "completion_criteria": ["string"],
  "tiered_completion_contract": {
    "active_tier": "tier_0_smoke",
    "tiers": [
      {
        "tier_id": "tier_0_smoke",
        "description": "string",
        "checks": [
          {"name": "string", "status": "pending|pass|fail|skipped", "result": "string|null"}
        ],
        "status": "pending|running|pass|fail"
      }
    ],
    "resolution": "string",
    "deliverable_tier": "string|null"
  },
  "decision_policy": {
    "level_3_fallback_timeout_seconds": 300,
    "active_decisions": [
      {
        "decision_id": "string",
        "level": "level_1_reversible|level_2_scope_affecting|level_3_goal_altering",
        "description": "string",
        "status": "pending|resolved|timed_out",
        "resolved_by": "string",
        "fallback_used": false
      }
    ]
  },
  "exploration_budget": {
    "data_acquisition": {"max_attempts": 3, "used": 0, "max_wallclock_seconds": 600, "wallclock_seconds_used": 0},
    "speed_measurement": {"max_attempts": 2, "used": 0},
    "structure_probing": {"max_attempts": 2, "used": 0, "max_wallclock_seconds": 120, "wallclock_seconds_used": 0}
  },
  "step_wallclock_budget": {
    "enabled": false,
    "default_budget_seconds": 3600,
    "budget_multiplier_on_retry": 2.0,
    "on_timeout": "block_and_record"
  }
}
```

## 状态迁移

```text
intake -> planning
planning -> execution
execution -> observation
execution -> step_timeout -> blocked   (若超过 step_wallclock_budget_seconds 且 autonomous_mode=true)
observation -> planning
observation -> repair
repair -> execution
observation -> tier_check
tier_check -> execution       (若当前 tier 未完成，继续执行)
tier_check -> tier_escalate   (若当前 tier 通过且需要进入更高 tier)
tier_check -> complete        (若 deliverable tier 已通过且不需 escalation)
tier_check -> partial         (若 deliverable tier 部分通过且有回退产物)
observation -> validation
validation -> complete
any -> blocked
```

状态说明：
- `tier_check`：每步 observation 完成后，orchestrator 检查 `tiered_completion_contract` 中当前 active_tier 的各项 check 状态，更新 tier status，并判定是否需要 escalation 或可宣告完成。
- `tier_escalate`：当前 tier 通过 → 若 `tier_config` 级联规则要求进入下一 tier（如 Tier 1 通过 + user_goal 含"全量"），自动激活下一 tier，写入 `active_tier`，进入 planning → execution。
- `partial`：任务未完全达成但仍可交付——通常发生在 Tier 2 失败/超时后回退 Tier 1 产物的场景。此时 `deliverable_tier` 指向实际交付的 tier。

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
- 当所有 `completion_criteria` 都满足时进入 `complete`；若已启用 `tiered_completion_contract`，则完成判定由 tier contract 的布尔解析结果驱动（见下方"分层完成契约判定规则"），`completion_criteria` 仅作补充参考。若暂时不可继续，则保持 `blocked` 直到条件变化或用户改写目标。
- `Task State` 是选择下一步执行的唯一事实源；在更新后的 state 上必须重新选择 `next_step`，不得沿用旧计划文本或旧 handoff 直接继续执行。
- 每次 `global_plan` 发生结构性修改（非简单状态更新），必须递增 `global_plan_version`，并追加一条 `global_plan_revision_history` 记录。
- 每次调用 executor 前、收到结果后、进入修复/重试/超时/阻断/tier 变化时，必须写入一条 `event` 记录到 `events` 数组。

## 分层完成契约判定规则

当 `tiered_completion_contract` 被初始化后，任务完成判定按以下规则：

1. orchestrator 在每步 observation 完成后，遍历当前 `active_tier` 的所有 checks，根据执行结果更新各 check 的 `status`（pending → pass / fail / skipped）。
2. 当当前 tier 的所有 checks 已无 pending 状态：
   - 全部 pass → 当前 tier status 标记为 `pass`，然后判定 escalation：
     - 若当前 tier 是 `deliverable_tier`（默认 Tier 1），且 user_goal 不含 escalation trigger（如"全量"/"完整复现"） → `status: complete`
     - 若存在下一 tier 且 user_goal 触发了 escalation → `active_tier` 切换到下一 tier，进入 `tier_escalate` 状态
   - 有 fail → 若有 `fallback_tier` 可回退 → `deliverable_tier` 指向 fallback tier，`status: partial`
   - 有 fail → 无 fallback → 标记 blocked 或 failed
3. `completion_criteria` 字段不变，但当 `tiered_completion_contract` 存在时，最终 `status` 由 tier contract 决定，不得由 orchestrator 事后覆盖。

## 决策分级策略

`decision_policy` 定义了 autonomous_mode 下的决策处理方式：

| 级别 | 判定条件 | 策略 | 示例 |
|---|---|---|---|
| level_1_reversible | 决策可回退、不影响最终目标 | auto_choose_first | 先训练哪个模型 |
| level_2_scope_affecting | 影响范围但不改变核心目标 | auto_with_log | 数据子集大小调整 |
| level_3_goal_altering | 涉及核心目标变化或外部资源硬阻塞 | block_and_escalate | 数据替代方案选择 |

当 level_3 决策被阻塞（blocked）时，orchestrator 写入 `.onescience/task_state.json`，包含决策选项和 fallback 配置。若 wallclock 超过 `level_3_fallback_timeout_seconds` 无人响应，自动使用 `fallback` 选项解除阻塞。

## 探索预算

`exploration_budget` 限制了 autonomous_mode 下数据探索类步骤的最大尝试次数和耗时：

```yaml
exploration_budget:
  data_acquisition:
    max_attempts: 3              # 不同方案的数据获取尝试上限
    max_wallclock_seconds: 600   # 最大探索墙钟时间（秒）
    on_exhausted: "report_blocker_and_proceed_with_fallback"
  speed_measurement:
    max_attempts: 2              # 测速最多 2 次
    on_exhausted: "use_last_measured_value"
  structure_probing:
    max_attempts: 2              # 文件结构探测上限
    max_wallclock_seconds: 120
    on_exhausted: "skip_and_mark_unavailable"
```

orchestrator 每次执行探索动作前，检查对应类别的预算余额（attempts used < max_attempts 且 wallclock_seconds_used < max_wallclock_seconds）。预算耗尽的类别不得再发起探索，直接按 `on_exhausted` 策略处理。

## Direct Step 与专家融合

`direct_step` 用于未召回到专家的通用、单步、低歧义需求，或当前专家体系尚未覆盖的需求。它仍然必须记录资源候选和 step spec，但不需要 `planner_proposals`。

`expert_proposal_synthesis` 用于多阶段、多资源或需要领域判断的需求。该模式必须保存：

- `intent_profile`
- `planner_candidates`
- `planner_proposals`
- `global_plan`
- `plan_detail_store`
- 当前从 `global_plan` 中选出的 `active_step`（含 detail bundle 引用或当前细节内容）

## Global Plan 版本控制

`global_plan_version` 和 `global_plan_revision_history` 用于追踪计划的演进过程：

- 初始生成 Global Plan 时，`global_plan_version` = 1，写入首条 revision_history（`revision_reason=initial_plan`）。
- 每当中途发生计划修改（observation 驱动的重规划、专家 re-plan、失败后调整、tier escalation 等），递增 `global_plan_version`，并追加一条 `global_plan_revision_history` 记录。
- `revision_reason` 枚举：
  - `initial_plan`：首次生成
  - `observation_driven`：observation 后发现需要调整后续步骤
  - `replan_after_failure`：执行失败后的重规划
  - `expert_replan`：专家技能主动建议的调整
  - `tier_escalate`：tier 升级触发的计划扩展
- 每次 plan revision 时，`changed_stage_ids` 记录本轮被修改的 stage_id 列表。

## Failure Taxonomy（失败分类与分策略处理）

当 executor 返回 `status: failed` 时，`observation.failure_category` 用于指导 orchestrator 选择后续策略：

| failure_category | 含义 | 推荐策略 | 示例 |
|---|---|---|---|
| `transient` | 临时性错误（网络超时、资源短暂不可用等），重试大概率恢复 | `retry_with_backoff`：指数退避重试，最多 2 次 | 网络波动导致下载失败 |
| `environment` | 运行环境问题（缺依赖、conda 不可用、CUDA 版本不匹配） | `delegate_to_installer`：委托 onescience-installer 修复环境 | torch 版本不兼容 |
| `dependency` | 外部依赖缺失或不可达（数据源不可用、API 返回错误） | `block_and_escalate`：暂停并通知用户 | 数据源 URL 失效 |
| `data` | 数据问题（格式错误、字段缺失、数据损坏） | `retry_re_fetch`：重新获取数据后重试 1 次，失败则 block | 数据集校验和不匹配 |
| `code` | 代码逻辑错误（实现偏差、接口不匹配、语法错误） | `delegate_to_coder`：委托 onescience-coder 修复后重试，最多 2 次 | 冒烟测试 forward_pass 失败 |
| `scientific` | 科学性问题（论文方法不可复现、模型不收敛、核心指标无法达到） | `block_and_escalate`：暂停，标记为需要人工研判 | 论文报告的指标在当前条件下无法复现 |
| `platform` | LLM 平台侧问题（推理超时、skill 调用挂起、上下文溢出） | `block_and_retry_once`：阻塞后重试 1 次，仍失败则 block | executor 调用无响应 |
| `unknown` | 无法自动分类的未知失败 | `block_with_diagnosis`：暂停，执行诊断后根据诊断结果再判定 | — |

当 `autonomous_mode: true` 时，上述策略自动执行，不向用户提问。超出重试上限或遇到 `scientific`/`dependency` 类别时进入 `blocked` 状态。

## 步骤级超时预算（Step Wallclock Budget）

`step_wallclock_budget` 为 autonomous_mode 下的每个 executor 步骤提供墙钟时间保护：

- `enabled`：是否启用步骤超时。autonomous_mode 下默认 `true`。
- `default_budget_seconds`：默认单步骤墙钟预算（默认 3600 秒 = 1 小时）。orchestrator 在创建 `active_step` 时根据该步骤的预估耗时写入 `active_step.step_wallclock_budget_seconds`。
- `budget_multiplier_on_retry`：重试时预算乘数（默认 2.0）。每次重试将当前预算翻倍。
- `on_timeout`：超时后的策略（固定为 `block_and_record`：标记 `status: step_timeout`，记录 event，写入 blocked）。

orchestrator 职责：
1. 在执行 executor_step 前，根据 `global_plan` 中该步骤的预估耗时设置 `active_step.step_wallclock_budget_seconds`，并记录 `step_started_at`。
2. 若 executor 调用返回时 wallclock 超过 `step_wallclock_budget_seconds * budget_multiplier_on_retry`，判定为超时，观察状态设为 `step_timeout`，写入 event（`event_type=step_timed_out`），进入 blocked。
3. 超时恢复后重新执行时，`attempt` 递增，预算按 `budget_multiplier_on_retry` 翻倍。

## Event 序列

`events` 数组为任务执行提供细粒度的结构化事件追踪，补充 `observations` 的步骤级摘要：

- 每个 event 记录 `event_id`（全局唯一）、`timestamp`、`step_id`、`attempt`、`event_type`、`source_skill`、`description`、`evidence`。
- orchestrator 在以下时机写入 event：
  - 调用 executor 前：`step_started`
  - 收到 execution_result 后：`step_completed` / `step_failed` / `blocked`
  - 检测到步骤超时：`step_timed_out`
  - 进入修复流程：`repair_attempted`
  - 开始重试：`retry_started`
  - 诊断完成后：`diagnosis_completed`
  - tier 升级/回退：`tier_escalated` / `tier_fallback`
  - 计划修改后：`plan_revised`
  - 自动决策后：`decision_auto_made`
  - observation 写入后：`observation_recorded`
- executor 可以通过 `execution_result.events` 回传其内部的子事件（如内部重试、内部修复），由 orchestrator 合并到 `Task State.events` 中。
- `events` 中的内容写入 `.onescience/task_state.json`，归档时随 state 一起保存。
