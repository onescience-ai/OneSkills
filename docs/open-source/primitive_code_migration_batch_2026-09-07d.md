# Primitive Code Migration Batch - 2026-09-07d

## Batch Summary

This batch materialized 4 additional source skills into OneScience primitives:

| Source skill | Primitive | Domain / category | Knowledge assets |
| --- | --- | --- | ---: |
| `exploratory-data-analysis` | `general.workflow-planning.exploratory_data_analysis` | `general/workflow-planning` | 6 |
| `pathml` | `bio.tools.pathml` | `bio/tools` | 6 |
| `pptx-posters` | `general.output-format.pptx_posters` | `general/output-format` | 7 |
| `scientific-slides` | `general.output-format.scientific_slides` | `general/output-format` | 11 |

All four primitives now carry the four core files plus copied `references/`. Source scripts and bundled assets remain provenance-tracked in metadata, but they are not promoted into executable primitive assets by this conservative materialization pass.

## Current Inventory Snapshot

- Source skills with `SKILL.md`: 163
- Target primitive metadata files: 283
- Explicit provenance matches: 66
- Heuristic matches: 2
- Uncovered source skills: 95

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
- The selected skills continue the high-priority coverage path across general EDA, bioimaging, and scientific presentation outputs.