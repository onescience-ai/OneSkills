# Primitive Code Migration Batch

Date: 2026-09-04

This batch continues the selective integration of `scientific-agent-skills` into OneScience primitives. It adds a second wave of cross-domain source skills and keeps execution promotion separate from knowledge distillation.

## Migrated primitives

The following primitives were materialized with source-traceable `references/` files and four-part primitive bundles:

- `bio.tools.pyopenms`
- `bio.tools.geniml`
- `bio.tools.cobrapy`
- `bio.datapipes.tiledbvcf`
- `general.tools.pydicom`
- `general.tools.pymoo`
- `general.tools.qutip`
- `general.tools.scikit_survival`
- `general.tools.lab_hardware_cad`
- `general.tools.torchdrug`
- `general.tools.torch_geometric`

Most of these remain resource-only. `knowledge_assets` were copied and hashed from the source skill references when available, and each primitive now exposes a source version, file counts, and read-only reference inventory in `metadata.json`.

## Notes by group

- Bioinformatics: proteomics, genomic language models, constraint-based metabolism, and VCF data access.
- General scientific computing: DICOM inspection, optimization, quantum dynamics, survival analysis, lab CAD, molecular graph learning, and graph neural networks.
- The `tiledbvcf` source skill did not provide reference files in this repository snapshot, so it was materialized with an empty knowledge asset list rather than inventing documentation.

## Current coverage snapshot

After this batch, the migration inventory reports:

- `explicit_provenance_matches`: 48
- `heuristic_matches`: 2
- `uncovered_source_skills`: 113

The inventory file for this batch is `docs/open-source/skill_migration_inventory_2026-09-04.json`.

## Next batch rule

Keep preserving the same separation:

1. Source knowledge becomes read-only primitive references.
2. Execution assets only enter when their boundary, hashes, and I/O contract are explicit.
3. Higher-risk scripts stay in the migration queue until they can be wrapped or decomposed.
