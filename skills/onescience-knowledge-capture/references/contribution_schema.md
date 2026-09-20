# Knowledge Contribution Schema

本文件定义 `onescience-knowledge-capture` 生成的 `contribution.json` 和 `contribution.md` 的最小结构。贡献是人工审查输入，不代表已经合并到生产 skill。

## `contribution.json`

```json
{
	"schema_version": "onescience-knowledge-contribution-v1",
	"contribution_id": "2026-09-07_example",
	"title": "",
	"domain": "bio | cfd | climate | matchem | general | unknown",
	"kind": "knowledge | integration | both",
	"status": "proposed",
	"created_at": "",
	"source": {
		"source_type": "inline | local_file | artifact | mixed",
		"session_id": "",
		"redacted": true,
		"raw_transcript_included": false,
		"summary": ""
	},
	"task": {
		"goal": "",
		"context": [],
		"inputs": [],
		"expected_outputs": [],
		"constraints": [],
		"success_criteria": []
	},

	"execution_trace": [
		{
			"step_id": "",
			"name": "",
			"objective": "",
			"expected_inputs": [],
			"actual_inputs": [],
			"expected_action": [],
			"actual_action": [],
			"resources": [],
			"skills": [],
			"tools": [],
			"knowledge": [],
			"expected_outputs": [],
			"actual_outputs": [],
			"observation": "",
			"decision": "",
			"decision_reason": "",
			"status": "success | partial | failed"
		}
	],
	"verification": [
		{
			"target": "",
			"type": "artifact |workflow |reasoning |scientific |result ",
			"method": "",
			"expected_result": "",
			"actual_result": "",
			"status": "pass |partial |fail |not_performed "
		}
	],

	"failures": [
		{
			"failure_id": "",
			"related_step": "",
			"symptom": "",
			"root_cause": "",
			"impact": ""
		}
	],

	"recovery_trace": [
		{
			"trigger_failure": "",
			"recovery_strategy": "",
			"recovery_action": "",
			"recovery_result": "",
			"status": "success |failed "
		}
	],

	"capability_attribution": {
		"knowledge_gaps": [],
		"reasoning_gaps": [],
		"planning_gaps": [],
		"execution_gaps": [],
		"verification_gaps": [],
		"resource_gaps": [],
		"contract_gaps": []
	},

	"knowledge_discovery": {
		"facts": [],
		"heuristics": [],
		"constraints": [],
		"fallbacks": [],
		"anti_patterns": [],
		"new_knowledge": [],
		"open_questions": []
	},
	"integration": {
		"target_layer": "primitive | expert | executor | orchestrator_review | retain_as_case",
		"target_skill": "",
		"target_directory": "",
		"proposed_changes": [],
		"contract_impact": [],
		"validation_plan": []
	},
	"promotion": {
		"recommendation": "promote_primitive | propose_expert | propose_executor | orchestrator_review | retain_as_case | human_review",
		"confidence": "high | medium | low",
		"rationale": "",
		"required_review": []
	},
	"privacy": {
		"redactions": [],
		"sensitive_content_detected": false,
		"publication_scope": "repository_private | repository_public | issue_review_only | unknown"
	},
	"submission": {
		"mode": "none | payload_only | submit",
		"status": "not_requested | generated | submitted | failed",
		"repository": "onescience-ai/oneskills-dev",
		"issue_number": null,
		"issue_url": null
	}
}
```

## 必需 Markdown 章节

```text
# <title>

## Contribution Metadata
## Task Summary
## Interaction Timeline
## Decisions And Evidence
## Resources And Skills
## Artifacts And Verification
## Failures And Recovery
## Reusable Knowledge
## Integration Proposal
## Promotion Decision
## Privacy And Limitations
```

## 证据规则

- 事实、决策和结论应能回溯到 `execution_trace` 中的步骤、`verification` 中的目标或已记录产物。
- 候选规则必须说明证据强度和复用条件；无法确认的内容只能进入 `open_questions`、`required_review` 或使用 `UNVERIFIED` 标记。
- 失败与恢复分别记录在 `failures` 和 `recovery_trace`，不要把未发生的恢复过程写成事实。
- 绝对本地路径只允许出现在内部执行结果，不得写入公开 Markdown 或 Issue body。
