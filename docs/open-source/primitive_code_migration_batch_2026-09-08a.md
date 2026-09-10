# Primitive Code Migration Batch - 2026-09-08a

## Batch Summary

This batch materialized 4 additional source skills into OneScience primitives:

| Source skill | Primitive | Domain / category | Knowledge assets |
| --- | --- | --- | ---: |
| `neuropixels-analysis` | `bio.workflow-planning.neuropixels_analysis` | `bio/workflow-planning` | 10 |
| `analytical-method-validation` | `general.workflow-planning.analytical_method_validation` | `general/workflow-planning` | 6 |
| `gget` | `bio.tools.gget` | `bio/tools` | 5 |
| `pytorch-lightning` | `general.tools.pytorch_lightning` | `general/tools` | 7 |

All four primitives now carry the four core files plus copied `references/`. Source scripts and bundled assets remain provenance-tracked in metadata, but they are not promoted into executable primitive assets by this conservative materialization pass.

## Current Inventory Snapshot

- Source skills with `SKILL.md`: 163
- Target primitive metadata files: 287
- Explicit provenance matches: 70
- Heuristic matches: 2
- Uncovered source skills: 91

## Code Migration Distribution

- `resource_only`: 85
- `resource_with_execution_assets`: 58
- `propose_executor`: 20

## Shape Distribution

- `single_primitive`: 93
- `split_primitives`: 52
- `primitive_plus_executor`: 18

## Notes

- This batch used the reusable batch driver and JSON plan file.
- The inventory snapshot was refreshed after materialization, so the counts above reflect the new primitives.
- The selected skills extend coverage across bioinformatics analysis, assay validation, database querying, and scientific deep learning.