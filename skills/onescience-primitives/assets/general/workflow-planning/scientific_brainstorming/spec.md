# architecture_overview

Scientific brainstorming primitive for evidence-aware ideation, independent generation, structured discussion, explicit assumptions, adversarial review, and decision logs.

This primitive is distilled from the source Agent Skill `scientific-brainstorming`. It is a planning and retrieval primitive. Preserved source payloads, if present, are inert copies for review and later binding; they are not executable runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Core guidance works in any Agent Skills-compatible host. Optional bundled CLIs require Python 3.11+ and use only the standard library; they make no network or LLM calls and require no credentials.

# source_knowledge_outline

- Scientific Brainstorming
- Purpose and boundaries
- Operating rules
- Reproducible workflow
- 1. Scope the session
- 2. Diversify perspectives deliberately
- 3. Generate independently
- 4. Share without immediate evaluation
- 5. Cluster structurally
- 6. Define transparent criteria

# knowledge_assets

- `references/brainstorming_methods.md`: Brainstorming Methods
- `references/facilitation_workflows.md`: Facilitation Workflows
- `references/idea_evaluation.md`: Idea Evaluation
- `references/responsible_ai.md`: Responsible Ai
- `references/sources.md`: Sources

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# source_payloads

- `source_payload/scripts/_common.py` (source_script):  Common
- `source_payload/scripts/evaluate_matrix.py` (source_script): Evaluate Matrix
- `source_payload/scripts/session_scaffold.py` (source_script): Session Scaffold
- `source_payload/scripts/validate_register.py` (source_script): Validate Register

Source payloads are indexed in `metadata.json.source_payloads` with SHA-256 values. They preserve source scripts, templates, and static files for later migration review, but they do not grant execution permission.

# execution_policy

No source scripts were promoted as execution assets in this batch. Source-side file counts were: references=5, scripts=4, assets=0. Preserved source payloads remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/scientific-brainstorming`.
