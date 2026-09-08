# architecture_overview

Hypothesis-generation primitive for evidence-bounded scientific questions, rival explanations, causal or associational claims, discriminating predictions, measurements, and preregistration-ready analysis plans.

This primitive is distilled from the source Agent Skill `hypothesis-generation`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Python 3.11+ standard library. Bundled CLIs are deterministic and local-only; they accept bounded JSON, CSV, or Markdown and require no network, credentials, models, image services, or external packages.

# source_knowledge_outline

- Scientific Hypothesis Generation
- Non-negotiable boundaries
- Keep the objects distinct
- Workflow
- 1. Run the scope and safety gate
- 2. Freeze the observation
- 3. Frame the research question
- 4. Establish a dated evidence boundary
- 5. Generate rivals before choosing tests
- 6. Declare the claim type and estimand

# knowledge_assets

- `references/causal_inference_and_claims.md`: Causal Inference And Claims
- `references/concepts_and_workflow.md`: Concepts And Workflow
- `references/ethics_safety_and_ai.md`: Ethics Safety And Ai
- `references/experimental_design_patterns.md`: Experimental Design Patterns
- `references/hypothesis_quality_criteria.md`: Hypothesis Quality Criteria
- `references/literature_search_strategies.md`: Literature Search Strategies
- `references/preregistration_and_open_science.md`: Preregistration And Open Science
- `references/security_validation.md`: Security Validation
- `references/source_ledger.md`: Source Ledger
- `references/tool_reference.md`: Tool Reference

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=10, scripts=8, assets=8. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/hypothesis-generation`.
