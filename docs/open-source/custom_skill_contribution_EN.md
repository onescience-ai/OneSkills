# Custom Skill Contribution Guide

This guide is for `OneSkills` users and contributors, explaining how to contribute new domain experience, resource knowledge, or custom skills within the current architecture.

Core principle: **Resources are also accessed through skills. Do not directly dump new resources into `skills/onescience-primitives/assets/`. Instead, implement or extend a corresponding `type=resource` skill and place resource files under that skill's own `assets/` directory.**

## 1. Current Architecture Layers

`OneSkills` organizes new capabilities into four layers:

| Layer | Name | Responsibility | Typical Form |
| --- | --- | --- | --- |
| LAYER 1 | Core Layer | Intent understanding, resource retrieval, expert recall, plan fusion, execution scheduling, state maintenance | `onescience-orchestrator` |
| LAYER 2 | Resource Layer | Recall resource summaries and detailed content via `type=resource` skills | Various resource skills and their `assets/` |
| LAYER 3 | Expert Layer | Handle complex planning, rule judgment, fallback design; output `planner_proposal` | `type=expert` skills |
| LAYER 4 | Executor Layer | Execute stable workflows, return verifiable `execution_result` | `type=executor` skills |

When adding new task types, do not modify the domain rules of the `orchestrator`. Extend through resource skills, expert planning skills, or executor skills.

## 2. Determine the Entry Point First

For any new capability, first classify it into one of the following three entry points:

| Entry Point | Applicable Targets | Placement | Output to System |
| --- | --- | --- | --- |
| A: Resource Skill | Reusable, recallable model / data / component / application / workflow knowledge | `assets/` of the corresponding `type=resource` skill | `resource_retrieval_result` |
| B: Executor Skill | Stable entry points, fixed steps, verifiable results | New or extended `type=executor` skill | `execution_result` |
| C: Expert Skill | Complex judgment rules requiring dynamic planning and fallback per task | New or extended `type=expert` skill | `planner_proposal` |

Decision rules:

- Callable, reusable "capability or knowledge" → Entry Point A: Resource Skill.
- Has a stable CLI / API / job entry point with verifiable output → Entry Point B: Executor Skill.
- Requires planning, trade-offs, and fallback based on task characteristics → Entry Point C: Expert Skill.
- Lightweight, unverified experience not yet worth independent solidification → First deposit into the planning knowledge resource of the corresponding resource skill.

## 3. How to Add Resources

The landing point for resource contributions is "the corresponding resource type skill," not a centralized public assets directory.

### 3.1 Resource Skill Structure

When adding a new resource type, create or extend a `type=resource` skill, for example:

```text
skills/<resource-skill-name>/
  SKILL.md
  assets/
    <domain>/
      <category>/
        <resource_name>/
          metadata.json
          spec.md
          usage.md
          workflow_planning.md
  references/
    <retrieval_rules>.md
```

Notes:

- `SKILL.md` defines the resource recall scope, input/output contracts, filtering rules, and content organization.
- `assets/` stores resource files privately managed by this resource skill.
- `references/` stores this resource skill's own retrieval rules, domain routing rules, or schema documentation.
- Callers can only obtain resource content through `resource_retrieval_request -> resource_retrieval_result`; they must not directly read any resource skill's `assets/`.

Do NOT add new resources directly to:

```text
skills/onescience-primitives/assets/
```

### 3.2 Resource Skill Frontmatter

```yaml
---
name: your-resource-skill
description: Describe what type of resources this skill recalls, what domains it covers, and when to use it. Must state that it returns resource_retrieval_result and does not do planning or execute tasks.
type: resource
---
```

### 3.3 Recommended Resource Files

| File | Purpose | Serves |
| --- | --- | --- |
| `metadata.json` | Basic identification info: `name`, `type`, `domain`, `description`, `tags`, `version` | Resource recall, quick matching |
| `spec.md` | Specification knowledge: architecture, input/output, dependencies, source anchors, implementation risks | coder / executor |
| `usage.md` | Usage knowledge: startup methods, interfaces, resource requirements, limitations, common failures | executor |
| `workflow_planning.md` | Planning decision knowledge: when to use, procedure, constraints, fallback | expert / orchestrator |

Different resource types may adjust fields, but `description` in `metadata.json` must be sufficient to support recall.

### 3.4 Resource Skill I/O Contracts

All `type=resource` skills must accept unified input:

```yaml
resource_retrieval_request:
  user_request: <user requirement description>
  task_state_summary: <task state summary, optional>
  content_request: <content requirements, optional>
  filters:
    domain: <domain filter, optional>
    keyword: <keyword filter, optional>
```

Must return unified output:

```yaml
resource_retrieval_result:
  status: success | partial | failed
  query_summary: <requirement summary>
  detected_domain: <domain>
  task_intent: <task intent>
  matched_resources:
    - type: <specific resource type>
      path: <resource identifier or source path>
      name: <resource name>
      why_matched: <match reason>
      limitations: <usage limitations>
      content: <summary, text, or structured content organized per content_request>
```

`matched_resources[].content` is the only resource content carrier that callers are allowed to consume. `path` is only used for tracking and binding, not for authorizing callers to directly read underlying files.

## 4. When to Add Non-Resource Skills

Only add a `type=expert` or `type=executor` skill when:

- Existing resource skills or existing executor / expert skills cannot handle it.
- The capability will be repeatedly reused.
- It has clear inputs, outputs, and boundaries.
- It is not a domain-specific copy of general executor skills like `coder/runtime/installer`.
- It can be explicitly connected to the orchestrator as `type=expert` or `type=executor`.

Do NOT add a new skill when:

- It is just adding a model, dataset, component, application, or template; this should first be made into a resource of a resource skill.
- It is just documenting experience from a project; this should first be deposited as resource planning knowledge.
- It is just copying `coder/runtime/installer` under a different domain name.
- It is just splitting a phase of runtime's internal `discover/preflight/execute/diagnose` into a public skill.
- It is just turning an agent preference into a general rule.

## 5. How to Add an Executor Skill

Applies to capabilities with "fixed workflows that must be strictly executed step by step," such as dataset builders, evaluators, stable CLI wrappers, and job submission entry points.

### 5.1 Executor Frontmatter

```yaml
---
name: your-executor-skill
description: Briefly describe what tasks this executor skill handles, when to use it, and its I/O boundaries. Must state that it returns execution_result.
type: executor
---
```

### 5.2 Input Contract

Executor skills receive the current step handoff from the orchestrator; they do not re-plan the entire user goal:

```yaml
step_handoff:
  step_id: <step ID>
  execution_skill: <executor skill name>
  step_goal: <goal of this step>
  task_context:
    user_goal: <user's ultimate goal>
    constraints: <list of constraints>
    relevant_artifacts: <relevant artifacts>
  resource_bindings:
    - path: <resource path>
      type: <resource type>
      purpose: <purpose>
  inputs: <inputs required for execution>
  required_outputs: <required outputs>
  completion_criteria: <completion criteria>
```

### 5.3 Output Contract

Must return:

```yaml
execution_result:
  skill: <executor skill name>
  status: success | partial | failed | blocked
  artifacts:
    <artifact list>
  observation:
    summary: <execution summary>
    completed: <what was completed>
    missing: <missing items>
    risks: <risks>
    next_recommendation: <next step recommendation>
```

If execution requires model, data, component, or workflow knowledge, it must obtain resource content through `type=resource` skills; do not directly read any resource skill's `assets/`.

## 6. How to Add an Expert Skill

Applies to capabilities requiring "dynamic planning, resource trade-offs, and fallback," such as certain types of research workflow planning, evaluation scheme design, or complex data processing route selection.

### 6.1 Expert Frontmatter

```yaml
---
name: your-expert-skill
description: Briefly describe the planning scenarios this expert skill covers, when to use it, and what planner_proposal it outputs. Must state that it does not execute tasks.
type: expert
---
```

### 6.2 Input Contract

Expert skills receive the planning aspect assigned by the orchestrator:

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

### 6.3 Output Contract

General expert skills should return the standard `planner_proposal` of the current architecture:

```json
{
  "planner_id": "your-expert-skill",
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

Specific expert skills may add extension fields such as `planner_payload` without breaking the above fields. Expert skills only do planning; they do not write code, submit jobs, install environments, or bypass the orchestrator to schedule executor skills.

## 7. Evolution Path from Experience to Skill

It is recommended to solidify capabilities along the following path:

1. Implicit experience: temporary prompts, manual operations, one-off scripts.
2. Resource deposit: write into the corresponding `type=resource` skill's `assets/`.
3. Repeated validation: recalled multiple times in real tasks, collecting observations and failure conditions.
4. Skill solidification: only after the workflow is stable, boundaries are clear, and outputs are verifiable, judge whether to solidify as `type=executor` or `type=expert`.
5. Core-transparent extension: after registration, recalled or scheduled by the orchestrator without modifying the main control logic.

Solidification criteria:

- Just reusable knowledge, resource cards, model cards, data cards, component contracts → `type=resource`.
- Steps are stable, dependencies are strong, must strictly execute in order → `type=executor`.
- Requires planning, resource trade-offs, and fallback based on task characteristics → `type=expert`.

## 8. Recommended Submission Workflow

1. Clearly describe what problem the new capability solves.
2. Determine whether it should be a resource, executor, or expert skill per entry point A/B/C.
3. Prioritize minimal changes: if it can be a resource skill, do not add an executor / expert skill.
4. Complete the necessary files per contract:
   - resource: `SKILL.md`, resource files under `assets/`, necessary retrieval rules
   - executor: `SKILL.md`, necessary `references/`, `scripts/`, or `assets/`
   - expert: `SKILL.md`, necessary planning protocols or reference documents
5. Check for overlapping responsibilities with existing skills.
6. Add verifiable examples, failure conditions, or usage limitations.
7. Submit a PR with the entry point, skill type, and verification method in the description.

## 9. PR Self-Check Checklist

- Have you avoided modifying the orchestrator's domain hardcoded rules?
- Are new resources placed under the corresponding `type=resource` skill's `assets/`, rather than directly into `skills/onescience-primitives/assets/`?
- Does the resource skill accept `resource_retrieval_request` and return `resource_retrieval_result`?
- Does the resource skill explicitly prohibit callers from directly reading its `assets/`?
- If adding a resource, is `metadata.json`'s `description` sufficient to support recall?
- If adding an executor, does it accept `step_handoff` and return the standard `execution_result`?
- If adding an expert, does it accept planner input and return the standard `planner_proposal`?
- Have you clearly documented inapplicable scenarios, constraints, and fallback?

## 10. One-Sentence Principle

Resources are accessed through `type=resource` skills, execution is delivered through `type=executor` skills, and complex decisions are planned by `type=expert` skills; all three follow unified contracts, and are uniformly recalled, fused, and scheduled by the orchestrator.
