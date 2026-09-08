# Primitive Code Migration Batch - 2026-09-07c

## Batch Summary

This batch materialized 4 additional source skills into OneScience primitives:

| Source skill | Primitive | Domain / category | Knowledge assets |
| --- | --- | --- | ---: |
| `pkpd-modeling` | `general.application.pkpd_modeling` | `general/application` | 14 |
| `iso-standards-readiness` | `general.application.iso_standards_readiness` | `general/application` | 9 |
| `hypothesis-generation` | `general.workflow-planning.hypothesis_generation` | `general/workflow-planning` | 10 |
| `peer-review` | `general.workflow-planning.peer_review` | `general/workflow-planning` | 6 |

All four primitives now carry the four core files plus `references/`, and their `knowledge_assets` entries match the copied reference count.

## Current Inventory Snapshot

- Source skills with `SKILL.md`: 163
- Target primitive metadata files: 286
- Explicit provenance matches: 62
- Heuristic matches: 2
- Uncovered source skills: 99

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
