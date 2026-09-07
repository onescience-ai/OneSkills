# architecture_overview

scikit-learn primitive for supervised learning, clustering, dimensionality reduction, preprocessing, model evaluation, hyperparameter tuning, and pipeline construction.

This primitive is distilled from the source Agent Skill `scikit-learn`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.11+ and scikit-learn 1.7+. NumPy and SciPy are required dependencies. Optional matplotlib/seaborn for bundled example scripts that save plots.

# source_knowledge_outline

- Scikit-learn
- Overview
- Installation
- Install scikit-learn using uv
- Optional: plotting utilities and bundled script dependencies
- Commonly used with
- When to Use This Skill
- Quick Start
- Classification Example
- Split data

# knowledge_assets

- `references/common_workflows.md`: Common Workflows
- `references/core_capabilities.md`: Core Capabilities
- `references/model_evaluation.md`: Model Evaluation
- `references/pipelines_and_composition.md`: Pipelines And Composition
- `references/preprocessing.md`: Preprocessing
- `references/quick_reference.md`: Quick Reference
- `references/supervised_learning.md`: Supervised Learning
- `references/unsupervised_learning.md`: Unsupervised Learning

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=8, scripts=2, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/scikit-learn`.
