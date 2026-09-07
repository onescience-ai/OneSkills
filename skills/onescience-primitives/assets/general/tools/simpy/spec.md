# architecture_overview

SimPy primitive for process-based discrete-event simulation models, resource contention, interrupts, monitoring, replications, and output-analysis workflows.

This primitive is distilled from the source Agent Skill `simpy`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Upstream SimPy 4.1.2 supports Python 3.8+; bundled CLIs require Python 3.10+, uv, and SimPy 4.1.2. They use only SimPy and the standard library, operate on local bounded inputs, and make no network calls.

# source_knowledge_outline

- SimPy
- Scope
- Current release and installation
- Model workflow
- Minimal bounded model
- Core semantics
- Environment and deterministic ordering
- Event, Timeout, Process, and Condition
- Interrupts
- Shared resources

# knowledge_assets

- `references/cli-guide.md`: Cli Guide
- `references/events.md`: Events
- `references/monitoring.md`: Monitoring
- `references/process-interaction.md`: Process Interaction
- `references/real-time.md`: Real Time
- `references/resources.md`: Resources
- `references/simulation-methodology.md`: Simulation Methodology
- `references/sources.md`: Sources

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=8, scripts=7, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/simpy`.
