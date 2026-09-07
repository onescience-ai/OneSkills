# architecture_overview

NeuroKit2 primitive for physiological time-series preprocessing, event and interval analysis, multimodal alignment, variability analysis, and complexity workflows.

This primitive is distilled from the source Agent Skill `neurokit2`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Python 3.10+ and uv; pinned workflows use NeuroKit2 0.2.13. Core processing needs NumPy, SciPy, pandas, scikit-learn, matplotlib, PyWavelets, requests, and setuptools; selected EEG, cvxEDA, plotting, file-format, and RQA features need separately locked optional packages.

# source_knowledge_outline

- NeuroKit2
- Scope and evidence cutoff
- Boundary
- Reproducible installation
- Required data contract
- Core workflow
- 1. Inspect before transforming
- 2. Preserve preprocessing order
- 3. Treat schemas as runtime observations
- Current patterns

# knowledge_assets

- `references/bio_module.md`: Bio Module
- `references/complexity.md`: Complexity
- `references/ecg_cardiac.md`: Ecg Cardiac
- `references/eda.md`: Eda
- `references/eeg.md`: Eeg
- `references/emg.md`: Emg
- `references/eog.md`: Eog
- `references/epochs_events.md`: Epochs Events
- `references/hrv.md`: Hrv
- `references/ppg.md`: Ppg
- `references/rsp.md`: Rsp
- `references/signal_processing.md`: Signal Processing

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=12, scripts=7, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/neurokit2`.
