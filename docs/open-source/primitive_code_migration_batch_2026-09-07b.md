# Primitive Code Migration Batch - 2026-09-07b

## Batch Summary

This batch materialized 5 additional source skills into OneScience primitives:

| Source skill | Primitive | Domain / category | Knowledge assets |
| --- | --- | --- | ---: |
| `clinical-reports` | `general.application.clinical_reports` | `general/application` | 11 |
| `clinical-decision-support` | `general.application.clinical_decision_support` | `general/application` | 12 |
| `treatment-plans` | `general.application.treatment_plans` | `general/application` | 8 |
| `matlab` | `general.tools.matlab` | `general/tools` | 8 |
| `simpy` | `general.tools.simpy` | `general/tools` | 8 |

All five primitives now carry the four core files plus `references/`, and their `knowledge_assets` entries match the copied reference count.

## Current Inventory Snapshot

- Source skills with `SKILL.md`: 163
- Target primitive metadata files: 282
- Explicit provenance matches: 58
- Heuristic matches: 2
- Uncovered source skills: 103

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
