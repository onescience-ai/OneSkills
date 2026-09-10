# architecture_overview

PyTorch Lightning primitive for organizing training code into LightningModules, configuring Trainers, data modules, callbacks, logging, and distributed training for scalable scientific deep learning.

This primitive is distilled from the source Agent Skill `pytorch-lightning`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.10+ and lightning 2.6+ (or pytorch-lightning 2.6+). GPU training needs CUDA-capable PyTorch. Optional loggers (wandb, mlflow, comet-ml) and DeepSpeed require separate installs.

# source_knowledge_outline

- PyTorch Lightning
- Overview
- Installation
- When to Use This Skill
- Core Capabilities
- 1. LightningModule - Model Definition
- 2. Trainer - Training Automation
- 3. LightningDataModule - Data Pipeline Organization
- 4. Callbacks - Extensible Training Logic
- 5. Logging - Experiment Tracking

# knowledge_assets

- `references/best_practices.md`: Best Practices
- `references/callbacks.md`: Callbacks
- `references/data_module.md`: Data Module
- `references/distributed_training.md`: Distributed Training
- `references/lightning_module.md`: Lightning Module
- `references/logging.md`: Logging
- `references/trainer.md`: Trainer

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=7, scripts=3, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/pytorch-lightning`.
