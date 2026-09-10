# Primitive Code Migration Batch - 2026-09-08b

## Batch Summary

This batch materialized 4 additional source skills into OneScience primitives:

| Source skill | Primitive | Domain / category | Knowledge assets |
| --- | --- | --- | ---: |
| `scholar-evaluation` | `general.workflow-planning.scholar_evaluation` | `general/workflow-planning` | 5 |
| `uncertainty-and-units` | `general.tools.uncertainty_and_units` | `general/tools` | 6 |
| `venue-templates` | `general.output-format.venue_templates` | `general/output-format` | 11 |
| `latex-posters` | `general.output-format.latex_posters` | `general/output-format` | 9 |

All four primitives now carry the four core files plus copied `references/`. Source scripts and bundled assets remain provenance-tracked in metadata, but they are not promoted into executable primitive assets by this conservative materialization pass.

## Current Inventory Snapshot

- Source skills with `SKILL.md`: 163
- Target primitive metadata files: 291
- Explicit provenance matches: 74
- Heuristic matches: 2
- Uncovered source skills: 87

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
- The selected skills extend coverage across scholarly evaluation, numerical sanity checks, venue-specific templates, and LaTeX poster production.