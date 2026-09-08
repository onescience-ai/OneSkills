# architecture_overview

PK/PD modeling primitive for non-compartmental analysis, compartmental and population PK, exposure-response, bioequivalence, allometric scaling, DDI screening, and therapeutic drug monitoring planning.

This primitive is distilled from the source Agent Skill `pkpd-modeling`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.11+ with numpy and scipy. No network access and no proprietary software. The estimation tools this skill orients you towards (NONMEM, Monolix, Phoenix, Simcyp, GastroPlus) are licensed separately and are never invoked by these scripts.

# source_knowledge_outline

- Pharmacokinetic and Pharmacodynamic Modelling
- When to use
- The three rules
- Scope
- Scripts
- Workflow
- 1. Non-compartmental analysis
- 2. Compartmental fitting and model selection
- 3. Population PK
- 4. Simulation and regimen selection

# knowledge_assets

- `references/antimicrobial-and-tdm.md`: Antimicrobial And Tdm
- `references/bioequivalence.md`: Bioequivalence
- `references/dataset-standards.md`: Dataset Standards
- `references/ddi-and-qt.md`: Ddi And Qt
- `references/nca-conventions.md`: Nca Conventions
- `references/pbpk.md`: Pbpk
- `references/pd-and-exposure-response.md`: Pd And Exposure Response
- `references/population-pk.md`: Population Pk
- `references/regulatory-guidance.md`: Regulatory Guidance
- `references/software-ecosystem.md`: Software Ecosystem
- `references/source-ledger.md`: Source Ledger
- `references/special-populations.md`: Special Populations
- `references/structural-models.md`: Structural Models
- `references/tmdd-and-biologics.md`: Tmdd And Biologics

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=14, scripts=11, assets=2. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/pkpd-modeling`.
