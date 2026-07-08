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
  "available_execution_skills": [],
  "latest_observation": {}
}
```

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
- 如果两个 proposal 对同一资源契约冲突，先标记冲突，再选择更高置信度或要求进一步确认。
- 如果一个 proposal 的阶段只在失败路径需要，放入 fallback，不进入主路径。
- 每轮只选一个当前 `next_step` 执行，避免把完整链路一次性压给执行技能。

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
