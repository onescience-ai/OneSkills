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
    "user_goal": "",
    "context": [],
    "constraints": [],
    "requested_outputs": []
  },
  "evidence": [
    {
      "id": "E1",
      "kind": "user_goal | context | action | observation | decision | artifact | verification | limitation",
      "summary": "",
      "source_ref": "message:3 | artifact:foo | handoff:inputs",
      "confidence": "high | medium | low"
    }
  ],
  "timeline": [
    {
      "step": 1,
      "user_need": "",
      "action": "",
      "observation": "",
      "evidence_refs": ["E1"]
    }
  ],
  "resources_and_skills": [],
  "artifacts": [],
  "failures_and_recovery": [],
  "reusable_knowledge": {
    "facts": [],
    "heuristics": [],
    "constraints": [],
    "fallbacks": [],
    "anti_patterns": [],
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

- 事实必须有 `evidence_refs`。
- 候选规则必须说明证据强度和复用条件。
- 未验证内容只能进入 `open_questions`、`required_review` 或 `UNVERIFIED` 标记。
- 绝对本地路径只允许出现在内部执行结果，不得写入公开 Markdown 或 Issue body。
