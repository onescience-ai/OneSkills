# architecture_overview

Stable-Baselines3 primitive for standard reinforcement-learning algorithms, Gymnasium environments, and reproducible single-agent training workflows.

This primitive is distilled from the source Agent Skill `stable-baselines3`. It is a planning and retrieval primitive. Preserved source payloads, if present, are inert copies for review and later binding; they are not executable runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.10+, PyTorch >= 2.3, and stable-baselines3 2.8+. Gymnasium environments; optional extras for TensorBoard and Atari (ale-py).

# source_knowledge_outline

- Stable Baselines3
- Overview
- Installation
- Basic installation
- With extra dependencies (TensorBoard, ale-py for Atari, etc.)
- Related Projects
- Core Capabilities
- 1. Training RL Agents
- Create environment
- Initialize agent (device="cpu" is often faster for MlpPolicy on small envs)

# knowledge_assets

- `references/algorithms.md`: Algorithms
- `references/callbacks.md`: Callbacks
- `references/custom_environments.md`: Custom Environments
- `references/vectorized_envs.md`: Vectorized Envs

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# source_payloads

- `source_payload/scripts/custom_env_template.py` (source_script): Custom Env Template
- `source_payload/scripts/evaluate_agent.py` (source_script): Evaluate Agent
- `source_payload/scripts/train_rl_agent.py` (source_script): Train Rl Agent

Source payloads are indexed in `metadata.json.source_payloads` with SHA-256 values. They preserve source scripts, templates, and static files for later migration review, but they do not grant execution permission.

# execution_policy

No source scripts were promoted as execution assets in this batch. Source-side file counts were: references=4, scripts=3, assets=0. Preserved source payloads remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/stable-baselines3`.
